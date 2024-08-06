from pytest import fixture
from typing import Optional

from wordle_solver.analyzer.scorer.scorer import get_results
from wordle_solver.common.single_result import SingleResult
from wordle_solver.common.solve_status.solve_status import SolveStatus
from wordle_solver.common.trie import Trie



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


def _test_validity(candidates: list[str], guesses: list[str], answers: list[str] | list[list[SingleResult]], expected_answers: list[list[str]], solve_status: Optional[SolveStatus] = None):
    if solve_status is None:
        solve_status = SolveStatus()

    for guess, answer, expected_as in zip(guesses, answers, expected_answers):
        trie = Trie(candidates)
        if isinstance(answer, list):
            res = answer
        else:
            res = get_results(answer, guess)
        solve_status.add_results(guess, res)

        actual_candidates = trie.get_words(solve_status)

        assert sorted(actual_candidates) == sorted(expected_as)
