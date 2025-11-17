# parallel_run_rl_cpu_workers.py
import argparse
import os
import time
import multiprocessing as mp
from datetime import datetime
from Utils.logger import SingletonLogger 

import torch
import rlcard
from rlcard.utils import Logger, set_seed, get_device, reorganize, plot_curve, tournament



import traceback
import sys
def worker_process(worker_id, traj_queue, param_queue, args, seed_offset = 0):

    print(f"[W{worker_id}]")
    try:
        seed = args.seed
        worker_seed = seed + seed_offset + worker_id
        print(f"[W{worker_id}] Avvio worker su CPU (seed={worker_seed})")
        set_seed(worker_seed)

        # Forza l'uso della CPU anche se disponibile GPU
        device = torch.device("cpu")
        print(f"[W{worker_id}] Avvio worker su CPU (seed={worker_seed})")

        env = rlcard.make(args.env, config={'seed': worker_seed})

        # Attende un checkpoint iniziale dal main process
        checkpoint = None
        while checkpoint is None:
            try:
                checkpoint = param_queue.get(timeout=5)
            except Exception:
                continue

        # Crea agente locale da checkpoint (solo per inference)
        local_agent = get_agent(env, device, args)
        # Imposta agents: agente locale + avversari random
        agents = [local_agent]
        from rlcard.agents import RandomAgent
        for _ in range(1, env.num_players):
            agents.append(RandomAgent(num_actions=env.num_actions))
        env.set_agents(agents)

        produced = 0
        for ep in range(args.num_ep_worker):
            print(f"starting [worker - {worker_id}] - [EP - {ep}] ")
            trajs, pays = env.run(is_training=True)
            traj_queue.put((trajs, pays))
            produced += 1
            # Polling per aggiornamenti di checkpoint (policy aggiornata)
            while not param_queue.empty():
                try:
                    new_ckpt = param_queue.get_nowait()
                    if args.algorithm == 'dqn':
                        from rlcard.agents import DQNAgent
                        local_agent = DQNAgent.from_checkpoint(checkpoint=new_ckpt)
                    else:
                        from rlcard.agents import NFSPAgent
                        local_agent = NFSPAgent.from_checkpoint(checkpoint=new_ckpt)
                    agents[0] = local_agent
                    env.set_agents(agents)
                    print(f"[W{worker_id}] Aggiornato modello locale da nuovo checkpoint")
                except Exception:
                    break

        traj_queue.put(("__WORKER_DONE__", worker_id))
        print(f"[W{worker_id}] Terminato, episodi generati: {produced}")
    
    except Exception:
        tb = traceback.format_exc()
        # prova a scrivere lo stacktrace nel log dir principale
        try:
            os.makedirs(args.log_dir, exist_ok=True)
            err_path = os.path.join(args.log_dir, f"worker_{worker_id}_exc.txt")
            with open(err_path, "w", encoding="utf-8") as f:
                f.write(tb)
        except Exception:
            # se non posso scrivere, almeno stampo su stderr (flush)
            print(f"[W{worker_id}] Errore e non posso scrivere file: {tb}", file=sys.stderr, flush=True)
        # esci con codice non-zero
        sys.exit(1)


