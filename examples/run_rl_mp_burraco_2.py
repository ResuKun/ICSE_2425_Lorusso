# parallel_run_rl_cpu_workers.py
import argparse
import os
import multiprocessing as mp
from datetime import datetime
from Utils.logger import ProcessLogger 
import time
import torch
import rlcard
import queue as _pyqueue
from rlcard.utils import Logger, set_seed, get_device, reorganize, plot_curve, tournament
from rlcard.agents import RandomAgent
from Utils.checkpoint_file_handler import save_and_send_ckpt_to_worker
from Utils.logger import ProcessLogger

# =========================
# Worker CPU: SOLO simulazione
# =========================
def worker_process(worker_id, traj_queue, param_queue, args, seed_offset=0):
    try:
        worker_log = ProcessLogger.get_logger(role=f"worker_{worker_id}")
        seed = args.seed + seed_offset + worker_id
        set_seed(seed)

        device = torch.device("cpu")
        env = rlcard.make(args.env, config={'seed': seed})

        # Riceve primo checkpoint (bloccante UNA SOLA VOLTA)
        ckpt_msg = param_queue.get()
        # Se è stringa -> carica da file, altrimenti lo usa direttamente
        if isinstance(ckpt_msg, str):
            ckpt = torch.load(ckpt_msg, map_location='cpu', weights_only=False)
        else:
            ckpt = ckpt_msg

        local_agent = get_agent(env, device, args, worker_log)

        opponents = [
            RandomAgent(num_actions=env.num_actions)
            for _ in range(env.num_players - 1)
        ]
        env.set_agents([local_agent] + opponents)

        for ep in range(args.num_ep_worker):
            worker_log.info(f"Worker {worker_id} - Episode [{ep}] START")
            trajs, pays = env.run(is_training=True)
            traj_queue.put((trajs, pays))
            worker_log.info(f"Worker {worker_id} - Episode [{ep}] END")

            # polling non bloccante: aggiorna SOLO i pesi
            try:
                latest = None
                while True:
                    latest = param_queue.get_nowait()
            except _pyqueue.Empty:
                pass

            if latest is not None:
                if isinstance(latest, str):
                    latest = torch.load(latest, map_location='cpu', weights_only=False)
                local_agent.load_state_dict(latest['model_state_dict'])

        traj_queue.put(("__WORKER_DONE__", worker_id))

    except Exception:
        import traceback, sys
        tb = traceback.format_exc()
        worker_log.error(f"[W{worker_id}] UNCAUGHT EXCEPTION:\n{tb}", file=sys.stderr, flush=True)
        sys.exit(1)


# =========================
# Learner GPU: SOLO training
# =========================
def learner_process(traj_queue, param_queues, args):
    device = get_device()
    set_seed(args.seed)
    learner_log = ProcessLogger.get_logger(role="learner")

    env = rlcard.make(args.env, config={'seed': args.seed})
    agent = get_agent(env, device, args, learner_log)

    opponents = [
        RandomAgent(num_actions=env.num_actions)
        for _ in range(env.num_players - 1)
    ]
    env.set_agents([agent] + opponents)

    # invio checkpoint iniziale ai worker
    ###### ORIGINALE ######
    #ckpt = agent.checkpoint_attributes()
    #for q in param_queues:
    #    q.put(ckpt)
    ##### DAL VECCHIO SCRIPT
    # invio primo checkpoint a ogni worker
    for wid, q in enumerate(param_queues):
        save_and_send_ckpt_to_worker(agent, wid, q, step=0, args=args)

    finished_workers = 0
    episode_count = 0

    with Logger(args.log_dir) as logger:
        while finished_workers < args.num_workers:
            item = traj_queue.get()

            # --- worker finito ---
            if isinstance(item, tuple) and item[0] == "__WORKER_DONE__":
                finished_workers += 1
                continue

            # --- traiettoria ---
            trajs, pays = item
            episode_count += 1

            # --- training ---
            learner_log.info(f"START TRAINING")
            reorganized = reorganize(trajs, pays)
            for ts in reorganized[0]:
                agent.feed(ts)  # QUI avviene il training su GPU
            learner_log.info(f"END TRAINING")

            # valutazione periodica (bloccante)
            if episode_count % args.eval_every == 0:
                learner_log.info(f"START tournament - episode_count:{episode_count}")
                result = tournament(env, args.num_eval_games)[0]
                logger.log_performance(
                    episode_count * args.train_every, result
                )
                learner_log.info("END tournament")

                # invio checkpoint aggiornato
                #ckpt = agent.checkpoint_attributes()
                step = episode_count * args.train_every
                for wid, q in enumerate(param_queues):
                    if not q.full():
                        save_and_send_ckpt_to_worker(agent, wid, q, step, args)

        # Get the paths
        csv_path, fig_path = logger.csv_path, logger.fig_path
    
    # Plot the learning curve
    learner_log.info("Saving Statistics")
    plot_curve(csv_path, fig_path, args.algorithm)

    torch.save(agent, os.path.join(args.log_dir, "final_model.pth"))


