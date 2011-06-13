#!/usr/bin/env python
# -*- coding: utf-8 -*-

class ValueType:
    '''
    Base class for any value type.
    '''
    
    def __call__(self):
        raise TypeError('Use a derived class.')
   
class Value:
    '''
    Base class for any value.
    '''

    def get_value(self):
        raise TypeError('Use a derived class.')
        
    def set_value(self, value):
        raise TypeError('Use a derived class.')
    
    def put_value(self, value):
        return self.set_value(value)
    
    def dump(self, fp):
        raise TypeError('Use a derived class.')
        
    def load(self, fp):
        raise TypeError('Use a derived class.')
        
    def validate(self):
        raise TypeError('Use a derived class.')
    
def VarintType():
    return VarintValue()

class VarintValue(Value):
    '''
    Represents a Varint value.
    '''
    
    def __init__(self, value=0):
        self._value = value
    
    def get_value(self):
        return self._value
        
    def set_value(self, value):
        self._value = value
    
    def dump(self, fp):
        value = self._value
        if value == 0:
            fp.write('\x00')
        elif not isinstance(value, int) and not isinstance(value, long):
            raise TypeError('Should be int or long.')
        elif value < 0:
            raise ValueError('Should be non-negative.')
        else:
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
        self._value = value

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
        field_number = 1
        for field_name in self._field_names:
            key = VarintValue((field_number << 3) | _WIRE_TYPES[self._field_types[field_name]])
            key.dump(fp)
            self._field_values[field_name].dump(fp)
            field_number += 1
        
    def load(self, fp):
        pass
        
    def validate(self):
        for field_name, field_value in self._values:
            field_value.validate()

_WIRE_TYPES = {
    VarintType: 0,
    MessageType: 2
}

