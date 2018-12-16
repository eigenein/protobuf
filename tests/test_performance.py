#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function
import timeit

import six

from pure_protobuf.protobuf import (
    Bool,
    EmbeddedMessage,
    MessageType,
    UVarint,
    Varint,
)

tests = list()
test_cases = dict()
number = 100000
repeat = 3


def test(title):
    def wrapper(target):
        tests.append((title, target.__name__))
        return target

    return wrapper


def testcase(*args, **kwargs):
    def wrapper(target):
        if target.__name__ in test_cases:
            test_cases[target.__name__].insert(0, (args, kwargs))
        else:
            test_cases[target.__name__] = [(args, kwargs)]
        return target

    return wrapper


def runtests():
    for title, target in tests:
        print('\033[95mTest: %s\033[0m' % title)
        for args, kwargs in test_cases[target]:
            args_str = ', '.join(repr(arg) for arg in args)
            kwargs_str = ', '.join(
                '%s=%s' % (k, repr(v)) for k, v in six.iteritems(kwargs)
            )
            allargs_str = args_str
            allargs_str += (
                ', ' + kwargs_str
                if len(args_str) > 0 and len(kwargs_str) > 0
                else kwargs_str
            )
            stmt = '%s(%s)' % (target, allargs_str)
            print(
                '%s: \033[92m%.4fs\033[0m'
                % (
                    stmt.ljust(70),
                    min(
                        timeit.repeat(
                            stmt,
                            'from __main__ import %s' % target,
                            repeat=repeat,
                            number=number,
                        )
                    ),
                )
            )
        print('\033[94m%s\033[0m' % '-' * 80)
        print()


# Fake output. ----------------------------------------------------------------


class FakeOutput:
    def write(self, s):
        pass


fp = FakeOutput()

# Tests themselves. -----------------------------------------------------------


@test('UVarint dump')
@testcase(1)
@testcase(0x7FFFFFFF)
@testcase(12345678901234567890)
def test_uvarint_dump(value):
    UVarint.dump(fp, value)


@test('UVarint loads')
@testcase('\x03')
@testcase('\x8E\x02')
@testcase('\x9E\xA7\x05')
def test_uvarint_loads(value):
    UVarint.loads(value)


@test('Varint dump')
@testcase(-1)
@testcase(-0x7FFFFFFE)
@testcase(-12345678901234567890)
def test_varint_dump(value):
    Varint.dump(fp, value)


@test('Varint loads')
@testcase('\x01')
@testcase('\x02')
@testcase('\x9E\xA7\x05')
def test_varint_loads(value):
    Varint.loads(value)


@test('Bool dump')
@testcase(False)
@testcase(True)
def test_bool_dump(value):
    Bool.dump(fp, value)


Type1 = MessageType().add_field(
    1, 'a', EmbeddedMessage(MessageType().add_field(1, 'a', UVarint))
)


@test('__hash__')
@testcase()
def test_hash():
    hash(Type1)


# Main. -----------------------------------------------------------------------

if __name__ == '__main__':
    print()
    try:
        print(
            '\033[95mRunning tests with repeat=%s, number=%s\033[0m'
            % (repeat, number)
        )
        print('\033[94m%s\033[0m' % '-' * 80)
        print()
        runtests()
    except KeyboardInterrupt:
        print()
        print('\033[91mInterrupted.\033[0m')
        print()
    else:
        print('\033[92mDone.\033[0m')
        print()
