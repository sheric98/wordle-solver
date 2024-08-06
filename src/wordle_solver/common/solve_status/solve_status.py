from collections import Counter, defaultdict
from typing import Any, Iterable, Optional, Self

from wordle_solver.common.solve_status.char_status import CharStatus
from wordle_solver.common.solve_status.single_filter import SingleFilter
from wordle_solver.common.solve_status.single_filter_type import SingleFilterType
from wordle_solver.common.solve_status.yellow_result_type import YellowResultType
from wordle_solver.common.solve_status.yellow_status import YellowStatus
from wordle_solver.common.single_result import SingleResult
from wordle_solver.util.constants import WORD_LENGTH

_ALL_CHARS = set('abcdefghjiklmnopqrstuvwxyz')


class SolveStatus:
    def __init__(self):
        self.single_statuses: list[SingleFilter] = [SingleFilter() for _ in range(WORD_LENGTH)]
        # self.must_contain: set[str] = set()
        self.must_not_contain: set[str] = set()
        # self.guaranteeds: set[str] = set()
        self.greens: list[Optional[str]] = [None] * WORD_LENGTH
        self._unknowns = set(range(WORD_LENGTH))
        # self._yellows: dict[str, YellowStatus] = {}
        self._uncertains = WORD_LENGTH
        # self._guessed_words = []
        self._char_statuses: dict[str, CharStatus] = {}
        self._num_guesses = 0

    def tup(self) -> tuple[Any]:
        return (self._num_guesses, tuple(sorted(self.must_not_contain)), tuple(sorted(((c, c_s.tup()) for c, c_s in self._char_statuses.items()), key=lambda x: x[0])))

    @staticmethod
    def make_char_filter(chars: Iterable[str]) -> Self:
        ret = SolveStatus()
        ret.must_contain.update(chars)
        return ret
    
    def _convert_results_to_char_statuses(self, guessed_word: str, results: list[SingleResult]) -> dict[str, CharStatus]:
        statuses = defaultdict(lambda: CharStatus(self._unknowns.copy()))
        grays = set()

        for i, (c, single_res) in enumerate(zip(guessed_word, results)):
            if single_res == SingleResult.GRAY:
                grays.add(c)
            else:
                statuses[c].count += 1
                if single_res == SingleResult.GREEN:
                    self.greens[i] = c
                    self.single_statuses[i].make_guaranteed(c)
                    self._unknowns.discard(i)
                    statuses[c].known.add(i)
                    for c_s in statuses.values():
                        c_s.possible.discard(i)
                else:
                    self.single_statuses[i].try_add_not(c)
                    statuses[c].possible.discard(i)

        for c in grays:
            if c in statuses:
                statuses[c].capped = True
            else:
                self.must_not_contain.add(c)

        return statuses

    def add_results(self, guessed_word: str, results: list[SingleResult]):
        self._num_guesses += 1
        # self._guessed_words.append(guessed_word)

        single_char_statuses: dict[str, CharStatus] = self._convert_results_to_char_statuses(guessed_word, results)
        new_guaranteed: dict[str, set[int]] = defaultdict(set)

        for c, c_s in single_char_statuses.items():
            if c not in self._char_statuses:
                self._char_statuses[c] = c_s
                # new_guaranteed[c].update(c_s.known)
            else:
                ret = self._char_statuses[c].combine(c_s)
                # if ret is not None:
                #     new_guaranteed[c].update(ret)

        # while new_guaranteed:
        #     for c, guarantees in new_guaranteed.items():
        #         for i in guarantees:
        #             self.single_statuses[i].make_guaranteed(c)
        #             self.greens[i] = c
        #             for c_s in self._char_statuses.values():
        #                 c_s.possible.discard(i)

        #     new_guaranteed = defaultdict(set)
        #     for c, c_s in self._char_statuses.items():
        #         ret = c_s.check_combine()
        #         if ret is not None:
        #             new_guaranteed[c].update(ret)

        # for c, c_s in self._char_statuses.items():
        #     if c_s.check_finished():
        #         self.must_not_contain.add(c)


        # yellow_counts: dict[str, list[int]] = defaultdict(list)
        # capped: set[str] = set()

        # for i, (c, single_res) in enumerate(zip(guessed_word, results)):
        #     if single_res == SingleResult.GREEN:
        #         self.guaranteeds.add(c)
        #         changed = self.single_statuses[i].make_guaranteed(c)
        #         self.greens[i] = c
        #         if changed and c in self._yellows:
        #             self._yellows[c].add_guaranteed(i)
        #         self.must_contain.discard(c)
        #     elif single_res == SingleResult.YELLOW:
        #         yellow_counts[c].append(i)
        #         self.single_statuses[i].try_add_not(c)
        #         if c not in self.guaranteeds:
        #             self.must_contain.add(c)
        #     else:
        #         if c in yellow_counts:
        #             capped.add(c)
        #         else:
        #             self.must_not_contain.add(c)

        # for c, idxs in yellow_counts.items():
        #     if c in self._yellows:
        #         self._yellows[c].update_seen(idxs, c in capped)
        #     else:
        #         self._yellows[c] = YellowStatus(c, idxs, c in capped)

        # to_del = []
        # for yellow_status in self._yellows.values():
        #     ret = yellow_status.try_consolidate()
        #     if ret is not None:
        #         if ret.t == YellowResultType.GUARANTEED:
        #             self.must_not_contain.add(yellow_status.c)
        #             for idx in ret.vals:
        #                 self.single_statuses[idx].make_guaranteed(yellow_status.c)
        #                 self.greens[idx] = yellow_status.c

        #         to_del.append(yellow_status.c)

        # for c in to_del:
        #     del self._yellows[c]

        self._uncertains = 0
        for g in self.greens:
            if g is None:
                self._uncertains += 1

    def get_valid(self, word: str) -> bool:
        uncertain_counts = defaultdict(lambda: 0)
        for i, c in enumerate(word):
            if i in self._unknowns:
                if c in self._char_statuses:
                    if i not in self._char_statuses[c].possible:
                        print(f'{word} not possible in {self._char_statuses[c]} because of {c} at {i}')
                        return False
                uncertain_counts[c] += 1

        for c, c_s in self._char_statuses.items():
            unknown_count = c_s.unknown_count()
            if unknown_count > 0:
                if c not in uncertain_counts:
                    return False
                cnt = uncertain_counts[c]
                if cnt < unknown_count or (cnt > unknown_count and c_s.capped):
                    return False
                
        return True
            

    def get_uncertain_candidates(self, curr_str: str, base_chars_arr: list[set[str]]) -> Iterable[str]:
        # need_addressing = {}
        # for c, c_s in self._char_statuses.items():
        #     if c_s.unknown_count > 0:
        #         need_addressing[c] = c_s.unknown_count

        # additional_not_alloweds = set()
        # remaining_uncertains = self._uncertains

        # for i, c in enumerate(curr_str):
        #     if self.greens[i] is not None:
        #         continue

        #     if c in need_addressing:
        #         need_addressing[c] -= 1
        #         if need_addressing == 0:
        #             del need_addressing[c]
        #             if self._char_statuses[c].capped:
        #                 additional_not_alloweds.add(c)
        #     remaining_uncertains -= 1

        # still_need_addressing = sum(need_addressing.values())

        # if still_need_addressing > remaining_uncertains:
        #     return []
        
        cand_i = len(curr_str)
        # must_bes = []
        # for c, cnt in need_addressing.items():
        #     valid = [i for i in self._char_statuses[c].possible if i >= cand_i]
        #     if cnt > len(valid):
        #         return []
        #     elif cnt == len(valid):
        #         must_bes.append(c)

        # if len(must_bes) > 1:
        #     return []
        # elif len(must_bes) == 1:
        #     return must_bes

        # if still_need_addressing == remaining_uncertains:
        #     ret = []
        #     for c in need_addressing:
        #         if cand_i in self._char_statuses[c].possible:
        #             ret.append(c)

        #     return ret
        
        # return base_chars_arr[cand_i] - additional_not_alloweds
        return base_chars_arr[cand_i]

    def get_base_chars_arr(self) -> list[set[str]]:
        base_chars: set[str] = _ALL_CHARS - self.must_not_contain
        base_chars_by_i: list[set[str]] = []
        for single_filter in self.single_statuses:
            if single_filter.filter_type == SingleFilterType.ANY:
                viable_chars = base_chars
            elif single_filter.filter_type == SingleFilterType.NOT:
                viable_chars = base_chars - single_filter.val
            else:
                viable_chars = {single_filter.val}
            base_chars_by_i.append(viable_chars)

        return base_chars_by_i

    def copy(self) -> Self:
        new_obj = SolveStatus()
        new_obj._num_guesses = self._num_guesses
        new_obj.single_statuses = [sf.copy() for sf in self.single_statuses]
        new_obj.must_not_contain = self.must_not_contain.copy()
        new_obj.greens = self.greens.copy()
        new_obj._unknowns = self._unknowns.copy()
        new_obj._uncertains = self._uncertains
        new_obj._char_statuses = {c: c_s.copy() for c, c_s in self._char_statuses.items()}

        return new_obj
    