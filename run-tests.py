#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from encoding import *

class TestUVarint(unittest.TestCase):

    def test_dumps_1(self):
        self.assertEqual(UVarint.dumps(0), '\x00')
        
    def test_dumps_2(self):
        self.assertEqual(UVarint.dumps(3), '\x03')
        
    def test_dumps_3(self):
        self.assertEqual(UVarint.dumps(270), '\x8E\x02')
        
    def test_dumps_4(self):
        self.assertEqual(UVarint.dumps(86942), '\x9E\xA7\x05')
        
    def test_loads_1(self):
        self.assertEqual(UVarint.loads('\x00'), 0)
    
    def test_loads_2(self):
        self.assertEqual(UVarint.loads('\x03'), 3)
        
    def test_loads_3(self):
        self.assertEqual(UVarint.loads('\x8E\x02'), 270)

    def test_loads_4(self):
        self.assertEqual(UVarint.loads('\x9E\xA7\x05'), 86942)

class TestVarint(unittest.TestCase):
    
    def test_dumps_1(self):
        self.assertEqual(Varint.dumps(0), '\x00')
    
    def test_dumps_2(self):
        self.assertEqual(Varint.dumps(-1), '\x01')
        
    def test_dumps_3(self):
        self.assertEqual(Varint.dumps(1), '\x02')
    
    def test_dumps_4(self):
        self.assertEqual(Varint.dumps(-2), '\x03')
        
    def test_loads_1(self):
        self.assertEqual(Varint.loads('\x00'), 0)
    
    def test_loads_2(self):
        self.assertEqual(Varint.loads('\x01'), -1)
        
    def test_loads_3(self):
        self.assertEqual(Varint.loads('\x02'), 1)
        
    def test_loads_4(self):
        self.assertEqual(Varint.loads('\x03'), -2)

class TestBool(unittest.TestCase):

    def test_dumps_1(self):
        self.assertEqual(Bool.dumps(True), '\x01')
        self.assertEqual(Bool.dumps(False), '\x00')
        
    def test_loads_1(self):
        self.assertEqual(Bool.loads('\x00'), False)
        self.assertEqual(Bool.loads('\x01'), True)

class TestUInt64(unittest.TestCase):

    def test_dumps_1(self):
        self.assertEqual(UInt64.dumps(1), '\x00\x00\x00\x00\x00\x00\x00\x01')
    
    def test_loads_1(self):
        self.assertEqual(UInt64.loads('\x00\x00\x00\x00\x00\x00\x00\x01'), 1)
        
class TestInt64(unittest.TestCase):

    def test_dumps_1(self):
        self.assertEqual(Int64.dumps(-2), '\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFE')
    
    def test_loads_1(self):
        self.assertEqual(Int64.loads('\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFE'), -2)

class TestString(unittest.TestCase):

    def test_dumps_1(self):
        self.assertEqual(String.dumps('testing'), '\x07\x74\x65\x73\x74\x69\x6e\x67')
        
    def test_loads_1(self):
        self.assertEqual(String.loads('\x07\x74\x65\x73\x74\x69\x6e\x67'), 'testing')

if __name__ == '__main__':
    unittest.main()

