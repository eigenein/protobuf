"""
`pure-protobuf` contributors © 2011-2022
"""

import dataclasses
from typing import Any, List, Tuple

from pytest import mark, raises

from pure_protobuf.dataclasses_ import field, message, one_of, part
from pure_protobuf.oneof import OneOf_, OneOfPartInfo
from pure_protobuf.types import int32


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


def test_which_one_of():
    parts = (
        OneOfPartInfo('abc', str, 5),
        OneOfPartInfo('foo', int, 10),
        OneOfPartInfo('f1', ComplexObj, 10),
        OneOfPartInfo('f2', List[int], 9)
    )
    values = (
        "foo",
        5,
        ComplexObj(1, 1., 1j, False),
        [1, 2, 3, 4, 5]
    )

    oneof_msg = OneOf_(*parts)

    for part_, val in zip(parts, values):
        setattr(oneof_msg, part_.name, val)

        assert oneof_msg.which_one_of == part_.name
        assert getattr(oneof_msg, oneof_msg.which_one_of) == val


def name_and_value(oneof_msg: OneOf_) -> Tuple[str, Any]:
    return oneof_msg.which_one_of, getattr(oneof_msg, oneof_msg.which_one_of)  # type: ignore


def test_usual_message_sets_work():
    parts = (
        OneOfPartInfo('abc', str, 5),
        OneOfPartInfo('foo', int, 10),
        OneOfPartInfo('f1', ComplexObj, 10),
        OneOfPartInfo('f2', List[int], 9)
    )
    oneof_msg = OneOf_(*parts)

    expected, expected_name = 5, 'foo'
    oneof_msg.foo = expected  # every set actually overrides
    field_name, val = name_and_value(oneof_msg)
    assert field_name == expected_name
    assert val == expected

    expected, expected_name = "aaa", 'abc'
    oneof_msg.abc = expected
    field_name, val = name_and_value(oneof_msg)
    assert field_name == expected_name
    assert val == expected

    expected, expected_name = ComplexObj(1, 1., 1j, True), 'f1'
    oneof_msg.f1 = expected
    field_name, val = name_and_value(oneof_msg)
    assert field_name == expected_name
    assert val == expected

    expected, expected_name = [1, 2, 3, 4], 'f2'
    oneof_msg.f2 = expected
    field_name, val = name_and_value(oneof_msg)
    assert field_name == expected_name
    assert val == expected


@message
@dataclasses.dataclass
class SomeObj:
    a: int32 = field(1)
    b: str = field(2)


@message
@dataclasses.dataclass
class Example:
    usual_value: int32 = field(3)
    another_one: str = field(4)

    oneof_msg: OneOf_ = one_of(
        abc=part(str, 5),
        foo=part(int32, 10),
        f1=part(SomeObj, 7),
        f2=part(List[int32], 9)
    )


def hardcoded_which_one_of(oneof_msg: OneOf_):
    if oneof_msg.abc is not None:
        return "abc", oneof_msg.abc
    elif oneof_msg.foo is not None:
        return "foo", oneof_msg.foo
    elif oneof_msg.f1 is not None:
        return "f1", oneof_msg.f1
    elif oneof_msg.f2 is not None:
        return "f2", oneof_msg.f2


def class_assertions(expected_name: str, expected_val: Any, oneof_msg: OneOf_):
    field_name, val = name_and_value(oneof_msg)
    assert field_name == expected_name
    assert val == expected_val
    assert oneof_msg.which_one_of == expected_name

    _r_name, _r_val = hardcoded_which_one_of(oneof_msg)
    assert _r_name == expected_name
    assert _r_val == expected_val


def test_class_sets_one_set():
    obj = Example(usual_value=5, another_one='111')

    # foo
    expected, expected_name = 5, 'foo'
    obj.oneof_msg.foo = expected  # every set actually overrides previous value
    class_assertions(expected_name, expected, obj.oneof_msg)

    # abc
    expected, expected_name = "aaa", 'abc'
    obj.oneof_msg.abc = expected
    class_assertions(expected_name, expected, obj.oneof_msg)

    # f1
    expected, expected_name = SomeObj(1, "aaa"), 'f1'
    obj.oneof_msg.f1 = expected
    class_assertions(expected_name, expected, obj.oneof_msg)

    # f2
    expected, expected_name = [1, 2, 3, 4], 'f2'
    obj.oneof_msg.f2 = expected
    class_assertions(expected_name, expected, obj.oneof_msg)

    # unset
    del obj.oneof_msg.f2
    assert obj.oneof_msg.f2 is None
    assert obj.oneof_msg.which_one_of is None

    with raises(AttributeError):
        # trying to delete unset method
        del obj.oneof_msg.f1
