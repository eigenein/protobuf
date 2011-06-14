#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import StringIO
import protobuf

# Mappings-like tests.
# ------------------------------------------------------------------------------

class TestCaseWithMappings(unittest.TestCase):

    def test_dump(self):
        if not hasattr(self, 'test_class'):
            return
        for k, v in self.mappings:
            s = StringIO.StringIO()
            clazz = self.test_class[0]
            value = clazz()
            value.set_value(k)
            value.dump(s)
            self.assertEqual(s.getvalue(), v)
    
    def test_load(self):
        if not hasattr(self, 'test_class'):
            return
        for k, v in self.mappings:
            s = StringIO.StringIO(v)
            clazz = self.test_class[0]
            value = clazz()
            value.load(s)
            self.assertEqual(value.get_value(), k)

class TestVarintValue(TestCaseWithMappings):

    def setUp(self):
        self.test_class = (protobuf.VarintType, )
        self.mappings = (
            (0, '\x00'),
            (3, '\x03'),
            (270, '\x8E\x02'),
            (86942, '\x9E\xA7\x05')
        )

class TestInt32Value(TestCaseWithMappings):

    def setUp(self):
        self.test_class = (protobuf.Int32Type, )
        self.mappings = (
            (0, '\x00\x00\x00\x00'),
            (3, '\x00\x00\x00\x03'),
            (0x76543210, '\x76\x54\x32\x10'),
            (-1, '\xFF\xFF\xFF\xFF')
        )

class TestSignedVarintValue(TestCaseWithMappings):

    def setUp(self):
        self.test_class = (protobuf.SignedVarintType, )
        self.mappings = (
            (0, '\x00'),
            (-1, '\x01'),
            (1, '\x02'),
            (-2, '\x03')
        )

class TestStringValue(unittest.TestCase):
    
    def setUp(self):
        self.test_class = (protobuf.StringType, )
        self.mappings = (
            ('testing', '\x07\x74\x65\x73\x74\x69\x6e\x67'),
        )

# Custom tests.
# ------------------------------------------------------------------------------

class TestMessageInstance(unittest.TestCase):
        
    def test_dump(self):
        message_type = protobuf.MessageType({'tag': 1, 'name': 'a', 'type': protobuf.VarintType})
        message_instance = message_type()
        message_instance['a'] = 150
        self.assertEqual(message_instance.dumps(), '\x08\x96\x01')

class TestMessageType(unittest.TestCase):

    def test_add_field(self):
        message_type = protobuf.MessageType()
        message_type.add_field(1, 'a', protobuf.VarintType, 666)
        message_type.add_field(2, 'b', protobuf.VarintType)
        self.assertTrue(message_type.has_field(1))
        v = message_type()
        self.assertEqual(v['a'], 666)
        self.assertEqual(v['b'], None)

class IntegrationTests(unittest.TestCase):

    def test_embedded_message(self):
        Test1 = protobuf.MessageType({'tag': 1, 'name': 'a', 'type': protobuf.VarintType})
        c = Test1()
        c['a'] = 150
        Test3 = protobuf.MessageType({'tag': 3, 'name': 'c', 'type': protobuf.EmbeddedMessageType(Test1)})
        message = Test3()
        message['c'] = c
        self.assertEqual(message.dumps(), '\x1a\x03\x08\x96\x01')

# Run tests.
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

