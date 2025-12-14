# parallel_run_rl_cpu_workers.py
import argparse
import os
import multiprocessing as mp
from datetime import datetime
from Utils.logger import SingletonLogger 
import time
import torch
import rlcard
import queue as _pyqueue
from rlcard.utils import Logger, set_seed, get_device, reorganize, plot_curve, tournament
from rlcard.agents import RandomAgent
from Utils.checkpoint_file_handler import save_and_send_ckpt_to_worker

def worker_process(worker_id, traj_queue, param_queue, args, seed_offset=0):
    try:
        seed = args.seed + seed_offset + worker_id
        set_seed(seed)

        device = torch.device("cpu")
        env = rlcard.make(args.env, config={'seed': seed})

        # Riceve primo checkpoint (bloccante una volta sola)
        ckpt_msg = param_queue.get()  # può essere dict oppure percorso file (str)

        # Se è stringa -> carica da file, altrimenti lo usa direttamente
        if isinstance(ckpt_msg, str):
            ckpt = torch.load(ckpt_msg, map_location='cpu', weights_only=False)
        else:
            ckpt = ckpt_msg

        local_agent = get_agent(env, device, args, ckpt)

        opponents = [
            RandomAgent(num_actions=env.num_actions)
            for _ in range(env.num_players - 1)
        ]
        agents = [local_agent] + opponents
        env.set_agents(agents)

        for ep in range(args.num_ep_worker):
            trajs, pays = env.run(is_training=True)
            traj_queue.put((trajs, pays))

            # polling: svuota param_queue (se ci sono messaggi, tieni solo l'ultimo)
            try:
                latest = None
                while True:
                    msg = param_queue.get_nowait()
                    latest = msg
            except _pyqueue.Empty:
                latest = latest  # nulla di nuovo

            if latest is not None:
                # applica l'ultimo messaggio arrivato
                if isinstance(latest, str):
                    new_ckpt = torch.load(latest, map_location='cpu', weights_only=False)
                else:
                    new_ckpt = latest
                # ricrea agente o aggiorna i pesi a seconda della API
                agents[0] = get_agent(env, device, args, new_ckpt)
                env.set_agents(agents)

        traj_queue.put(("__WORKER_DONE__", worker_id))

    except Exception:
        import traceback, sys
        tb = traceback.format_exc()
        # Print immediately so you see it in console
        print(f"[W{worker_id}] UNCAUGHT EXCEPTION:\n{tb}", file=sys.stderr, flush=True)
        # Also save to file for inspection
        try:
            os.makedirs(args.log_dir, exist_ok=True)
            with open(os.path.join(args.log_dir, f"worker_{worker_id}_exc.txt"), "w", encoding="utf-8") as f:
                f.write(tb)
        except Exception as e_file:
            print(f"[W{worker_id}] Failed to write exc file: {e_file}", file=sys.stderr, flush=True)
            print(tb, file=sys.stderr, flush=True)
        # Ensure non-zero exit
        sys.exit(1)



def main(args):

    mp.set_start_method("spawn", force=True)

    # --- creo code ---
    param_queues = [mp.Queue(maxsize=1) for _ in range(args.num_workers)]
    traj_queue = mp.Queue()

    main_log = SingletonLogger().get_logger()

    main_log.info(f" num_workers            : {args.num_workers}")
    main_log.info(f" num_ep_worker          : {args.num_ep_worker}")
    main_log.info(f" num_eval_games         : {args.num_eval_games}")
    main_log.info(f" train_every            : {args.train_every}")
    main_log.info(f" load_checkpoint_path   : {args.load_checkpoint_path}")

    # --- setup agente centrale (GPU) ---
    device = get_device()
    set_seed(args.seed)

    env_main = rlcard.make(args.env, config={'seed': args.seed})
    central_agent = get_agent(env_main, device, args)

    opponents = [
        RandomAgent(num_actions=env_main.num_actions)
        for _ in range(env_main.num_players - 1)
    ]
    env_main.set_agents([central_agent] + opponents)

   ## --- avvio worker ---
    processes = []
    for wid in range(args.num_workers):
        p = mp.Process(
            target=worker_process,
            args=(wid, traj_queue, param_queues[wid], args)
        )
        p.start()
        processes.append(p)
        time.sleep(0.5)


    # invio primo checkpoint a ogni worker
    for wid, q in enumerate(param_queues):
        save_and_send_ckpt_to_worker(central_agent, wid, q, step=0, args=args)

    # --- ciclo principale ---
    finished_workers = 0
    buffer_count = 0
    episode_count = 0

    worker_done = [False] * args.num_workers

    with Logger(args.log_dir) as logger:

        while finished_workers < args.num_workers:
            try:
                item = traj_queue.get(timeout=10)
            except:
                main_log.warning("[Main] timeout waiting for traj_queue; checking workers...")
                for i, p in enumerate(processes):
                     main_log.warning(f"[Main] worker {i} pid={p.pid} is_alive={p.is_alive()} exitcode={p.exitcode}")
                continue

            # --- worker finito ---
            if isinstance(item, tuple) and item[0] == "__WORKER_DONE__":
                wid = item[1]
                worker_done[wid] = True
                finished_workers += 1
                continue

            # --- traiettoria ---
            trajs, pays = item
            episode_count += 1

            reorganized = reorganize(trajs, pays)
            for ts in reorganized[0]:
                central_agent.feed(ts)
                buffer_count += 1

            # --- train ---
            if buffer_count >= args.train_every:
                if len(central_agent.memory.memory) >= central_agent.batch_size:
                    main_log.info(f"TRAIN: buffer_count={buffer_count}, memory={len(central_agent.memory.memory)}")
                    central_agent.train()
                else:
                    main_log.info(f"SKIP TRAIN: memory too small ({len(central_agent.memory.memory)}/{central_agent.batch_size})")

                buffer_count = 0

            # --- valutazione periodica ---
            if episode_count % args.eval_every == 0:
                main_log.info(f"START tournament - episode_count:{episode_count}")
                main_log.info(f"param_queue size before tournament: {[par.qsize() for par in param_queues]}")
                result = tournament(env_main, args.num_eval_games)[0]
                logger.log_performance(
                    episode_count * args.train_every, result
                )
                main_log.info("END tournament")

                # --- invio checkpoint aggiornato ---
                if finished_workers < args.num_workers:
                    ckpt = central_agent.checkpoint_attributes()
                    step = episode_count * args.train_every
                    for wid, q in enumerate(param_queues):
                        if not worker_done[wid] and processes[wid].is_alive():
                            save_and_send_ckpt_to_worker(central_agent, wid, q, step=step, args=args)
        
        # Get the paths
        csv_path, fig_path = logger.csv_path, logger.fig_path

    # Plot the learning curve
    main_log.info("Saving Statistics")
    plot_curve(csv_path, fig_path, args.algorithm)

    # --- chiusura ---
    for p in processes:
        p.join()

    for q in param_queues:
        q.close()
        q.join_thread()
    traj_queue.close()
    traj_queue.join_thread()

    # --- salvataggio finale ---
    os.makedirs(args.log_dir, exist_ok=True)
    torch.save(central_agent, os.path.join(args.log_dir, "final_model.pth"))


