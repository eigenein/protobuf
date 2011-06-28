#!/usr/bin/env python
# -*- coding: utf-8 -*-

import timeit

tests = list()
test_cases = dict()

def test(title):
    def wrapper(target):
        tests.append((title, target.__name__))
        return target
    return wrapper

def testcase(*args, **kwargs):
    def wrapper(target):
        if target.__name__ in test_cases:
            test_cases[target.__name__].append((args, kwargs))
        else:
            test_cases[target.__name__] = [(args, kwargs)]
        return target
    return wrapper
        
def runtests():
    for title, target in tests:
        if not target in test_cases:
            stmt = '%s()' % target
            print '%s: %ss' % (stmt, min(timeit.repeat(stmt, 'import protobuf; from __main__ import %s' % target)))
        else:
            for args, kwargs in test_cases[target]:
                args_str = ', '.join(str(arg) for arg in args)
                kwargs_str = ', '.join('%s=%s' % (k, v) for k, v in kwargs.iteritems())
                allargs_str = args_str
                allargs_str += ', ' + kwargs_str if len(args_str) > 0 and len(kwargs_str) > 0 else kwargs_str
                stmt = '%s(%s)' % (target, allargs_str)
                print '%s: %ss' % (stmt, min(timeit.repeat(stmt, 'import protobuf; from __main__ import %s' % target)))
        
# Tests themselves. ------------------------------------------------------------

@test('testtest')
@testcase()
def testtest():
    pass

# Main. ------------------------------------------------------------------------

if __name__ == '__main__':
    runtests()

