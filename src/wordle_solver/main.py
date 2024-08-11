import argparse
import os

from wordle_solver.analyzer.candidate_guess.candidate_guesser_factory import CandidateGuesserFactory
from wordle_solver.analyzer.candidate_guess.guesser_type import GuesserType
from wordle_solver.solver.solver import Solver

parser = argparse.ArgumentParser()
parser.add_argument('--recompute_start', default=False, action='store_true')
parser.add_argument('-d', '--max_search_depth', type=int, default=1)
parser.add_argument('-g', '--candidate_guessing_strategy', type=GuesserType.from_string, default=GuesserType.NoGuess)
parser.add_argument('--num_common_chars', type=int, default=2)
parser.add_argument('--num_candidate_guesses', type=int, default=100)
parser.add_argument('--num_processes', type=int, default=os.cpu_count())


def main():
    args = parser.parse_args()
    use_computed_start = not args.recompute_start

    candidate_guesser_factory = CandidateGuesserFactory(args.candidate_guessing_strategy, args.num_common_chars, args.num_candidate_guesses)
    candidate_guesser_builder = candidate_guesser_factory.build()
    solver = Solver(candidate_guesser_builder, args.num_processes, use_computed_start=use_computed_start, max_search_depth=args.max_search_depth)
    solver.play()


if __name__ == '__main__':
    main()
