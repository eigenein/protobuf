"""
`pure-protobuf` contributors © 2011-2022
"""

import dataclasses
from typing import Any, Tuple

from pytest import mark, raises

from pure_protobuf.oneof import OneOf_, OneOfPartInfo


@dataclasses.dataclass(frozen=True)
class ComplexObj:
    a: int
    b: float
    c: complex
    d: bool


def create_one_of_pair(scheme: Tuple[OneOfPartInfo, ...], field_name: str,
                       value1: Any, value2: Any) -> Tuple[OneOf_, OneOf_]:
    oneof_value1 = OneOf_(*scheme)
    oneof_value2 = OneOf_(*scheme)

    setattr(oneof_value1, field_name, value1)
    setattr(oneof_value2, field_name, value2)
    return oneof_value1, oneof_value2


@mark.parametrize('field_name, value1, value2', [
    ('abc', "foo", "foo"),
    ('foo', 5, 5),
    ('f1', ComplexObj(1, 1., 1j, True), ComplexObj(1, 1., 1j, True))
])
def test_one_of_field_eq_hash(field_name: str, value1: Any, value2: Any):
    parts = (
        OneOfPartInfo('abc', str, 5),
        OneOfPartInfo('foo', int, 10),
        OneOfPartInfo('f1', ComplexObj, 11)
    )
    oneof_value1, oneof_value2 = create_one_of_pair(parts, field_name, value1, value2)

    assert oneof_value1 == oneof_value2
    assert hash(oneof_value1) == hash(oneof_value2)


@mark.parametrize('field_name, value1, value2', [
    ('abc', "foo", "abudu"),
    ('foo', 5, -1),
    ('f1', ComplexObj(1, 1., 1j, True), ComplexObj(2, 2., 2j, False))
])
def test_one_of_field_not_eq_hash(field_name: str, value1: Any, value2: Any):
    parts = (
        OneOfPartInfo('abc', str, 5),
        OneOfPartInfo('foo', int, 10),
        OneOfPartInfo('f1', ComplexObj, 10)
    )
    oneof_value1, oneof_value2 = create_one_of_pair(parts, field_name, value1, value2)

    assert oneof_value1 != oneof_value2
    assert hash(oneof_value1) != hash(oneof_value2)


def test_hash_doesnt_work_with_unhashable_type():
    @dataclasses.dataclass
    class ComplexObj:
        a: int
        b: float

    with raises(TypeError):
        one_of_value = OneOf_(OneOfPartInfo('complex', ComplexObj, 1))
        one_of_value.complex = ComplexObj(a=5, b=1.)
        hash(one_of_value)
