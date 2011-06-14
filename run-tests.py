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

class TestMessageValue(unittest.TestCase):
        
    def test_dump(self):
        message_type = protobuf.MessageType(('a', protobuf.VarintType))
        message_value = message_type()
        message_value['a'] = 150
        fp = StringIO.StringIO()
        message_value.dump(fp)
        self.assertEqual(fp.getvalue(), '\x08\x96\x01')

# Run tests.
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