# =========================
# Main: orchestration
# =========================
def main(args):

    mp.set_start_method("spawn", force=True)

    # --- creo code ---
    traj_queue = mp.Queue(maxsize=100)
    param_queues = [mp.Queue(maxsize=1) for _ in range(args.num_workers)]

    main_log = ProcessLogger.get_logger(role="main")
    main_log.info(f" num_workers            : {args.num_workers}")
    main_log.info(f" num_ep_worker          : {args.num_ep_worker}")
    main_log.info(f" num_eval_games         : {args.num_eval_games}")
    main_log.info(f" load_checkpoint_path   : {args.load_checkpoint_path}")

    learner = mp.Process(
        target=learner_process,
        args=(traj_queue, param_queues, args)
    )
    learner.start()

    workers = []
    for wid in range(args.num_workers):
        p = mp.Process(
            target=worker_process,
            args=(wid, traj_queue, param_queues[wid], args)
        )
        p.start()
        workers.append(p)
        time.sleep(0.3)

    for p in workers:
        p.join()
    learner.join()


# =========================
# Agent factory
# =========================
def get_agent(env, device, args, logger):
    if args.algorithm == 'dqn':
        from rlcard.agents import DQNAgent
        if args.load_checkpoint_path != "":
            logger.info(f"Loading from: {args.load_checkpoint_path}")
            ckpt = torch.load(args.load_checkpoint_path,weights_only=False)
            agent = DQNAgent.from_checkpoint(checkpoint=ckpt)
            agent.device = device
            return agent
        
        return DQNAgent(
            replay_memory_size=200000,
            #replay_memory_init_size=10000,
            #per test
            replay_memory_init_size=1000,
            update_target_estimator_every=2500,
            discount_factor=0.99,
            epsilon_start=1.0,
            epsilon_end=0.1,
            #epsilon_decay_steps=400000,
            epsilon_decay_steps=200000,
            batch_size=256,
            num_actions=env.num_actions,
            state_shape=env.state_shape[0],
            #mlp_layers=[128, 128],
            mlp_layers=[512, 512, 256],
            learning_rate=0.0003,
            device=device,
            save_path=args.log_dir,
            save_every=args.save_every,
            train_every=args.train_every
        )


# =========================
# Entry point
# =========================
if __name__ == "__main__":
    path = f"experiments/burraco_dqn_result/{datetime.now().strftime('%Y_%m_%d_%H%M%S')}"
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default="burraco")
    parser.add_argument("--algorithm", default="dqn")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--log_dir", default=path)
    parser.add_argument("--save_every", type=int, default=-1)
    parser.add_argument("--num_workers", type=int, default=10)
    parser.add_argument("--num_ep_worker", type=int, default=2)
    parser.add_argument("--train_every", type=int, default=5000)
    parser.add_argument("--eval_every", type=int, default=10)
    parser.add_argument("--num_eval_games", type=int, default=1)
    #parser.add_argument("--load_checkpoint_path", default="Checkpoint/checkpoint_dqn.pt")
    parser.add_argument("--load_checkpoint_path", default="")

    args = parser.parse_args()
    main(args)
