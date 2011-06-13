#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct

# Base classes.

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
        
    def is_set(self):
        return not self._value is None
  
# Varint.
    
def VarintType():
    return VarintValue()

class VarintValue(PrimitiveValue):
    '''
    Represents a Varint value.
    '''
    
    def __init__(self, value=0):
        self.set_value(value)
    
    def dump_value(self, fp, value):
        if value == 0:
            fp.write('\x00')
        elif not value is None:
            while value != 0:
                new_value = value >> 7
                fp.write(chr(value & 0x7F | (0x80 if new_value != 0 else 0x00)))
                value = new_value
    
    def dump(self, fp):
        self.dump_value(fp, self.get_value())
    
    def load_value(self, fp):
        value = shift = 0
        while True:
            code = ord(fp.read(1))
            value += (code & 0x7F) << shift
            if code & 0x80 == 0:
                return value
            shift += 7
       
    def load(self, fp):
        self.set_value(self.load_value(fp))
        
    def pre_validate(self):
        value = self.get_value()
        if self.is_set():
            if not isinstance(value, int) and not isinstance(value, long):
                raise TypeError('Should be int or long.')
            elif value < 0:
                raise ValueError('Should be non-negative.')

# Signed Varint.

def SignedVarintType():
    return SignedVarintValue()

class SignedVarintValue(VarintValue):
    
    def __init__(self, value=0):
        self.set_value(value)
    
    def pre_validate(self):
        value = self.get_value()
        if self.is_set():
            if not isinstance(value, int) and not isinstance(value, long):
                raise TypeError('Should be int or long.')

    def dump(self, fp):
        value = abs(self.get_value())
        converted = value + value
        if self.get_value() < 0:
            converted -= 1
        self.dump_value(fp, converted)
        
    def load(self, fp):
        converted = self.load_value(fp)
        value, sign = divmod(converted + 1, 2)
        if sign == 0:
            value = -value
        self.set_value(value)

# Fixed32.

def Fixed32Type():
    return Fixed32Value()

class Fixed32Value(PrimitiveValue):
    
    def __init__(self, value='\x00\x00\x00\x00'):
        self.set_value(value)
        
    def pre_validate(self):
        value = self.get_value()
        if self.is_set() and len(value) != 4:
            raise ValueError('Length must be 4.')
        
    def dump_value(self, fp, value):
        fp.write(value)
            
    def dump(self, fp):
        self.dump_value(fp, self.get_value())
    
    def load_value(self, fp):
        return fp.read(4)
    
    def load(self, fp):
        self.set_value(self.load_value(fp))

def Int32Type():
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
        if self.is_set():
            if not isinstance(value, int) and not isinstance(value, long):
                raise ValueError('Must be int or long.')

def UInt32Type():
    return UInt32Value()
    
class UInt32Value(Fixed32Value):
    
    def __init__(self, value=0):
        self.set_value(value)
        
    def dump(self, fp):
        self.dump_value(fp, struct.pack('>I', self.get_value()))
        
    def load(self, fp):
        self.set_value(struct.unpack('>I', self.load_value(fp))[0])
        
    def pre_validate(self):
        value = self.get_value()
        if self.is_set():
            if not isinstance(value, int) and not isinstance(value, long):
                raise ValueError('Must be int or long.')
            if value < 0:
                raise ValueError('Unsigned value must be non-negative.')

def Float32Type():
    return Float32Value()

class Float32Value(Fixed32Value):
    
    def __init__(self, value=0.0):
        self.set_value(value)
        
    def dump(self, fp):
        self.dump_value(fp, struct.pack('>f', self.get_value()))
        
    def load(self, fp):
        self.set_value(struct.unpack('>f', self.load_value(fp))[0])
        
    def pre_validate(self):
        if self.is_set():
            if not isinstance(self.get_value(), float):
                raise ValueError('Must be float.')

# Fixed64.

def Fixed64Type():
    return Fixed64Value()

class Fixed64Value(PrimitiveValue):
    
    def __init__(self, value='\x00\x00\x00\x00\x00\x00\x00\x00'):
        self.set_value(value)
        
    def pre_validate(self):
        value = self.get_value()
        if self.is_set() and len(value) != 8:
            raise ValueError('Length must be 8.')
            
    def dump(self, fp):
        fp.write(self.get_value())
        
    def load(self, fb):
        self.set_value(fp.read(8))

def Int64Type():
    return Int64Value()
    
class Int64Value(Fixed64Value):
    
    def __init__(self, value=0):
        self.set_value(value)
        
    def dump(self, fp):
        self.dump_value(fp, struct.pack('>q', self.get_value()))
        
    def load(self, fp):
        self.set_value(struct.unpack('>q', self.load_value(fp))[0])
        
    def pre_validate(self):
        value = self.get_value()
        if self.is_set():
            if not isinstance(value, int) and not isinstance(value, long):
                raise ValueError('Must be int or long.')

def UInt64Type():
    return UInt64Value()
    
class UInt64Value(Fixed64Value):
    
    def __init__(self, value=0):
        self.set_value(value)
        
    def dump(self, fp):
        self.dump_value(fp, struct.pack('>Q', self.get_value()))
        
    def load(self, fp):
        self.set_value(struct.unpack('>Q', self.load_value(fp))[0])
        
    def pre_validate(self):
        value = self.get_value()
        if self.is_set():
            if not isinstance(value, int) and not isinstance(value, long):
                raise ValueError('Must be int or long.')
            if value < 0:
                raise ValueError('Unsigned value must be non-negative.')

def Float64Type():
    return Float64Value()

class Float64Value(Fixed64Value):
    
    def __init__(self, value=0.0):
        self.set_value(value)
        
    def dump(self, fp):
        self.dump_value(fp, struct.pack('>d', self.get_value()))
        
    def load(self, fp):
        self.set_value(struct.unpack('>d', self.load_value(fp))[0])
        
    def pre_validate(self):
        if self.is_set():
            if not isinstance(self.get_value(), float):
                raise ValueError('Must be float.')

# Message.

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
    Fixed64Type: 1,
    Int64Type: 1,
    UInt64Type: 1,
    Float64Type: 1,
    MessageType: 2,
    Fixed32Type: 5,
    Int32Type: 5,
    UInt32Type: 5,
    Float32Type: 5
}

