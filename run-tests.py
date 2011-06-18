#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Runs unit tests.

eigenein (c) 2011
'''

import unittest
from encoding import *
from remoting import *

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

class TestMessageType(unittest.TestCase):

    def test_dumps_1(self):
        Test2 = MessageType()
        Test2.add_field(2, 'b', String)
        msg = Test2()
        msg.b = 'testing'
        self.assertEqual(msg.dumps(), '\x12\x07\x74\x65\x73\x74\x69\x6e\x67')

    def test_dumps_2(self):
        '''
        Tests missing optional value.
        '''
        Test2 = MessageType()
        Test2.add_field(2, 'b', String)
        msg = Test2()
        self.assertEqual(msg.dumps(), '')
        
    def test_dumps_3(self):
        '''
        Tests missing required value.
        '''
        Test2 = MessageType()
        Test2.add_field(2, 'b', String, flags=Flags.REQUIRED)
        msg = Test2()
        with self.assertRaises(ValueError):
            msg.dumps()

    def test_dumps_4(self):
        '''
        Tests repeated value.
        '''
        Test2 = MessageType()
        Test2.add_field(1, 'b', UVarint, flags=Flags.REPEATED)
        msg = Test2()
        msg.b = (1, 2, 3)
        self.assertEqual(msg.dumps(), '\x08\x01\x08\x02\x08\x03')
        
    def test_dumps_5(self):
        '''
        Tests packed repeated value.
        '''
        Test4 = MessageType()
        Test4.add_field(4, 'd', UVarint, flags=Flags.PACKED_REPEATED)
        msg = Test4()
        msg.d = (3, 270, 86942)
        self.assertEqual(msg.dumps(), '\x22\x06\x03\x8E\x02\x9E\xA7\x05')

    def test_loads_1(self):
        '''
        Tests missing optional value.
        '''
        Test2 = MessageType()
        Test2.add_field(2, 'b', String)
        msg = Test2.loads('')
        self.assertNotIn('b', msg)
    
    def test_loads_2(self):
        '''
        Tests that the last value in the input stream is assigned to
        a non-repeated field.
        '''
        Test2 = MessageType()
        Test2.add_field(1, 'b', UVarint)
        msg = Test2.loads('\x08\x01\x08\x02\x08\x03')
        self.assertEquals(msg.b, 3)
    
    def test_loads_3(self):
        '''
        Tests repeated value.
        '''
        Test2 = MessageType()
        Test2.add_field(1, 'b', UVarint, flags=Flags.REPEATED)
        msg = Test2.loads('\x08\x01\x08\x02\x08\x03')
        self.assertIn('b', msg)
        self.assertEquals(msg.b, [1, 2, 3])
        
    def test_loads_4(self):
        '''
        Tests packed repeated value.
        '''
        Test4 = MessageType()
        Test4.add_field(4, 'd', UVarint, flags=Flags.PACKED_REPEATED)
        msg = Test4.loads('\x22\x06\x03\x8E\x02\x9E\xA7\x05')
        self.assertIn('d', msg)
        self.assertEquals(msg.d, [3, 270, 86942])

class TestEmbeddedMessage(unittest.TestCase):

    def test_dumps_1(self):
        '''
        Tests general dumps.
        '''
        Test1 = MessageType()
        Test1.add_field(1, 'a', UVarint)
        Test3 = MessageType()
        Test3.add_field(3, 'c', EmbeddedMessage(Test1))
        msg = Test3()
        msg.c = Test1()
        msg.c.a = 150
        self.assertEqual(msg.dumps(), '\x1a\x03\x08\x96\x01')
        
    def test_loads_1(self):
        Test1 = MessageType()
        Test1.add_field(1, 'a', UVarint)
        Test3 = MessageType()
        Test3.add_field(3, 'c', EmbeddedMessage(Test1))
        msg = Test3.loads('\x1a\x03\x08\x96\x01')
        self.assertIn('c', msg)
        self.assertIn('a', msg.c)
        self.assertEqual(msg.c.a, 150)

if __name__ == '__main__':
    unittest.main()

