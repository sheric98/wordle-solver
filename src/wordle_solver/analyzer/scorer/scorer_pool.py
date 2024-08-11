from decimal import Decimal
from itertools import repeat
from multiprocessing import Pool
from tqdm import tqdm
from typing import Iterable

from wordle_solver.analyzer.scorer.scorer_child import init_scorer_child, process, update, reset
from wordle_solver.common.guess_result import GuessResult


class ScorerPool:
    def __init__(self, num_processes: int, words: list[int]):
        self._update_id = 0
        self._reset_id = 0
        self._num_processes = num_processes
        self._pool = Pool(processes=num_processes, initializer=init_scorer_child, initargs=(words,))

    def process(self, indexes: Iterable[int], depth: int, num_items: int) -> Iterable[Decimal]:
        return list(tqdm(self._pool.imap(process, zip(indexes, repeat(depth))), total=num_items))

    def update(self, word: str, res: GuessResult):
        finished = set()

        while len(finished) < self._num_processes:
            ret = self._pool.map(update, zip(repeat(self._update_id, self._num_processes), repeat(word, self._num_processes), repeat(res, self._num_processes)))
            for child_id in ret:
                finished.add(child_id)

        self._update_id += 1

    def reset(self):
        finished = set()

        while len(finished) < self._num_processes:
            ret = self._pool.map(reset, repeat(self._reset_id, self._num_processes))
            for child_id in ret:
                finished.add(child_id)

        self._reset_id += 1
