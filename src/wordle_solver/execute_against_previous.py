import argparse

from wordle_solver.analyzer.candidate_guess.candidate_guesser_factory import CandidateGuesserFactory
from wordle_solver.analyzer.candidate_guess.guesser_type import GuesserType
from wordle_solver.executor.executor import Executor

parser = argparse.ArgumentParser()
parser.add_argument('-g', '--candidate_guessing_strategy', type=GuesserType.from_string, default=GuesserType.NoGuess)
parser.add_argument('--num_common_chars', type=int, default=2)
parser.add_argument('--num_candidate_guesses', type=int, default=100)


def main():
    args = parser.parse_args()

    candidate_guesser_factory = CandidateGuesserFactory(args.candidate_guessing_strategy, args.num_common_chars, args.num_candidate_guesses)
    candidate_guesser_builder = candidate_guesser_factory.build()
    executor = Executor(candidate_guesser_builder)

    executor.execute()


if __name__ == '__main__':
    main()
