from wordle_solver.analyzer.scorer.scorer import get_results
from wordle_solver.common.single_result import SingleResult


def test_get_results_basic():
    ans = 'abcde'
    guess = 'acdfe'

    expected_ans = (SingleResult.GREEN, SingleResult.YELLOW, SingleResult.YELLOW, SingleResult.GRAY, SingleResult.GREEN)
    actual_ans = get_results(ans, guess)

    assert actual_ans == expected_ans


def test_get_results_overcounted():
    ans = 'abcde'
    guess = 'cacaa'

    expected_ans = (SingleResult.GRAY, SingleResult.YELLOW, SingleResult.GREEN, SingleResult.GRAY, SingleResult.GRAY)
    actual_ans = get_results(ans, guess)

    assert actual_ans == expected_ans


def test_get_results_overcounted_green_and_yellow():
    ans = 'abcda'
    guess = 'xaaca'

    expected_ans = (SingleResult.GRAY, SingleResult.YELLOW, SingleResult.GRAY, SingleResult.YELLOW, SingleResult.GREEN)
    actual_ans = get_results(ans, guess)

    assert actual_ans == expected_ans
