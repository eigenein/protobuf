# `pure-protobuf`

My own implementation of [Google](http://www.google.com)'s [Protocol Buffers](http://code.google.com/apis/protocolbuffers/docs/encoding.html).

[![Build Status](https://travis-ci.org/eigenein/protobuf.svg?branch=master)](https://travis-ci.org/eigenein/protobuf)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pure-protobuf.svg)](https://pypi.org/project/pure-protobuf/)
[![PyPI – Version](https://img.shields.io/pypi/v/pure-protobuf.svg)](https://pypi.org/project/pure-protobuf/#history)
[![PyPI – Python](https://img.shields.io/pypi/pyversions/pure-protobuf.svg)](https://pypi.org/project/pure-protobuf/#files)
![License](https://img.shields.io/pypi/l/pure-protobuf.svg)

## Usage

Assume you have the following definition:

```proto
message Test2 {
  string b = 2;
}
```
    
First, you should create the message type:

```python
from pure_protobuf.protobuf import MessageType, Unicode

Test2 = MessageType()
Test2.add_field(2, 'b', Unicode)
```
    
Then, create a message and fill it with the appropriate data:

```python
msg = Test2()
msg.b = 'testing'
```
    
You can dump this now!

```python
print msg.dumps() # This will dump into a string.
msg.dump(open('/tmp/message', 'wb')) # And this will dump into any write-like object.
```
    
You also can load this message with:

```python
msg = Test2.load(open('/tmp/message', 'rb'))
```

or with:

```python
msg = load(open('/tmp/message', 'rb'), Test2)
```
    
Simple enough. :)

### Sample 2. Required field

To add a missing field you should pass an additional `flags` parameter to `add_field` like this:

```python
Test2 = MessageType()
Test2.add_field(2, 'b', String, flags=Flags.REQUIRED)
```
    
If you'll not fill a required field, then ValueError will be raised during serialization.

### Sample 3. Repeated field

Do like this:

```python
Test2 = MessageType()
Test2.add_field(1, 'b', UVarint, flags=Flags.REPEATED)
msg = Test2()
msg.b = (1, 2, 3)
```
    
A value of repeated field can be any iterable object. The loaded value will always be `list`.

### Sample 4. Packed repeated field

```python
Test4 = MessageType()
Test4.add_field(4, 'd', UVarint, flags=Flags.PACKED_REPEATED)
msg = Test4()
msg.d = (3, 270, 86942)
```
    
### Sample 5. Embedded messages

Consider the following definitions:

```proto
message Test1 {
  int32 a = 1;
}
```
    
and

```proto
message Test3 {
  required Test1 c = 3;
}
```
    
To create an embedded field, pass `EmbeddedMessage` as the type of field and fill it like this:

```python
# Create the type.
Test1 = MessageType()
Test1.add_field(1, 'a', UVarint)
Test3 = MessageType()
Test3.add_field(3, 'c', EmbeddedMessage(Test1))

# Fill in the message.
msg = Test3()
msg.c = Test1()
msg.c.a = 150
```
    
## Data types

There are the following data types supported for now:

    UVarint             # Unsigned integer.
    Varint              # Signed integer.
    Bool                # Boolean.
    Fixed64             # 8-byte string.
    UInt64              # C++'s 64-bit `unsigned long long`
    Int64               # C++'s 64-bit `long long`
    Float64             # C++'s `double`.
    Fixed32             # 4-byte string.
    UInt32              # C++'s 32-bit `unsigned int`.
    Int32               # C++'s 32-bit `int`.
    Float32             # C++'s `float`.
    Bytes               # Pure bytes string.
    Unicode             # Unicode string.
    TypeMetadata        # Type that describes another type.

## Some techniques

### Streaming messages

The Protocol Buffers format is not self delimiting. But you can wrap you message type in `EmbeddedMessage` class and write/read it sequentially.

The other option is to use `protobuf.EofWrapper` that has a `limit` parameter in its constructor. The `EofWrapper` raises `EOFError` when the specified number of bytes is read.

### Self-describing messages and `TypeMetadata`

There is no any description of the message type in a message itself. Therefore, if you want to send a self-described messages, you should send the a description of the message too.

I've implemented a tool for this... Look:

```python
A, B, C = MessageType(), MessageType(), MessageType()
A.add_field(1, 'a', UVarint)
A.add_field(2, 'b', TypeMetadata, flags=Flags.REPEATED)     # <- Look here!
A.add_field(3, 'c', Bytes)
B.add_field(4, 'ololo', Float32)
B.add_field(5, 'c', TypeMetadata, flags=Flags.REPEATED)     # <- And here!
B.add_field(6, 'd', Bool, flags=Flags.PACKED_REPEATED)
C.add_field(7, 'ghjhdf', UVarint)
msg = A()
msg.a = 1
msg.b = [B, C]                                              # Assigning of types.
msg.c = 'ololo'
bytes = msg.dumps()
# ...
msg = A.loads(bytes)
msg2 = msg.b[0]()                                           # Creating a message of the loaded type.
```

You can send your `bytes` anywhere and you'll got your message type on the other side!

### `add_field` chaining

`add_field` return the message type itself, thus you can do so:

```python
MessageType().add_field(1, 'a', EmbeddedMessage(MessageType().add_field(1, 'a', UVarint)))
