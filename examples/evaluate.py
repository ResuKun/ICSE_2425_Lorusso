''' An example of evluating the trained models in RLCard
'''
import os
import argparse
from datetime import datetime

from Utils.logger import ProcessLogger
import rlcard
from rlcard.agents import (
    DQNAgent,
    RandomAgent,
)
from rlcard.utils import (
    Logger,
    get_device,
    set_seed,
    simple_tournament,
    plot_curve
)

def load_model(model_path, env=None, position=None, device=None):
    if os.path.isfile(model_path):  # Torch model
        import torch
        agent = torch.load(model_path, map_location=device)
        agent.set_device(device)
    elif os.path.isdir(model_path):  # CFR model
        from rlcard.agents import CFRAgent
        agent = CFRAgent(env, model_path)
        agent.load()
    elif model_path == 'random':  # Random model
        from rlcard.agents import RandomAgent
        agent = RandomAgent(num_actions=env.num_actions)
    else:  # A model in the model zoo
        from rlcard import models
        agent = models.load(model_path).agents[position]
    
    return agent

def evaluate(args):
    worker_log = ProcessLogger.get_logger(role=f"Evaluation")
    worker_log.info(f" num_games          : {args.num_games}")

    # Check whether gpu is available
    device = get_device()
        
    # Seed numpy, torch, random
    set_seed(args.seed)

    # Make the environment with seed
    env = rlcard.make(args.env, config={'seed': args.seed})

    # Load models
    agents = []
    for position, model_path in enumerate(args.models):
        worker_log.info(f" model_path          : {model_path}")
        agents.append(load_model(model_path, env, position, device))
    env.set_agents(agents)

    with Logger(args.log_dir) as logger:
        rewards = simple_tournament(env, args.num_games, worker_log)
        p0_rewards = [r[0] * 500 for r in rewards]
        p1_rewards = [r[1] * 500 for r in rewards]
        for episode, val in enumerate(p0_rewards):
            logger.log_performance(episode + 1, val)
            
        fig_path = logger.fig_path
        
    plot_curve(p0_rewards, p1_rewards, fig_path, "DQN Model", "Random Model")


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Evaluation example in RLCard")
    path = f"experiments/burraco_dqn_TOURNAMENTS/{datetime.now().strftime('%Y_%m_%d_%H%M%S')}"
    parser.add_argument(
        '--env',
        type=str,
        default='burraco',
        choices=[
            'blackjack',
            'leduc-holdem',
            'limit-holdem',
            'doudizhu',
            'mahjong',
            'no-limit-holdem',
            'uno',
            'gin-rummy',
            'burraco',
        ],
    )
    parser.add_argument(
        '--models',
        nargs='*',
        default=[
            #'experiments/burraco_dqn_result/2026_02_12_183630/final_model.pth',
            'random',
            'random',
            #'experiments/burraco_dqn_result/2026_02_04_200258/final_model.pth',
        ],
    )
    parser.add_argument(
        "--log_dir", 
        default=path
    )
    parser.add_argument(
        '--cuda',
        type=str,
        default='',
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
    )
    parser.add_argument(
        '--num_games',
        type=int,
        default=100,
    )

    parser.add_argument(
        "--algorithm", 
        default="dqn"
    )

    args = parser.parse_args()
    evaluate(args)

