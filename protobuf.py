#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct

# Base classes.
# ------------------------------------------------------------------------------

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
        '''
        Dumps the value to the .write()-like object.
        '''
        raise TypeError('Define in a derived class.')
        
    def load(self, fp):
        '''
        Loads the value from the .read()-like object.
        '''
        raise TypeError('Define in a derived class.')
        
    def pre_validate(self):
        '''
        Called before the value will be dumped.
        '''
        pass
        
    def post_validate(self):
        '''
        Called after the value was loaded.
        '''
        pass
    
class PrimitiveValue(Value):
    '''
    Represents a primitive value.
    '''

    def get_value(self):
        '''
        Gets the underlying value.
        '''
        return self._value
        
    def set_value(self, value):
        '''
        Sets the underlying value.
        '''
        self._value = value
    
    def push_value(self, value):
        '''
        Pushes the underlying value. Primitive value cannot be pushed twice.
        '''
        if self.is_set():
            raise ValueError('Primitive value cannot be pushed twice.')
        return self.set_value(value)
        
    def is_set(self):
        '''
        Gets whether the value is set.
        '''
        return not self._value is None
  
# Varint.
# ------------------------------------------------------------------------------
    
def VarintType():
    '''
    Creates a new Varint value instance.
    '''
    return VarintValue()

class VarintValue(PrimitiveValue):
    '''
    Represents a Varint value.
    '''
    
    WIRE_TYPE = 0
    
    def __init__(self, value=None):
        self.set_value(value)
    
    def dump_value(self, fp, value):
        '''
        Dumps the value to .write()-like object.
        '''
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
        '''
        Loads the value from .read()-like object and returns it.
        '''
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
        if not isinstance(value, int) and not isinstance(value, long):
            raise TypeError('Should be int or long.')
        elif value < 0:
            raise ValueError('Should be non-negative.')

# Signed Varint.
# ------------------------------------------------------------------------------

def SignedVarintType():
    '''
    Creates a new instance of signed Varint type.
    '''
    return SignedVarintValue()

class SignedVarintValue(VarintValue):
    '''
    Represents a signed Varint value.
    '''
    
    def __init__(self, value=None):
        self.set_value(value)
    
    def pre_validate(self):
        value = self.get_value()
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
# ------------------------------------------------------------------------------

def Fixed32Type():
    '''
    Creates a new instance of sfixed32 type.
    '''
    return Fixed32Value()

class Fixed32Value(PrimitiveValue):
    '''
    Represents a signed fixed32 value.
    '''
    
    WIRE_TYPE = 5
    
    def __init__(self, value=None):
        self.set_value(value)
        
    def pre_validate(self):
        value = self.get_value()
        if len(value) != 4:
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
    '''
    Creates an instance of signed int32 type.
    '''
    return Int32Value()
    
class Int32Value(Fixed32Value):
    
    def __init__(self, value=None):
        self.set_value(value)
        
    def dump(self, fp):
        self.dump_value(fp, struct.pack('>i', self.get_value()))
        
    def load(self, fp):
        self.set_value(struct.unpack('>i', self.load_value(fp))[0])
        
    def pre_validate(self):
        value = self.get_value()
        if not isinstance(value, int) and not isinstance(value, long):
            raise ValueError('Must be int or long.')

def UInt32Type():
    '''
    Creates an instance of unsigned int32 type.
    '''
    return UInt32Value()
    
class UInt32Value(Fixed32Value):
    '''
    Represents an unsigned int32 value.
    '''
    
    def __init__(self, value=None):
        self.set_value(value)
        
    def dump(self, fp):
        self.dump_value(fp, struct.pack('>I', self.get_value()))
        
    def load(self, fp):
        self.set_value(struct.unpack('>I', self.load_value(fp))[0])
        
    def pre_validate(self):
        value = self.get_value()
        if not isinstance(value, int) and not isinstance(value, long):
            raise ValueError('Must be int or long.')
        if value < 0:
            raise ValueError('Unsigned value must be non-negative.')

def Float32Type():
    '''
    Creates an instance of float32 type.
    '''
    return Float32Value()

class Float32Value(Fixed32Value):
    '''
    Represents an float32 value type.
    '''
    
    def __init__(self, value=None):
        self.set_value(value)
        
    def dump(self, fp):
        self.dump_value(fp, struct.pack('>f', self.get_value()))
        
    def load(self, fp):
        self.set_value(struct.unpack('>f', self.load_value(fp))[0])
        
    def pre_validate(self):
        if not isinstance(self.get_value(), float):
            raise ValueError('Must be float.')

# Fixed64.
# ------------------------------------------------------------------------------

def Fixed64Type():
    '''
    Creates an instance of fixed64 value.
    '''
    return Fixed64Value()

class Fixed64Value(PrimitiveValue):
    '''
    Represents a fixed64 value.
    '''
    
    WIRE_TYPE = 1
    
    def __init__(self, value=None):
        self.set_value(value)
        
    def pre_validate(self):
        value = self.get_value()
        if len(value) != 8:
            raise ValueError('Length must be 8.')
            
    def dump(self, fp):
        fp.write(self.get_value())
        
    def load(self, fb):
        self.set_value(fp.read(8))

def Int64Type():
    '''
    Creates an instance of signed int64 type.
    '''
    return Int64Value()
    
