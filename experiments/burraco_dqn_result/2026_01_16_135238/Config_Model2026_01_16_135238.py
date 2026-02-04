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
import traceback, sys
from rlcard.games.burraco.action_event_utils import ActionIndexes

# -------------------------
# Worker CPU: SOLO simulazione
# -------------------------
def worker_process(worker_id, traj_queue, param_queue, args, seed_offset=0):
    worker_log = ProcessLogger.get_logger(role=f"worker_{worker_id}")
    try:
        seed = args.seed + seed_offset + worker_id
        set_seed(seed)

        device = torch.device("cpu")
        env = rlcard.make(args.env, config={'seed': seed})
        local_agent = get_agent(env, device, args, worker_log, False)

        opponents = [
            RandomAgent(num_actions=env.num_actions)
            for _ in range(env.num_players - 1)
        ]
        env.set_agents([local_agent] + opponents)

        ep = 0
        while ep < args.num_ep_worker:
            try:
                worker_log.info(f"Worker {worker_id} - Episode [{ep}] START")
                trajs, pays = env.run(is_training=True)
                traj_queue.put((trajs, pays))
                worker_log.info(f"Worker {worker_id} - Episode [{ep}] PAY: {pays}")
            
                # polling non bloccante: aggiorna SOLO i pesi
                try:
                    latest = None
                    while True:
                        latest = param_queue.get_nowait()
                except _pyqueue.Empty:
                    pass

                if latest is not None:
                    checkpoint_data = None
                    
                    if isinstance(latest, str):
                        # Caricamento da file (percorso stringa)
                        checkpoint_data = torch.load(latest, map_location='cpu', weights_only=False)
                    else:
                        # È già un dizionario passato in memoria
                        checkpoint_data = latest
                    
                    # Applichiamo i pesi identificando la struttura corretta
                    if checkpoint_data is not None:
                        state_dict = checkpoint_data['q_estimator']['qnet']
                        if state_dict is not None:
                            local_agent.q_estimator.qnet.load_state_dict(state_dict)
                            local_agent.target_estimator.qnet.load_state_dict(state_dict)
                            worker_log.info(f"Worker {worker_id} - Pesi aggiornati con successo")
                ep += 1
            except Exception:
                tb = traceback.format_exc()
                worker_log.info(f"[W{worker_id}] uncaught Single game exception :\n{tb}")

        traj_queue.put(("__WORKER_DONE__", worker_id))
        worker_log.info(f"__WORKER_DONE__ {worker_id} - Exit")

    except Exception:
        tb = traceback.format_exc()
        worker_log.info(f"[W{worker_id}] UNCAUGHT EXCEPTION:\n{tb}")
        sys.exit(1)


