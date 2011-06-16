#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cStringIO
import struct

# Message instance. ------------------------------------------------------------

class Message(dict):

    def __init__(self, message_type):
        self.message_type = message_type

# Types. -----------------------------------------------------------------------

class Type:
    
    def dump(self, fp, value):
        raise TypeError('Don\'t call this directly.')
    
    def load(self, fp):
        raise TypeError('Don\'t call this directly.')
    
    def dumps(self, value):
        fp = cStringIO.StringIO()
        self.dump(fp, value)
        return fp.getvalue()
    
    def loads(self, s):
        return self.load(cStringIO.StringIO(s))
    
    def validate(self, value):
        pass
        
class UVarintType(Type):

    def dump(self, fp, value):
        shifted_value = True
        while shifted_value:
            shifted_value = value >> 7
            fp.write(chr((value & 0x7F) | (0x80 if shifted_value != 0 else 0x00)))
            value = shifted_value
        
    def load(self, fp):
        value, shift, quantum = 0, 0, 0x80
        while (quantum & 0x80) == 0x80:
            quantum = ord(fp.read(1))
            value, shift = value + ((quantum & 0x7F) << shift), shift + 7
        return value
        
class VarintType(UVarintType):
    
    def dump(self, fp, value):
        UVarintType.dump(self, fp, abs(value) * 2 - (1 if value < 0 else 0))
        
    def load(self, fp):
        div, mod = divmod(UVarintType.load(self, fp) + 1, 2)
        return -div if mod == 0 else div
      
class BoolType(UVarintType):

    def dump(self, fp, value):
        UVarintType.dump(self, fp, int(value))
    
    def load(self, fp):
        return bool(UVarintType.load(self, fp))
        
class StringType(Type):
    
    def dump(self, fp, value):
        UVarint.dump(fp, len(value))
        fp.write(value)
        
    def load(self, fp):
        length = UVarint.load(fp)
        return fp.read(length)

class FixedLengthType(Type):

    def dump(self, fp, value):
        fp.write(value)
        
    def load(self, fp):
        return fp.read(self.length())

class Fixed64Type(FixedLengthType):
    
    def length(self):
        return 8

class Fixed32Type(FixedLengthType):

    def length(self):
        return 4

class Fixed64SubType(Fixed64Type):

    def dump(self, fp, value):
        Fixed64Type.dump(self, fp, struct.pack(self._format(), value))
        
    def load(self, fp):
        return struct.unpack(self._format(), Fixed64Type.load(self, fp))[0]
        
class UInt64Type(Fixed64SubType):
    
    def _format(self):
        return '>Q'

class Int64Type(Fixed64SubType):
    
    def _format(self):
        return '>q'
        
class Float64Type(Fixed64SubType):

    def _format(self):
        return 'd'

class Fixed32SubType(Fixed32Type):

    def dump(self, fp, value):
        Fixed32Type.dump(self, fp, struct.pack(self._format(), value))
        
    def load(self, fp):
        return struct.unpack(self._format(), Fixed32Type.load(self, fp))[0]

class UInt32Type(Fixed32SubType):
    
    def _format(self):
        return '>I'

class Int32Type(Fixed32SubType):
    
    def _format(self):
        return '>i'
        
class Float32Type(Fixed32SubType):

    def _format(self):
        return 'f'

class MessageType(Type): # TODO

    def __init__(self):
        pass # TODO

    def __call__(self):
        return Message(self) # TODO Update message with defaults.

    def dump(self, fp, value):
        pass
        
    def load(self, fp):
        pass # load the message
        pass # validate?
        return message
    
    def validate(self, value):
        pass
        
    def validate_fields_values(self, message):
        pass # call validate on each field?
        
    def validate_structure(self, message):
        pass # check all required fields are filled?

class EmbeddedMessage():
    
    def __init__(self, message_type):
        self.message_type = message_type
    
    def dump(self, fp, value):
        String.dump(fp, self.message_type.dumps(value))
        
    def load(self, fp):
        return self.message_type.loads(String.load(fp))
    
    def validate(self, value):
        self.message_type.validate(value)

# Types instances. -------------------------------------------------------------

UVarint = UVarintType()
Varint = VarintType()
Bool = BoolType()
Fixed64 = Fixed64Type()
UInt64 = UInt64Type()
Int64 = Int64Type()
Float64 = Float64Type()
Fixed32 = Fixed32Type()
UInt32 = UInt32Type()
Int32Type = Int32Type()
Float32 = Float32Type()
String = StringType()

