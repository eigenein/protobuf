#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct

class ValueType:
    '''
    Base class for any value type.
    '''
    
    def __call__(self):
        raise TypeError('Define in a derived class.')
   
class Value:
    '''
    Base class for any value.
    '''
    
    def dump(self, fp):
        raise TypeError('Define in a derived class.')
        
    def load(self, fp):
        raise TypeError('Define in a derived class.')
        
    def pre_validate(self):
        pass
        
    def post_validate(self):
        pass
    
class PrimitiveValue(Value):

    def get_value(self):
        return self._value
        
    def set_value(self, value):
        self._value = value
    
    def push_value(self, value):
        return self.set_value(value)
    
def VarintType():
    return VarintValue()

class VarintValue(PrimitiveValue):
    '''
    Represents a Varint value.
    '''
    
    def __init__(self, value=0):
        self.set_value(value)
    
    def dump(self, fp):
        value = self.get_value()
        if value == 0:
            fp.write('\x00')
        elif not value is None:
            while value != 0:
                new_value = value >> 7
                fp.write(chr(value & 0x7F | (0x80 if new_value != 0 else 0x00)))
                value = new_value
    
    def load(self, fp):
        value = shift = 0
        while True:
            code = ord(fp.read(1))
            value += (code & 0x7F) << shift
            if code & 0x80 == 0:
                break
            shift += 7
        self.set_value(value)
        
    def pre_validate(self):
        value = self.get_value()
        if not value is None:
            if not isinstance(value, int) and not isinstance(value, long):
                raise TypeError('Should be int or long.')
            elif value < 0:
                raise ValueError('Should be non-negative.')

def Fixed32ValueType():
    return Fixed32Value()

class Fixed32Value(PrimitiveValue):
    
    def __init__(self, value='\x00\x00\x00\x00'):
        self.set_value(value)
        
    def pre_validate(self):
        value = self.get_value()
        if not value is None or len(value) != 4:
            raise ValueError('Length must be 4.')
        
    def dump_value(self, fp, value):
        fp.write(value)
            
    def dump(self, fp):
        self.dump_value(fp, self.get_value())
    
    def load_value(self, fp):
        return fp.read(4)
    
    def load(self, fp):
        self.set_value(self.load_value(fp))

def Int32ValueType():
    return Int32Value()
    
class Int32Value(Fixed32Value):
    
    def __init__(self, value=0):
        self.set_value(value)
        
    def dump(self, fp):
        self.dump_value(fp, struct.pack('>i', self.get_value()))
        
    def load(self, fp):
        self.set_value(struct.unpack('>i', self.load_value(fp))[0])
        
    def pre_validate(self):
        value = self.get_value()
        if not isinstance(value, int) and not isinstance(value, long):
            raise ValueError('Must be int or long.')

def Fixed64ValueType():
    return Fixed64Value()

class Fixed64Value(PrimitiveValue):
    
    def __init__(self, value='\x00\x00\x00\x00\x00\x00\x00\x00'):
        self.set_value(value)
        
    def pre_validate(self):
        value = self.get_value()
        if not value is None or len(value) != 8:
            raise ValueError('Length must be 8.')
            
    def dump(self, fp):
        fp.write(self.get_value())
        
    def load(self, fb):
        self.set_value(fp.read(8))

class MessageType(ValueType):
    '''
    Represents a message type.
    '''
    
    def __init__(self, *fields):
        self._fields = fields
        
    def __call__(self):
        return MessageValue(*self._fields)

class MessageValue(Value):
    '''
    Represents a message value.
    '''
    
    def __init__(self, *fields):
        self._field_names = tuple(field[0] for field in fields)
        self._field_types = dict(fields)
        self._field_values = dict((field_name, field_type()) for field_name, field_type in fields)
    
    def __getitem__(self, field_name):
        return self._field_values[field_name].get_value()
        
    def __setitem__(self, field_name, field_value):
        self._field_values[field_name].set_value(field_value)
        return field_value
        
    def dump(self, fp):
        self.pre_validate()
        field_number = 1
        for field_name in self._field_names:
            key = VarintValue((field_number << 3) | _WIRE_TYPES[self._field_types[field_name]])
            key.dump(fp)
            self._field_values[field_name].dump(fp)
            field_number += 1
        
    def load(self, fp):
        pass
        
    def pre_validate(self):
        for field_name, field_value in self._field_values.iteritems():
            field_value.pre_validate()
        
    def post_validate(self):
        for field_name, field_value in self._field_values.iteritems():
            field_value.post_validate()

_WIRE_TYPES = {
    VarintType: 0,
    Fixed64ValueType: 1,
    MessageType: 2,
    Fixed32ValueType: 5
}