def get_agent(env, device, args, checkpoint_arg = None):
    # Initialize the agent and use random agents as opponents
    agent = None
    if args.algorithm == 'dqn':
        from rlcard.agents import DQNAgent
        if checkpoint_arg != None:
            agent = DQNAgent.from_checkpoint(checkpoint=checkpoint_arg)
        elif args.load_checkpoint_path != "":
            print(f"Loading from: {args.load_checkpoint_path}")
            ckpt = torch.load(args.load_checkpoint_path,weights_only=False)
            agent = DQNAgent.from_checkpoint(checkpoint=ckpt)

        else:
            agent = DQNAgent(
                    replay_memory_size=200000,
                    replay_memory_init_size=10000,
                    update_target_estimator_every=2500,
                    discount_factor=0.99,
                    epsilon_start=1.0,
                    epsilon_end=0.1,
                    epsilon_decay_steps=400000,
                    batch_size=256,
                    num_actions=env.num_actions,        # da ambiente Burraco
                    state_shape=env.state_shape[0],     # da env.state_shape[0]
                    mlp_layers=[128, 128],              # da valutare mlp_layers=[512, 512, 256],
                    learning_rate=0.00005,
                    device=device,
                    save_path=args.log_dir,
                    save_every=args.save_every,
                    train_every = 100
                )

            #agent = DQNAgent(
            #    num_actions=env.num_actions,
            #    state_shape=env.state_shape[0],
            #    #salire a [1024, 512, 256] con TANTI esempi
            #    mlp_layers=[512, 512, 256],
            #    device=device,
            #    save_path=args.log_dir,
            #    save_every=args.save_every
            #)

    elif args.algorithm == 'nfsp':
        from rlcard.agents import NFSPAgent
        if checkpoint_arg != None:
            agent = NFSPAgent.from_checkpoint(checkpoint=checkpoint_arg)
        else:
            agent = NFSPAgent(
                num_actions=env.num_actions,
                state_shape=env.state_shape[0],
                hidden_layers_sizes=[64,64],
                q_mlp_layers=[64,64],
                device=device,
                save_path=args.log_dir,
                save_every=args.save_every
            )
    return agent

if __name__ == "__main__":
    path = f"experiments/burraco_dqn_result/{datetime.now().strftime('%Y_%m_%d_%H%M%S')}"
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default="burraco")
    parser.add_argument("--algorithm", default="dqn", choices=["dqn", "nfsp"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--log_dir", default=path)
    parser.add_argument("--save_every", type=int, default=-1)
    #parser.add_argument("--load_checkpoint_path", default="Checkpoint/checkpoint_dqn.pt")
    parser.add_argument("--load_checkpoint_path", default="")

    #default 32
    parser.add_argument("--train_every", type=int, default=100)
    parser.add_argument("--num_workers", type=int, default=5)
    parser.add_argument("--num_ep_worker", type=int, default=10000)
    parser.add_argument("--num_eval_games", type=int, default=10)
    parser.add_argument("--eval_every", type=int, default=100)

    args = parser.parse_args()
    main(args)