def main(args):
    mp.set_start_method('spawn', force=True)
    param_queue = mp.Queue(maxsize=args.num_workers)
    traj_queue = mp.Queue(maxsize=64)

    
    main_log = SingletonLogger().get_logger()

    main_log.info(f" num_workers            : {args.num_workers}")
    main_log.info(f" num_ep_worker          : {args.num_ep_worker}")
    main_log.info(f" num_eval_games         : {args.num_eval_games}")
    main_log.info(f" train_every            : {args.train_every}")
    # --- Processo principale (GPU) ---
    device = get_device()  # qui userà la GPU se disponibile
    set_seed(args.seed)
    env_for_agent = rlcard.make(args.env, config={'seed': args.seed})

    central_agent = get_agent(env_for_agent, device, args)
    main_log.info("get_agent")

    agents = [central_agent]
    from rlcard.agents import RandomAgent
    for _ in range(1, env_for_agent.num_players):
        agents.append(RandomAgent(num_actions=env_for_agent.num_actions))
    env_for_agent.set_agents(agents)
    main_log.info("set_agents")

    # Invia il primo checkpoint ai worker
    init_ckpt = central_agent.checkpoint_attributes()
    import pickle

    try:
        pickle.dumps(init_ckpt)
        print("PICKLE OK")
    except Exception as e:
        print("PICKLE ERROR:", e)
    main_log.info("checkpoint_attributes")
    for _ in range(args.num_workers):
        param_queue.put(init_ckpt)
    main_log.info("param_queue.put")

    # --- Avvio dei worker (solo CPU) ---
    processes = []
    main_log.info("startig processes 1")
    for wid in range(args.num_workers):
        p = mp.Process(target=worker_process, args=(wid, traj_queue, param_queue, args))
        main_log.info("startig processes 2")
        p.start()
        processes.append(p)
        time.sleep(0.5)

    finished_workers = 0
    buffer_count = 0
    episode_count = 0
    
    with Logger(args.log_dir) as logger:
        while finished_workers < args.num_workers:
            item = traj_queue.get()
            if isinstance(item, tuple) and item[0] == "__WORKER_DONE__":
                finished_workers += 1
                main_log.info(f"[Main] Worker {item[1]} completato ({finished_workers}/{args.num_workers})")
                continue

            trajs, pays = item
            episode_count += 1
            reorganized = reorganize(trajs, pays)
            for ts in reorganized[0]:
                central_agent.feed(ts)
                buffer_count += 1

            # Esegue training ogni N transizioni raccolte
            if buffer_count >= args.train_every:
                main_log.info(f"buffer_count >= args.train_every --> {buffer_count} - {args.train_every}")
                central_agent.train()
                buffer_count = 0
            
            if episode_count % args.eval_every == 0:
                main_log.info("")
                logger.log_performance(
                    episode_count * args.train_every,
                    tournament(
                        env_for_agent,
                        args.num_eval_games,
                    )[0]
                )
                # Invia nuovo checkpoint ai worker
                ckpt = central_agent.checkpoint_attributes()
                for _ in range(args.num_workers):
                    param_queue.put(ckpt)
        # Get the paths
        csv_path, fig_path = logger.csv_path, logger.fig_path
        try:
            main_log.info("Logger closed")
            logger.close()
            main_log.info("Logger closed")
        except Exception as e_logger:
            main_log.error(f"Error while closing Logger - {e_logger}")

    main_log.info("Joining processes")
    for p in processes:
        p.join()
    main_log.info("Joining processes end")

    main_log.info("Closing Queues")
    main_log.info(f"traj_queue size before close: {traj_queue.qsize()}")
    main_log.info("active children:", mp.active_children())

    # --- CHIUSURA CODE ---
    try:
        traj_queue.close()
        traj_queue.join_thread()
        param_queue.close()
        param_queue.join_thread()
        main_log.info("Queues closed")
    except Exception as e:
        main_log.error("Errore chiusura code:", e)

    main_log.info("FORCE SHUTDOWN processes")
    # --- FORCE SHUTDOWN eventuale ---
    for p in processes:
        if p.is_alive():
            main_log.warning(f"[Main] Worker {p.pid} ancora vivo, terminate()...")
            p.terminate()

    # Salva modello finale
    main_log.info("Saving Model")
    os.makedirs(args.log_dir, exist_ok=True)
    save_path = os.path.join(args.log_dir, "final_model.pth")
    torch.save(central_agent, save_path)
    main_log.info(f"[Main] Modello finale salvato in {save_path}")

    # Plot the learning curve
    main_log.info("Saving Statistics")
    plot_curve(csv_path, fig_path, args.algorithm)


    # --- chiudi SingletonLogger ---
    try:
        main_log.info("Closing main_log")
        for h in main_log.handlers:
            h.close()
            main_log.removeHandler(h)
    except:
        pass


def get_agent(env, device, args):
    # Initialize the agent and use random agents as opponents
    agent = None
    if args.algorithm == 'dqn':
        from rlcard.agents import DQNAgent
        if args.load_checkpoint_path != "":
            agent = DQNAgent.from_checkpoint(checkpoint=torch.load(args.load_checkpoint_path))
        else:
            agent = DQNAgent(
                num_actions=env.num_actions,
                state_shape=env.state_shape[0],
                mlp_layers=[64,64],
                device=device,
                save_path=args.log_dir,
                save_every=args.save_every
            )

    elif args.algorithm == 'nfsp':
        from rlcard.agents import NFSPAgent
        if args.load_checkpoint_path != "":
            agent = NFSPAgent.from_checkpoint(checkpoint=torch.load(args.load_checkpoint_path))
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
    parser.add_argument("--load_checkpoint_path", default="")

    #default 32
    parser.add_argument("--train_every", type=int, default=32)
    parser.add_argument("--num_workers", type=int, default=5)
    parser.add_argument("--num_ep_worker", type=int, default=2)
    parser.add_argument("--num_eval_games", type=int, default=1)
    parser.add_argument("--eval_every", type=int, default=5)

    args = parser.parse_args()
    main(args)
