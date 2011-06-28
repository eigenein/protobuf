#!/usr/bin/env python
# -*- coding: utf-8 -*-

import timeit
from protobuf import *

tests = list()
test_cases = dict()
number = 100000

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
        for args, kwargs in test_cases[target]:
            args_str = ', '.join(repr(arg) for arg in args)
            kwargs_str = ', '.join('%s=%s' % (k, repr(v)) for k, v in kwargs.iteritems())
            allargs_str = args_str
            allargs_str += ', ' + kwargs_str if len(args_str) > 0 and len(kwargs_str) > 0 else kwargs_str
            stmt = '%s(%s)' % (target, allargs_str)
            print '\033[95mTest: %s\033[0m' % title
            print '%s: \033[92m%.4fs\033[0m' % (stmt.ljust(70), min(timeit.repeat(stmt, 'from __main__ import %s' % target, number=number)))
        print '\033[94m%s\033[0m' % '-' * 80
        
# Fake output. -----------------------------------------------------------------

class FakeOutput:
    
    def write(self, s):
        pass

fp = FakeOutput()      

# Tests themselves. ------------------------------------------------------------

@test('UVarint dump')
@testcase(1)
@testcase(0x7FFFFFFF)
@testcase(12345678901234567890L)
def test_uvarint_dump(value):
    UVarint.dump(fp, value)

# Main. ------------------------------------------------------------------------

if __name__ == '__main__':
    print
    try:
        runtests()
    except KeyboardInterrupt:
        print
        print '\033[91mInterrupted.\033[0m'
        print
    else:
        print 
        print '\033[92mDone.\033[0m'
        print

