''' An example of playing randomly in RLCard
'''
import argparse
import pprint

import rlcard
from rlcard.agents import RandomAgent
from rlcard.utils import set_seed
from datetime import datetime
import time

def run(args):

    seed = int(datetime.now().strftime("%S%f"))
    # Make environment
   #env = rlcard.make(
   #    args.env,
   #    config={
   #        'seed': seed,
   #    }
   #)

    print("solver:" + args.csp_solver)
    config = {'seed': seed}
    if hasattr(args, 'csp_solver') and args.csp_solver:
        config['csp_solver'] = args.csp_solver
    env = rlcard.make(args.env, config=config)

    # Seed numpy, torch, random
    set_seed(seed)

    # Set agents
    agent = RandomAgent(num_actions=env.num_actions)
    env.set_agents([agent for _ in range(env.num_players)])

    # Generate data from the environment
    start = time.perf_counter()          # o time.time()
    ep = 0
    while ep < args.num_games:
        trajectories, player_wins = env.run(is_training=False)
        # Print out the trajectories
        ep += 1
        #print(f'\n------------ EP{ep}----------')
        #print('\nTrajectories:')
        #print(trajectories)
        #print('\nSample raw observation:')
        #pprint.pprint(trajectories[0][0]['raw_obs'])
        #print('\nSample raw legal_actions:')
        #pprint.pprint(trajectories[0][0]['raw_legal_actions'])
    
    end = time.perf_counter()
    print(f"elapsed {end-start:.6f} s")

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Random example in RLCard")
    parser.add_argument(
        '--env',
        type=str,
        default='burraco',
        choices=[
            'blackjack',
            'leduc-holdem',
            'burraco',
            'limit-holdem',
            'doudizhu',
            'mahjong',
            'no-limit-holdem',
            'uno',
            'gin-rummy',
            'bridge',
        ],
    )

    parser.add_argument("--num_games", type=int, default=10)
    parser.add_argument("--csp_solver", default="solve_csp")


    args = parser.parse_args()

    run(args)