class Int64Value(Fixed64Value):
    '''
    Represents a signed int64 value.
    '''
    
    def __init__(self, value=None):
        self.set_value(value)
        
    def dump(self, fp):
        self.dump_value(fp, struct.pack('>q', self.get_value()))
        
    def load(self, fp):
        self.set_value(struct.unpack('>q', self.load_value(fp))[0])
        
    def pre_validate(self):
        value = self.get_value()
        if not isinstance(value, int) and not isinstance(value, long):
            raise ValueError('Must be int or long.')

def UInt64Type():
    '''
    Creates an instance of unsigned int64 type.
    '''
    return UInt64Value()
    
class UInt64Value(Fixed64Value):
    '''
    Represents an unsigned int64 value.
    '''
    
    def __init__(self, value=None):
        self.set_value(value)
        
    def dump(self, fp):
        self.dump_value(fp, struct.pack('>Q', self.get_value()))
        
    def load(self, fp):
        self.set_value(struct.unpack('>Q', self.load_value(fp))[0])
        
    def pre_validate(self):
        value = self.get_value()
        if not isinstance(value, int) and not isinstance(value, long):
            raise ValueError('Must be int or long.')
        if value < 0:
            raise ValueError('Unsigned value must be non-negative.')

def Float64Type():
    '''
    Creates an instance of float64 type.
    '''
    return Float64Value()

class Float64Value(Fixed64Value):
    '''
    Represents a float64 value.
    '''
    
    def __init__(self, value=None):
        self.set_value(value)
        
    def dump(self, fp):
        self.dump_value(fp, struct.pack('>d', self.get_value()))
        
    def load(self, fp):
        self.set_value(struct.unpack('>d', self.load_value(fp))[0])
        
    def pre_validate(self):
        if not isinstance(self.get_value(), float):
            raise ValueError('Must be float.')

# Bytes.
# ------------------------------------------------------------------------------

def BytesType():
    '''
    Creates a new instance of raw bytes type.
    '''
    return BytesValue()
    
class BytesValue(PrimitiveValue):
    '''
    Represents a bytes-value.
    '''
    
    WIRE_TYPE = 2
    
    def __init__(self, value=None):
        self.set_value(value)
        
    def dump(self, fp):
        self.dump_value(fp, self.get_value())
        
    def load(self, fp):
        self.set_value(self.load_value(fp))
        
    def pre_validate(self):
        if not isinstance(self.get_value(), str):
            raise TypeError('Value should be of str type.')
        
    def dump_value(self, fp, value):
        length_value = VarintValue(len(value))
        length_value.dump(fp)
        fp.write(value)
        
    def load_value(self, fp):
        length_value = VarintValue()
        length_value.load(fp)
        return fp.read(length_value.get_value())

# Strings.
# ------------------------------------------------------------------------------

def StringType():
    '''
    Creates a new instance of string value.
    '''
    return StringValue()

class StringValue(BytesValue):
    '''
    Represents a string value.
    '''
    
    def __init__(self, value=None):
        self.set_value(value)
        
    def dump(self, fp):
        self.dump_value(fp, self.get_value().encode('utf-8'))
        
    def load(self, fp):
        self.set_value(self.load_value(fp).decode('utf-8'))
        
    def pre_validate(self):
        if not isinstance(self.get_value(), str):
            raise TypeError('Value should be of str type.')

# Message.
# ------------------------------------------------------------------------------

class MessageType(ValueType):
    '''
    Represents a message type.
    '''
    
    def __init__(self, *fields):
        '''
        Constructs a new message type with the specified fields. The parameter
        should be an iterable of tuples (field_name, field_type).
        '''
        self._fields = fields
        
    def __call__(self):
        '''
        Creates an instance of the message type.
        '''
        return MessageInstance(*self._fields)

class MessageInstance(Value):
    '''
    Represents a message instance.
    '''
    
    WIRE_TYPE = 2
    
    def __init__(self, *fields):
        '''
        Initializes a new instance.
        '''
        self._field_names = tuple(field[0] for field in fields)
        self._field_types = dict(fields)
        self._field_values = dict((field_name, field_type()) for field_name, field_type in fields)
    
    def __getitem__(self, field_name):
        '''
        Gets the value of the field.
        '''
        return self._field_values[field_name].get_value()
        
    def __setitem__(self, field_name, field_value):
        '''
        Sets the value of the field.
        '''
        self._field_values[field_name].set_value(field_value)
        return field_value
        
    def __delitem__(self, field_name):
        '''
        Deletes the value of the field. Actually, sets it to None.
        '''
        self._field_values[field_name].set_value(None)
        
    def dump(self, fp):
        self.pre_validate()
        field_number = 1
        for field_name in self._field_names:
            value = self._field_values[field_name]
            key = VarintValue((field_number << 3) | value.WIRE_TYPE)
            key.dump(fp)
            value.dump(fp)
            field_number += 1
        
    def load(self, fp):
        pass
        
    def pre_validate(self):
        for field_name, field_value in self._field_values.iteritems():
            if field_value.is_set():
                field_value.pre_validate()
        
    def post_validate(self):
        for field_name, field_value in self._field_values.iteritems():
            if field_value.is_set():
                field_value.post_validate()
            
    def keys(self):
        return self._field_names
        
    def iterkeys(self):
        return iter(self._field_names)

