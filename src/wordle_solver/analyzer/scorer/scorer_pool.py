from decimal import Decimal
from multiprocessing import Pool
from typing import Iterable

from wordle_solver.analyzer.scorer.scorer_child import init_scorer_child, process, update, reset
from wordle_solver.common.guess_result import GuessResult


class ScorerPool:
    def __init__(self, num_processes: int, words: list[int]):
        self._update_id = 0
        self._reset_id = 0
        self._num_processes = num_processes
        self._pool = Pool(processes=num_processes, initializer=init_scorer_child, initargs=(words,))

    def process(self, words: list[str]) -> Iterable[Decimal]:
        return self._pool.map(process, words)

    def update(self, res: GuessResult):
        finished = set()

        while len(finished) < self._num_processes:
            ret = self._pool.map(update, [self._update_id] * self._num_processes, [res] * self._num_processes)
            for child_id in ret:
                finished.add(child_id)

        self._update_id += 1

    def reset(self):
        finished = set()

        while len(finished) < self._num_processes:
            ret = self._pool.map(reset, [self._reset_id] * self._num_processes)
            for child_id in ret:
                finished.add(child_id)

        self._reset_id += 1