# -------------------------
# Learner GPU: SOLO training
# -------------------------
def learner_process(traj_queue, param_queues, args):
    device = get_device()
    set_seed(args.seed)
    learner_log = ProcessLogger.get_logger(role="learner")

    env = rlcard.make(args.env, config={'seed': args.seed})
    agent = get_agent(env, device, args, learner_log, True)

    opponents = [
        RandomAgent(num_actions=env.num_actions)
        for _ in range(env.num_players - 1)
    ]
    env.set_agents([agent] + opponents)

    # invio primo checkpoint a ogni worker
    for wid, q in enumerate(param_queues):
        save_and_send_ckpt_to_worker(agent, wid, q, step=0, args=args)

    finished_workers = 0
    episode_count = 0

    with Logger(args.log_dir) as logger:
        while finished_workers < args.num_workers:
            # --- blocca l'esecuzione finchè una partita non termina -- thread safe
            item = traj_queue.get()

            # --- worker finito ---
            if isinstance(item, tuple) and item[0] == "__WORKER_DONE__":
                finished_workers += 1
                continue

            # --- traiettoria ---
            trajs, pays = item
            episode_count += 1


            # -------------------------
            # Warmup scheduling
            # -------------------------
            if episode_count == 30000:
                learner_log.info("Switching to fine training phase")
                # train_every: 1000 -> 500
                agent.train_every = 500
                # learning rate: 0.00025 -> 0.0001
                for param_group in agent.q_estimator.optimizer.param_groups:
                    param_group['lr'] = 0.0001
            # -------------------------
            # Warmup scheduling END
            # -------------------------
            
            
            # --- training ---
            reorganized = reorganize(trajs, pays)
            
            # per il bonus partita
            has_won = pays[0] > pays[1]

            # gestione intermedia delle ricompense
            trajectory = reorganized[0] # Traiettoria del tuo agente
            for transition in trajectory:
                # transition = [state, action_id, reward, next_state, done]
                action_id = transition[1]

                if transition[4]:  # end of game
                    if has_won:
                        transition[2] += 0.3
                    else:
                        transition[2] -= 0.3
                        
                # --- penalità discard ---
                if ActionIndexes.DISCARD_ACTION_ID.value[1] <= action_id < ActionIndexes.CLOSE_GAME_ACTION_ID.value[1]:
                    transition[2] -= 0.003

                # --- chiusura corretta ---
                elif ActionIndexes.CLOSE_GAME_ACTION_ID.value[1] <= action_id < ActionIndexes.OPEN_TRIS_ACTION_ID.value[1]:
                    transition[2] += 0.025

                # --- open meld / tris ---
                elif ActionIndexes.OPEN_TRIS_ACTION_ID.value[1] <= action_id < ActionIndexes.UPDATE_TRIS_ACTION_ID.value[1]:
                    transition[2] += 0.006

                # --- update meld ---
                elif ActionIndexes.UPDATE_TRIS_ACTION_ID.value[1] <= action_id < ActionIndexes.CLOSE_GAME_JUDGE_ACTION_ID.value[1]:
                    transition[2] += 0.01
           
            for ts in trajectory:
                agent.feed(ts, learner_log)
            learner_log.info(f"End   Feed")

            # valutazione periodica (bloccante)
            if episode_count % args.eval_every == 0:
                learner_log.info(f"Tournament - episode_count:{episode_count}")
                result = tournament(env, args.num_eval_games)[0]
                logger.log_performance(
                    episode_count, result
                )
                learner_log.info(f"Tournament end -- average pay: {result}")

                # invio checkpoint aggiornato
                #step = episode_count * args.train_every
                step = agent.total_t
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
# Agent factory
# =========================
def get_agent(env, device, args, logger, is_learner = False):


    if args.algorithm == 'dqn':
        from rlcard.agents import DQNAgent
        if args.load_checkpoint_path != "":
            logger.info(f"Loading from: {args.load_checkpoint_path}")
            ckpt = torch.load(args.load_checkpoint_path,weights_only=False)
            agent = DQNAgent.from_checkpoint(checkpoint=ckpt)
            agent.device = device
            return agent
        
        current_mem_size = 500000 if is_learner else 1000
        current_init_size = 50000 if is_learner else 100
        return DQNAgent(
            replay_memory_size=current_mem_size,
            replay_memory_init_size=current_init_size,
            #per test
            #replay_memory_init_size=1000,
            # OLD -- update_target_estimator_every=2500,
            # OLD -- update_target_estimator_every=10000,
            # multi-worker asincrono - replay rumoroso - riduce oscillazioni forti nei tornei
            update_target_estimator_every=3000,
            discount_factor=0.99,
            epsilon_start=1.0,
            # OLD -- epsilon_end=0.1,
            epsilon_end=0.05,
            # OLD -- epsilon_decay_steps=200000,
            # OLD -- epsilon_decay_steps=400000,
            epsilon_decay_steps=300000,
            batch_size=256,
            num_actions=env.num_actions,
            state_shape=env.state_shape[0],
            # OLD -- mlp_layers=[128, 128],
            # OLD -- mlp_layers=[512, 512, 256],
            mlp_layers=[256, 256],
            # ---OLD learning_rate=0.0003,
            # ---OLD learning_rate=0.0001,
            learning_rate=0.0001,
            device=device,
            save_path=args.log_dir,
            save_every=args.save_every,
            train_every=args.train_every
        )



# -------------------------
# Main: orchestration
# -------------------------
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


if __name__ == "__main__":
    path = f"experiments/burraco_dqn_result/{datetime.now().strftime('%Y_%m_%d_%H%M%S')}"
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default="burraco")
    parser.add_argument("--algorithm", default="dqn")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--log_dir", default=path)
    parser.add_argument("--save_every", type=int, default=-1)
    parser.add_argument("--num_workers", type=int, default=6)
    # 100k episodi totali
    # 16667 * 6 = 100k episodi totali + tornei
    # parser.add_argument("--num_ep_worker", type=int, default=16667)
    # 16667 - 4600 = 12067 errore bloccante
    #parser.add_argument("--num_ep_worker", type=int, default=16667)
    # [20/01/2026] --> 16667 - 9400 = 7267 fermato processo per rallentamento
    parser.add_argument("--num_ep_worker", type=int, default=7267)
    parser.add_argument("--train_every", type=int, default=2000)
    parser.add_argument("--eval_every", type=int, default=10000)
    parser.add_argument("--num_eval_games", type=int, default=25)
    # 25 partite di torneo ogni 10000 partite giocate dai worker
    #parser.add_argument("--load_checkpoint_path", default="")
    parser.add_argument("--load_checkpoint_path", default="experiments/burraco_dqn_result/2026_01_16_135238/checkpoint_dqn.pt")

    args = parser.parse_args()
    main(args)