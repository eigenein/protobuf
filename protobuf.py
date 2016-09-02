#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Implements the Google's protobuf encoding.

eigenein (c) 2011-2016
'''

import cStringIO
import struct
import marshal

# Types. -----------------------------------------------------------------------

class Type:
    '''
    Represents a general field type.
    '''
    
    def dump(self, fp, value):
        '''
        Dumps its value to write-like object.
        '''
        raise TypeError('Don\'t call this directly.')
    
    def load(self, fp):
        '''
        Loads its value from read-like object and returns a read value.
        '''
        raise TypeError('Don\'t call this directly.')
    
    def dumps(self, value):
        '''
        Dumps its value to string and returns this string.
        '''
        fp = cStringIO.StringIO()
        self.dump(fp, value)
        return fp.getvalue()
    
    def loads(self, s):
        '''
        Loads its value from a string and returns a read value.
        '''
        return self.load(cStringIO.StringIO(s))
        
    def __hash__(self):
        '''
        Returns a hash of this type.
        '''
        return hash(self.__class__.__name__)
        
class UVarintType(Type):
    '''
    Represents an unsigned Varint type.
    '''

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
    '''
    Represents a signed Varint type. Implements ZigZag encoding.
    '''
    
    def dump(self, fp, value):
        encoded_varint = abs(value) << 1
        if value < 0:
            encoded_varint -= 1
        UVarintType.dump(self, fp, encoded_varint)
        
    def load(self, fp):
        encoded_varint = UVarintType.load(self, fp) + 1
        div = encoded_varint >> 1
        return div if encoded_varint & 1 else -div
      
class BoolType(UVarintType):
    '''
    Represents a boolean type. Encodes True as UVarint 1, and False as UVarint 0.
    '''

    dump = lambda self, fp, value: fp.write('\x01' if value else '\x00') # Similarly to UVarint.
    
    load = lambda self, fp: UVarintType.load(self, fp) != 0
        
class BytesType(Type):
    '''
    Represents a raw bytes type.
    '''
    
    WIRE_TYPE = 2
    
    def dump(self, fp, value):
        UVarint.dump(fp, len(value))
        fp.write(value)
        
    def load(self, fp):
        return fp.read(UVarint.load(fp))

class UnicodeType(BytesType):

    dump = lambda self, fp, value: BytesType.dump(self, fp, value.encode('utf-8'))

    load = lambda self, fp: unicode(BytesType.load(self, fp), 'utf-8')

class FixedLengthType(Type):
    '''
    Represents a general fixed-length value type. You should not use this type
    directly. Use derived types instead.
    '''

    dump = lambda self, fp, value: fp.write(value)
        
    load = lambda self, fp: fp.read(self.length())

class Fixed64Type(FixedLengthType):
    '''
    Represents a general 64-bit value type.
    '''
        
    WIRE_TYPE = 1
    
    length = lambda self: 8

class Fixed32Type(FixedLengthType):
    '''
    Represents a general 32-bit value type.
    '''

    WIRE_TYPE = 5

    length = lambda self: 4

class Fixed64SubType(Fixed64Type):
    '''
    Represents a general pickle'able 64-bit value type.
    '''

    dump = lambda self, fp, value: Fixed64Type.dump(self, fp, struct.pack(self.format, value))
        
    load = lambda self, fp: struct.unpack(self.format, Fixed64Type.load(self, fp))[0]
        
class UInt64Type(Fixed64SubType):
    '''
    Represents an unsigned int64 type.
    '''
    
    format = '>Q'

class Int64Type(Fixed64SubType):
    '''
    Represents a signed int64 type.
    '''
    
    format = '>q'
        
class Float64Type(Fixed64SubType):
    '''
    Represents a double precision floating point type.
    '''

    format = 'd'

class Fixed32SubType(Fixed32Type):
    '''
    Represents a pickle'able 32-bit value.
    '''

    dump = lambda self, fp, value: Fixed32Type.dump(self, fp, struct.pack(self.format, value))
 
    load = lambda self, fp: struct.unpack(self.format, Fixed32Type.load(self, fp))[0]
        
class UInt32Type(Fixed32SubType):
    '''
    Represents an unsigned int32 type.
    '''
    
    format = '>I'

class Int32Type(Fixed32SubType):
    '''
    Represents a signed int32 type.
    '''
    
    format = '>i'
        
class Float32Type(Fixed32SubType):
    '''
    Represents a single precision floating point type.
    '''

    format = 'f'

# Types instances. -------------------------------------------------------------
# You should actually use these types instances when defining your message type.

UVarint = UVarintType()
Varint = VarintType()
Bool = BoolType()
Fixed64 = Fixed64Type()
UInt64 = UInt64Type()
Int64 = Int64Type()
Float64 = Float64Type()
Fixed32 = Fixed32Type()
UInt32 = UInt32Type()
Int32 = Int32Type()
Float32 = Float32Type()
Bytes = BytesType()
Unicode = UnicodeType()

# Messages. --------------------------------------------------------------------

class Flags:
    '''
    Flags for a field.
    '''

    SIMPLE = 0 # Single value field.
    REQUIRED, REQUIRED_MASK = 1, 1 # Required field_type.
    SINGLE, REPEATED, PACKED_REPEATED, REPEATED_MASK = 0, 2, 6, 6 # Repeated and packed-repeated fields.
    PRIMITIVE, EMBEDDED, EMBEDDED_MASK = 0, 8, 8 # Used by MessageMetaType to determine if a field contains embedded definition.

class EofWrapper:
    '''
    Wraps a stream to raise EOFError instead of just returning of ''.
    '''
    def __init__(self, fp, limit=None):
        self.__fp = fp
        self.__limit = limit
        
    def read(self, size=None):
        '''
        Reads a string. Raises EOFError on end of stream.
        '''
        if size == 0:
            return ''
        if self.__limit is not None:
            size = min(size, self.__limit)
            self.__limit -= size
        s = self.__fp.read(size)
        if len(s) == 0:
            raise EOFError()
        return s

def _pack_key(tag, wire_type):
    '''
    Packs a tag and a wire_type into single int according to the protobuf spec.
    '''
    return (tag << 3) | wire_type
    
def _unpack_key(key):
    '''
    Unpacks a key into a tag and a wire_type according to the protobuf spec.
    '''
    return key >> 3, key & 7

# This used to correctly determine the length of unknown tags when loading a message.
_wire_type_to_type_instance = {0: Varint, 1: Fixed64, 2: Bytes, 5: Fixed32}

class MessageType(Type):
    '''
    Represents a message type.
    '''

    def __init__(self):
        '''
        Creates a new message type.
        '''
        self.__tags_to_types = dict() # Maps a tag to a type instance.
        self.__tags_to_names = dict() # Maps a tag to a given field name.
        self.__flags = dict() # Maps a tag to flags.

    def __hash__(self):
        _hash = 17
        for tag, name, field_type, flags in iter(self):
            _hash = hash((_hash, tag, field_type, flags))
        return _hash

    def __iter__(self):
        '''
        Iterates over all fields.
        '''
        for tag, name in self.__tags_to_names.iteritems():
            yield (tag, name, self.__tags_to_types[tag], self.__flags[tag])

    def add_field(self, tag, name, field_type, flags=Flags.SIMPLE):
        '''
        Adds a field to the message type.
        '''
        if tag in self.__tags_to_names or tag in self.__tags_to_types:
            raise ValueError('The tag %s is already used.' % tag)
        self.__tags_to_names[tag] = name
        self.__tags_to_types[tag] = field_type
        self.__flags[tag] = flags
        return self # Allow add_field chaining.

    def remove_field(self, tag):
        '''
        Removes a field by its tag. Doesn't raise any exception when the tag is
        missing.
        '''
        if tag in self.__tags_to_names:
            del self.__tags_to_names[tag]
        if tag in self.__tags_to_types:
            del self.__tags_to_types[tag]

    def __call__(self):
        '''
        Creates an instance of this message type.
        '''
        return Message(self)

    def __has_flag(self, tag, flag, mask):
        '''
        Checks whether the field with the specified tag has the specified flag.
        '''
        return (self.__flags[tag] & mask) == flag

    def dump(self, fp, value):
        if self != value.message_type:
            raise TypeError('Attempting to dump an object with type that\'s different from mine.')
        for tag, field_type in self.__tags_to_types.iteritems():
            if self.__tags_to_names[tag] in value:
                if self.__has_flag(tag, Flags.SINGLE, Flags.REPEATED_MASK):
                    # Single value.
                    UVarint.dump(fp, _pack_key(tag, field_type.WIRE_TYPE))
                    field_type.dump(fp, value[self.__tags_to_names[tag]])
                elif self.__has_flag(tag, Flags.PACKED_REPEATED, Flags.REPEATED_MASK):
                    # Repeated packed value.
                    UVarint.dump(fp, _pack_key(tag, Bytes.WIRE_TYPE))
                    internal_fp = cStringIO.StringIO()
                    for single_value in value[self.__tags_to_names[tag]]:
                        field_type.dump(internal_fp, single_value)
                    Bytes.dump(fp, internal_fp.getvalue())
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
        fp, message = EofWrapper(fp), self.__call__() # Wrap fp and create a new instance.
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
                    elif wire_type != Bytes.WIRE_TYPE:
                        raise TypeError('Tag %s has wiretype %s while the field is packed repeated.' % (tag, wire_type))
                    if self.__has_flag(tag, Flags.SINGLE, Flags.REPEATED_MASK):
                        # Single value.
                        message[self.__tags_to_names[tag]] = field_type.load(fp)
                    elif self.__has_flag(tag, Flags.PACKED_REPEATED, Flags.REPEATED_MASK):
                        # Repeated packed value.
                        repeated_value = message[self.__tags_to_names[tag]] = list()
                        internal_fp = EofWrapper(fp, UVarint.load(fp)) # Limit with value length.
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
                    # Skip this field.
                    _wire_type_to_type_instance[wire_type].load(fp)
            except EOFError:
                # Check if all required fields are present.
                for tag, name in self.__tags_to_names.iteritems():
                    if self.__has_flag(tag, Flags.REQUIRED, Flags.REQUIRED_MASK) and not name in message:
                        if self.__has_flag(tag, Flags.REPEATED, Flags.REPEATED_MASK):
                            message[name] = list() # Empty list (no values was in input stream). But required field.
                        else:
                            raise ValueError('The field with the tag %s (\'%s\') is required but a value is missing.' % (tag, name))
                return message

class Message(dict):
    '''
    Represents a message instance.
    '''

    def __init__(self, message_type):
        '''
        Initializes a new instance of the specified message type.
        '''
        self.__dict__['message_type'] = message_type
        
    def __getattr__(self, name):
        '''
        Gets a value of the specified message field.
        '''
        return self.__getitem__(name)
        
    def __setattr__(self, name, value):
        '''
        Sets a value of the specified message field.
        '''
        (self.__dict__ if name in self.__dict__ else self).__setitem__(name, value)
        return value
    
    def __delattr__(self, name):
        '''
        Removes a value of the specified message field.
        '''
        (self.__dict__ if name in self.__dict__ else self).__delitem__(name, value)
        
    def dumps(self):
        '''
        Dumps the message into a string.
        '''
        return self.message_type.dumps(self)
    
    def dump(self, fp):
        '''
        Dumps the message into a write-like object.
        '''
        return self.message_type.dump(fp, self)   

def loads(self, s, message_type):
    '''
    Loads a message of the specified message type from the string.
    '''
    return message_type.loads(s)
    
def load(self, fp, message_type):
    '''
    Loads a message of the specified message type from the read-like object.
    '''
    return message_type.load(fp)

# Embedded message. ------------------------------------------------------------

class EmbeddedMessage(Type):
    '''
    Represents an embedded message type.
    '''
    
    WIRE_TYPE = 2
    
    def __init__(self, message_type):
        '''
        Initializes a new instance. The argument is an underlying message type.
        '''
        self.message_type = message_type
    
    def __call__(self):
        '''
        Creates a message of the underlying message type.
        '''
        return self.message_type()
    
    def dump(self, fp, value):
        Bytes.dump(fp, self.message_type.dumps(value))
        
    def load(self, fp):
        return self.message_type.load(EofWrapper(fp, UVarint.load(fp))) # Limit with embedded message length.

# Describing messages themselves. ----------------------------------------------

class TypeMetadataType(Type):

    WIRE_TYPE = 2

    def __init__(self):
        # Field description.
        self.__field_metadata_type = MessageType()
        self.__field_metadata_type.add_field(1, 'tag', UVarint, flags=Flags.REQUIRED)
        self.__field_metadata_type.add_field(2, 'name', Bytes, flags=Flags.REQUIRED)
        self.__field_metadata_type.add_field(3, 'type', Bytes, flags=Flags.REQUIRED)
        self.__field_metadata_type.add_field(4, 'flags', UVarint, flags=Flags.REQUIRED)
        self.__field_metadata_type.add_field(5, 'embedded', EmbeddedMessage(self)) # Used to describe embedded messages.
        # Metadata message description.
        self.__self_type = EmbeddedMessage(MessageType())
        self.__self_type.message_type.add_field(1, 'fields', EmbeddedMessage(self.__field_metadata_type), flags=(Flags.REPEATED | Flags.REQUIRED))
    
    def __create_message(self, message_type):
        '''
        Creates a message that contains info about the message_type.
        '''
        message, message.fields = self.__self_type(), list()
        for field in iter(message_type):
            field_meta = self.__field_metadata_type()
            field_meta.tag, field_meta.name, field_type, field_meta.flags = field
            field_meta.type = type_str = field_type.__class__.__name__
            if isinstance(field_type, EmbeddedMessage):
                field_meta.flags |= Flags.EMBEDDED
                field_meta.embedded_metadata = self.__create_message(field_type.message_type)
            elif not type_str.endswith('Type'):
                raise TypeError('Type name of type singleton object should end with \'Type\'. Actual: \'%s\'.' % type_str)
            else:
                field_meta.type = type_str[:-4]
            message.fields.append(field_meta)
        return message
    
    def dump(self, fp, message_type):
        self.__self_type.dump(fp, self.__create_message(message_type))
        
    def __restore_type(self, message):
        '''
        Restores a message type by the information in the message.
        '''
        message_type, g = MessageType(), globals()
        for field in message.fields:
            field_type = field['type']
            if not field_type in g:
                raise TypeError('Primitive type \'%s\' not found in this protobuf module.' % field_type)
            field_info = (field.tag, field.name, g[field_type], field.flags)
            if field.flags & Flags.EMBEDDED_MASK == Flags.EMBEDDED:
                field_info[3] -= Flags.EMBEDDED
                field_info[2] = EmbeddedMessage(self.__restore_type(field.embedded))
            message_type.add_field(*field_info)
        return message_type
        
    def load(self, fp):
        return self.__restore_type(self.__self_type.load(fp))
    
TypeMetadata = TypeMetadataType() # Use this type to dump and load metatypes.

