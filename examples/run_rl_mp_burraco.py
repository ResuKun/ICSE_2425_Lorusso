# parallel_run_rl_cpu_workers.py
import argparse
import os
import time
import multiprocessing as mp
from datetime import datetime

import torch
import rlcard
from rlcard.utils import Logger, set_seed, get_device, reorganize, plot_curve, tournament

NUM_WORKERS = 5
EPISODES_PER_WORKER = 2
BASE_SEED = 42


def worker_process(worker_id, env_name, algorithm, traj_queue, param_queue, seed_offset=0):
    worker_seed = BASE_SEED + seed_offset + worker_id
    set_seed(worker_seed)

    # Forza l'uso della CPU anche se disponibile GPU
    device = torch.device("cpu")
    print(f"[W{worker_id}] Avvio worker su CPU (seed={worker_seed})")

    env = rlcard.make(env_name, config={'seed': worker_seed})

    # Attende un checkpoint iniziale dal main process
    checkpoint = None
    while checkpoint is None:
        try:
            checkpoint = param_queue.get(timeout=5)
        except Exception:
            continue

    # Crea agente locale da checkpoint (solo per inference)
    if algorithm == 'dqn':
        from rlcard.agents import DQNAgent
        local_agent = DQNAgent.from_checkpoint(checkpoint=checkpoint)
    else:
        from rlcard.agents import NFSPAgent
        local_agent = NFSPAgent.from_checkpoint(checkpoint=checkpoint)

    # Imposta agents: agente locale + avversari random
    agents = [local_agent]
    from rlcard.agents import RandomAgent
    for _ in range(1, env.num_players):
        agents.append(RandomAgent(num_actions=env.num_actions))
    env.set_agents(agents)

    produced = 0
    for ep in range(EPISODES_PER_WORKER):
        trajs, pays = env.run(is_training=True)
        traj_queue.put((trajs, pays))
        produced += 1

        # Polling per aggiornamenti di checkpoint (policy aggiornata)
        while not param_queue.empty():
            try:
                new_ckpt = param_queue.get_nowait()
                if algorithm == 'dqn':
                    local_agent = DQNAgent.from_checkpoint(checkpoint=new_ckpt)
                else:
                    local_agent = NFSPAgent.from_checkpoint(checkpoint=new_ckpt)
                agents[0] = local_agent
                env.set_agents(agents)
                print(f"[W{worker_id}] Aggiornato modello locale da nuovo checkpoint")
            except Exception:
                break

    traj_queue.put(("__WORKER_DONE__", worker_id))
    print(f"[W{worker_id}] Terminato, episodi generati: {produced}")


def main(args):
    mp.set_start_method('spawn', force=True)
    traj_queue = mp.Queue(maxsize=NUM_WORKERS * 10)
    param_queue = mp.Queue()

    # --- Processo principale (GPU) ---
    device = get_device()  # qui userà la GPU se disponibile
    set_seed(args.seed)
    env_for_agent = rlcard.make(args.env, config={'seed': args.seed})

    if args.algorithm == 'dqn':
        from rlcard.agents import DQNAgent
        central_agent = DQNAgent(
            num_actions=env_for_agent.num_actions,
            state_shape=env_for_agent.state_shape[0],
            mlp_layers=[64, 64],
            device=device,
            save_path=args.log_dir,
            save_every=args.save_every,
        )
    else:
        from rlcard.agents import NFSPAgent
        central_agent = NFSPAgent(
            num_actions=env_for_agent.num_actions,
            state_shape=env_for_agent.state_shape[0],
            hidden_layers_sizes=[64, 64],
            q_mlp_layers=[64, 64],
            device=device,
            save_path=args.log_dir,
            save_every=args.save_every,
        )

    agents = [central_agent]
    from rlcard.agents import RandomAgent
    for _ in range(1, env_for_agent.num_players):
        agents.append(RandomAgent(num_actions=env_for_agent.num_actions))
    env_for_agent.set_agents(agents)
    # Invia il primo checkpoint ai worker
    init_ckpt = central_agent.checkpoint_attributes()
    for _ in range(NUM_WORKERS):
        param_queue.put(init_ckpt)

    # --- Avvio dei worker (solo CPU) ---
    processes = []
    for wid in range(NUM_WORKERS):
        p = mp.Process(target=worker_process, args=(wid, args.env, args.algorithm, traj_queue, param_queue, args.seed))
        p.start()
        processes.append(p)
        time.sleep(0.5)

    finished_workers = 0
    buffer_count = 0
    episode_count = 1
    
    with Logger(args.log_dir) as logger:
        while finished_workers < NUM_WORKERS:
            item = traj_queue.get()
            if isinstance(item, tuple) and item[0] == "__WORKER_DONE__":
                finished_workers += 1
                print(f"[Main] Worker {item[1]} completato ({finished_workers}/{NUM_WORKERS})")
                continue

            trajs, pays = item
            reorganized = reorganize(trajs, pays)
            for ts in reorganized[0]:
                central_agent.feed(ts)
                buffer_count += 1

            # Esegue training ogni N transizioni raccolte
            if buffer_count >= args.train_every:
                central_agent.train()
                buffer_count = 0
                logger.log_performance(
                    episode_count * args.train_every,
                    tournament(
                        env_for_agent,
                        args.num_eval_games,
                    )[0]
                )
                episode_count += 1
                # Invia nuovo checkpoint ai worker
                ckpt = central_agent.checkpoint_attributes()
                for _ in range(NUM_WORKERS):
                    param_queue.put(ckpt)
        # Get the paths
        csv_path, fig_path = logger.csv_path, logger.fig_path

    for p in processes:
        p.join()

    # Salva modello finale
    os.makedirs(args.log_dir, exist_ok=True)
    save_path = os.path.join(args.log_dir, "final_model.pth")
    torch.save(central_agent, save_path)
    print(f"[Main] Modello finale salvato in {save_path}")

    # Plot the learning curve
    plot_curve(csv_path, fig_path, args.algorithm)


def create_tournament_env(args):
        env = rlcard.make(
            args.env,
            config={ 'seed': args.seed,} )
        

if __name__ == "__main__":
    path = f"experiments/burraco_dqn_result/{datetime.now().strftime('%Y_%m_%d_%H%M%S')}"
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default="burraco")
    parser.add_argument("--algorithm", default="dqn", choices=["dqn", "nfsp"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--log_dir", default=path)
    parser.add_argument("--save_every", type=int, default=-1)
    parser.add_argument("--train_every", type=int, default=5)
    parser.add_argument("--num_eval_games", type=int, default=1)
    args = parser.parse_args()
    main(args)
