#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cStringIO
import struct

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
        
class UVarintType(Type):

    WIRE_TYPE = 0

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
    
    WIRE_TYPE = 2
    
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
    
    WIRE_TYPE = 1
    
    def length(self):
        return 8

class Fixed32Type(FixedLengthType):

    WIRE_TYPE = 5

    def length(self):
        return 4

class Fixed64SubType(Fixed64Type):

    def dump(self, fp, value):
        Fixed64Type.dump(self, fp, struct.pack(self.format, value))
        
    def load(self, fp):
        return struct.unpack(self.format, Fixed64Type.load(self, fp))[0]
        
class UInt64Type(Fixed64SubType):
    
    format = '>Q'

class Int64Type(Fixed64SubType):
    
    format = '>q'
        
class Float64Type(Fixed64SubType):

    format = 'd'

class Fixed32SubType(Fixed32Type):

    def dump(self, fp, value):
        Fixed32Type.dump(self, fp, struct.pack(self.format, value))
        
    def load(self, fp):
        return struct.unpack(self.format(), Fixed32Type.load(self, fp))[0]

class UInt32Type(Fixed32SubType):
    
    format = '>I'

class Int32Type(Fixed32SubType):
    
    format = '>i'
        
class Float32Type(Fixed32SubType):

    format = 'f'

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

# Messages. --------------------------------------------------------------------

class Flags:
    '''
    Flags for a field.
    '''

    SIMPLE = 0
    REQUIRED, REQUIRED_MASK = 1, 1
    SINGLE, REPEATED, PACKED_REPEATED, REPEATED_MASK = 0, 2, 6, 6

class _EofWrapper:
    '''
    Wraps a stream to raise EOFError instead of just returning of ''.
    '''
    def __init__(self, fp):
        self.__fp = fp
        
    def read(self, size=None):
        s = self.__fp.read(size)
        if len(s) == 0:
            raise EOFError()
        return s

def _pack_key(tag, wire_type):
    return (tag << 3) | wire_type
    
def _unpack_key(key):
    return key >> 3, key & 7

_wire_type_to_type_instance = {
    0: Varint,
    1: Fixed64,
    2: String,
    5: Fixed32
}

class MessageType(Type):

    def __init__(self):
        self.__tags_to_types = dict()
        self.__tags_to_names = dict()
        self.__flags = dict()
        self.__defaults = dict()

    def add_field(self, tag, name, field_type, default=None, flags=Flags.SIMPLE):
        if tag in self.__tags_to_names or tag in self.__tags_to_types:
            raise ValueError('The tag %s is already used.' % tag)
        self.__tags_to_names[tag] = name
        self.__tags_to_types[tag] = field_type
        self.__flags[tag] = flags
        if default is not None:
            self.__defaults[tag] = default

    def remove_field(self, tag):
        if tag in self.__tags_to_names:
            del self.__tags_to_names[tag]
        if tag in self.__tags_to_types:
            del self.__tags_to_types[tag]
        if tag in self.__defaults:
            del self.__defaults[tag]

    def __call__(self):
        return Message(self, self.__defaults)

    def __has_flag(self, tag, flag, mask):
        return (self.__flags[tag] & mask) == flag

    def dump(self, fp, value):
        for tag, field_type in self.__tags_to_types.iteritems():
            if self.__tags_to_names[tag] in value:
                if self.__has_flag(tag, Flags.SINGLE, Flags.REPEATED_MASK):
                    # Simple value.
                    UVarint.dump(fp, _pack_key(tag, field_type.WIRE_TYPE))
                    field_type.dump(fp, value[self.__tags_to_names[tag]])
                elif self.__has_flag(tag, Flags.PACKED_REPEATED, Flags.REPEATED_MASK):
                    # Repeated packed value.
                    UVarint.dump(fp, _pack_key(tag, String.WIRE_TYPE))
                    internal_fp = cStringIO.StringIO()
                    for single_value in value[self.__tags_to_names[tag]]:
                        field_type.dump(internal_fp, single_value)
                    String.dump(fp, internal_fp.getvalue())
                elif self.__has_flag(tag, Flags.REPEATED, Flags.REPEATED_MASK):
                    # Repeated value.
                    key = _pack_key(tag, field_type.WIRE_TYPE)
                    # Put it together sequently.
                    for single_value in value[self.__tags_to_names[tag]]:
                        UVarint.dump(fp, key)
                        field_type.dump(fp, single_value)
            elif self.__has_flag(tag, Flags.REQUIRED, Flags.REQUIRED_MASK):
                raise ValueError('The field with the tag %s is required but a value is missing.' % tag)
        
    def load(self, fp):
        fp, message = _EofWrapper(fp), self.__call__() # Wrap fp and create a new instance.
        while True:
            try:
                tag, wire_type = _unpack_key(UVarint.load(fp))
                if tag in self.__tags_to_types:
                    field_type = self.__tags_to_types[tag]
                    if not self.__has_flag(tag, Flags.PACKED_REPEATED, Flags.REPEATED_MASK):
                        if wire_type != field_type.WIRE_TYPE:
                            raise TypeError(
                                'The received value with the tag %s has incorrect wiretype: %s instead of %s expected.' % \
                                (tag, wire_type, field_type.WIRE_TYPE))
                    elif wire_type != String.WIRE_TYPE:
                        raise TypeError('Tag %s has wiretype %s while the field is packed repeated.' % tag)
                    if self.__has_flag(tag, Flags.SINGLE, Flags.REPEATED_MASK):
                        message[self.__tags_to_names[tag]] = field_type.load(fp)
                    elif self.__has_flag(tag, Flags.PACKED_REPEATED, Flags.REPEATED_MASK):
                        # Repeated packed value.
                        repeated_value = message[self.__tags_to_names[tag]] = list()
                        internal_fp = _EofWrapper(cStringIO.StringIO(String.load(fp)))
                        while True:
                            try:
                                repeated_value.append(field_type.load(internal_fp))
                            except EOFError:
                                break
                    elif self.__has_flag(tag, Flags.REPEATED, Flags.REPEATED_MASK):
                        # Repeated value.
                        if not self.__tags_to_names[tag] in message:
                            repeated_value = message[self.__tags_to_names[tag]] = list()
                        repeated_value.append(field_type.load(fp))
                else:
                    # Skip this.
                    _wire_type_to_type_instance[wire_type].load(fp)
            except EOFError:
                return message

class Message(dict):

    def __init__(self, message_type, defaults=dict()):
        self.message_type = message_type
        self.update(defaults)
        
    def __getattr__(self, name):
        return self.__getitem__(name)
        
    def __setattr__(self, name, value):
        (self.__dict__ if name in self.__dict__ else self).__setitem__(name, value)
        return value
    
    def __delattr__(self, name):
        (self.__dict__ if name in self.__dict__ else self).__delitem__(name, value)
        
    def dumps(self):
        return self.message_type.dumps(self)
    
    def dump(self, fp):
        return self.message_type.dump(self, value)   

def loads(self, s, message_type):
    return message_type.loads(s)
    
def load(self, fp, message_type):
    return message_type.load(fp)

# Embedded message. ------------------------------------------------------------

class EmbeddedMessage(Type):
    
    WIRE_TYPE = 2
    
    def __init__(self, message_type):
        self.message_type = message_type
    
    def dump(self, fp, value):
        String.dump(fp, self.message_type.dumps(value))
        
    def load(self, fp):
        return self.message_type.loads(String.load(fp))

