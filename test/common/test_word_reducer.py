from collections import Counter
import numpy as np

from wordle_solver.common.guess_result import GuessResult, to_res_arr
from wordle_solver.common.single_result import SingleResult
from wordle_solver.common.solve_status.solve_status_np import SolveStatusNp
from wordle_solver.common.word_reducer import WordReducer
from wordle_solver.util.word_utils import convert_word


TEST_CANDIDATES: list[str] = ["robot", "oreos", "taurs", "tares", "teams", "trrrs", "sweet", "feral", "coyly"]


def test_single():
    test_guess = "tsooo"
    test_answer = "teams"

    expected_results = ["teams", "taurs", "tares", "trrrs"]

    _test_validity(TEST_CANDIDATES, [test_guess], [test_answer], [expected_results])


def test_capped():
    test_guess = "tsrxr"
    test_answer = "taurs"

    expected_results = ["taurs"]
    _test_validity(TEST_CANDIDATES, [test_guess], [test_answer], [expected_results])


def test_feral():
    test_guesses = ["tares", "buzzy", "powie"]
    test_answers = ["feral", "feral", "feral"]

    expected_results = [["feral"], ["feral"], ["feral"]]
    _test_validity(TEST_CANDIDATES, test_guesses, test_answers, expected_results)


def test_coyly():
    test_guesses = ["tares", "mould", "punji", "gowfs", "holly"]
    test_answers = ["coyly", "coyly", "coyly", "coyly", "coyly"]

    expected_results = [["coyly"], ["coyly"], ["coyly"], ["coyly"], ["coyly"]]

    _test_validity(TEST_CANDIDATES, test_guesses, test_answers, expected_results)


def _test_validity(candidates: list[str], guesses: list[str], answers: list[str] | list[GuessResult], expected_answers: list[list[str]]):
    solve_status = SolveStatusNp()
    word_reducer = WordReducer(candidates, solve_status)

    for guess, answer, expected_as in zip(guesses, answers, expected_answers):
        if isinstance(answer, list):
            res = answer
        else:
            res = _get_guess_res(guess, answer)
        solve_status.update(np.array(convert_word(guess)), to_res_arr(guess, res))
        word_reducer.update()

        actual_candidates = word_reducer._words_stack[-1]

        assert sorted(actual_candidates.tolist()) == sorted(expected_as)
        candidates = actual_candidates


def _get_guess_res(guess: str, ans: str):
    char_counts = Counter(ans)
    ret = []
    
    for g_c, r_c in zip(guess, ans):
        if g_c == r_c:
            char_counts[g_c] -= 1
            if char_counts[g_c] == 0:
                del char_counts[g_c]

    for g_c, r_c in zip(guess, ans):
        if g_c == r_c:
            ret.append(SingleResult.GREEN)
        elif g_c in char_counts:
            ret.append(SingleResult.YELLOW)
            char_counts[g_c] -= 1
            if char_counts[g_c] == 0:
                del char_counts[g_c]
        else:
            ret.append(SingleResult.GRAY)

    return ret
