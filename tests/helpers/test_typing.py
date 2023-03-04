from typing import Any, Iterable, List, Optional, Union

from pytest import mark

from pure_protobuf.helpers._typing import extract_optional, extract_repeated


@mark.parametrize(
    ("hint", "expected_flag", "expected_inner"),
    [
        (int, False, int),
        (Optional[int], True, int),
        (Union[str, None, int], True, Union[str, int]),
    ],
)
def test_extract_optional(hint: Any, expected_flag: bool, expected_inner: Any) -> None:
    assert extract_optional(hint) == (expected_inner, expected_flag)


@mark.parametrize(
    ("hint", "expected_flag", "expected_inner"),
    [
        (int, False, int),
        (List[int], True, int),
        (Iterable[int], True, int),
    ],
)
def test_extract_repeated(hint: Any, expected_flag: bool, expected_inner: Any) -> None:
    assert extract_repeated(hint) == (expected_inner, expected_flag)
