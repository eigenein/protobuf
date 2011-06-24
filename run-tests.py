#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Runs unit tests.

eigenein (c) 2011
'''

import unittest
import types
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

class TestBytes(unittest.TestCase):

    def test_dumps_1(self):
        self.assertEqual(Bytes.dumps('testing'), '\x07\x74\x65\x73\x74\x69\x6e\x67')
        
    def test_loads_1(self):
        self.assertEqual(Bytes.loads('\x07\x74\x65\x73\x74\x69\x6e\x67'), 'testing')

class TestUnicode(unittest.TestCase):

    def test_dumps_1(self):
        self.assertEqual(Unicode.dumps(u'Привет'), '\x0c\xd0\x9f\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82')
        
    def test_loads_1(self):
        self.assertEqual(Unicode.loads('\x0c\xd0\x9f\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82'), u'Привет')

class TestMarshalableCode(unittest.TestCase):

    def test_dumps_and_loads(self):
        def func():
            return 42
        code = MarshalableCode.loads(MarshalableCode.dumps(func.func_code))
        f = types.FunctionType(code, globals())
        self.assertEqual(f(), 42)

class TestMessageType(unittest.TestCase):

    def test_dumps_1(self):
        Test2 = MessageType()
        Test2.add_field(2, 'b', Bytes)
        msg = Test2()
        msg.b = 'testing'
        self.assertEqual(msg.dumps(), '\x12\x07\x74\x65\x73\x74\x69\x6e\x67')

    def test_dumps_2(self):
        '''
        Tests missing optional value.
        '''
        Test2 = MessageType()
        Test2.add_field(2, 'b', Bytes)
        msg = Test2()
        self.assertEqual(msg.dumps(), '')
        
    def test_dumps_3(self):
        '''
        Tests missing required value.
        '''
        Test2 = MessageType()
        Test2.add_field(2, 'b', Bytes, flags=Flags.REQUIRED)
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
        Test2.add_field(2, 'b', Bytes)
        msg = Test2.loads('')
        self.assertNotIn('b', msg)
    
    def test_loads_1_1(self):
        '''
        Tests missing required value.
        '''
        Test2 = MessageType()
        Test2.add_field(2, 'b', Bytes, flags=Flags.REQUIRED)
        with self.assertRaises(ValueError):
            Test2.loads('')
    
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
    
    def test_hash_1(self):
        '''
        Tests __hash__.
        '''
        Type1, Type2, Type3, Type4 = MessageType(), MessageType(), MessageType(), MessageType()
        Type1.add_field(1, 'b', UVarint)
        Type2.add_field(1, 'a', UVarint)
        Type3.add_field(2, 'a', UVarint)
        Type4.add_field(1, 'b', UVarint, flags=Flags.REPEATED)
        self.assertEquals(hash(Type1), hash(Type2))
        self.assertNotEquals(hash(Type1), hash(Type3))
        self.assertNotEquals(hash(Type1), hash(Type4))
        
    def test_iter_1(self):
        '''
        Tests __iter__.
        '''
        Type1 = MessageType()
        Type1.add_field(1, 'b', UVarint, flags=Flags.REPEATED)
        Type1.add_field(2, 'c', Bytes, flags=Flags.PACKED_REPEATED)
        i = iter(Type1)
        self.assertEqual(i.next(), (1, 'b', UVarint, Flags.REPEATED))
        self.assertEqual(i.next(), (2, 'c', Bytes, Flags.PACKED_REPEATED))

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
    
    def test_dumps_and_loads(self):
        '''
        Tests that boundaries of embedded messages are properly read.
        '''
        Type1, Type2 = MessageType(), MessageType()
        Type2.add_field(1, 'a', UVarint)
        Type1.add_field(1, 'a', UVarint)
        Type1.add_field(2, 'b', EmbeddedMessage(Type2))
        Type1.add_field(3, 'c', UVarint)
        msg = Type1()
        msg.a = 1
        msg.c = 3
        msg.b = Type2()
        msg.b.a = 2
        msg = Type1.loads(msg.dumps())
        self.assertEqual(msg.a, 1)
        self.assertEqual(msg.c, 3)
        self.assertEqual(msg.b.a, 2)
    
    def test_loads_1(self):
        Test1 = MessageType()
        Test1.add_field(1, 'a', UVarint)
        Test3 = MessageType()
        Test3.add_field(3, 'c', EmbeddedMessage(Test1))
        msg = Test3.loads('\x1a\x03\x08\x96\x01')
        self.assertIn('c', msg)
        self.assertIn('a', msg.c)
        self.assertEqual(msg.c.a, 150)

class TestTypeMetadata(unittest.TestCase):
    
    def test_dumps_1(self):
        '''
        Simple test.
        '''
        Test2 = MessageType()
        Test2.add_field(2, 'b', Bytes)
        Type1 = MessageType()
        Type1.add_field(1, 't', TypeMetadata)
        msg = Type1()
        msg.t = Test2
        self.assertEqual(msg.dumps(), '\n\n\x0e\x08\x02\x12\x01b\x1a\x05Bytes \x00')

if __name__ == '__main__':
    unittest.main()

