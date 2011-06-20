protobuf
========

#### Changes in v0.3 (next)

-   README techniques added.
-   Hashes of message types.
-   Fixed: loading of missing required field doesn't raise `ValueError`.

#### Changes in v0.2

-   Fixed `Int32` type name (was `Int32Type`).
-   Added validation of message type.
-   Unicode type.
-   Python code object type.
-   Fixed casting values to bool and from bool.

My own implementation of [Google](http://www.google.com)'s [Protocol Buffers](http://code.google.com/apis/protocolbuffers/docs/encoding.html).

What and why
------------

I've written this just4fun, thus all questions like "What's the goal?" have no any sense.

Fow now, there is full protobuf encoding implementation, so you can use the `encoding` module with full compatibility with the standard implementation.

The `encoding` module is covered with unit tests, but you should understand that there are may be some unknown bugs. **Thus, use this software at your own risk.**

Using
-----

Do `from encoding import *` and you're ready to go.

Note: all names of message types are similar to described [there](http://code.google.com/apis/protocolbuffers/docs/encoding.html). ;-)

### Sample 1. Simple

Assume you have the following definition:

    message Test2 {
      string b = 2;
    }
    
First, you should create the message type:

    Test2 = MessageType()
    Test2.add_field(2, 'b', String)
    
Then, create a message and fill it with the appropriate data:

    msg = Test2()
    msg.b = 'testing'
    
You can dump this now!

    print msg.dumps() # This will dump into a string.
    msg.dump(open('/tmp/message', 'wb')) # And this will dump into any write-like object.
    
You also can load this message with:

    msg = Test2.load(open('/tmp/message', 'rb'))

or with:

    msg = load(open('/tmp/message', 'rb'), Test2)
    
Simple enough. :)

### Sample 2. Required field

To add a missing field you should pass an additional `flags` parameter to `add_field` like this:

    Test2 = MessageType()
    Test2.add_field(2, 'b', String, flags=Flags.REQUIRED)
    
If you'll not fill a required field, then ValueError will be raised during serialization.

### Sample 3. Repeated field

Do like this:

    Test2 = MessageType()
    Test2.add_field(1, 'b', UVarint, flags=Flags.REPEATED)
    msg = Test2()
    msg.b = (1, 2, 3)
    
A value of repeated field can be any iterable object. The loaded value will always be `list`.

### Sample 4. Packed repeated field

    Test4 = MessageType()
    Test4.add_field(4, 'd', UVarint, flags=Flags.PACKED_REPEATED)
    msg = Test4()
    msg.d = (3, 270, 86942)
    
### Sample 5. Embedded messages

Consider the following definitions:

    message Test1 {
      int32 a = 1;
    }
    
and
    
    message Test3 {
      required Test1 c = 3;
    }
    
To create an embedded field, pass EmbeddedMessage as the type of field and fill it like this:

    # Create the type.
    Test1 = MessageType()
    Test1.add_field(1, 'a', UVarint)
    Test3 = MessageType()
    Test3.add_field(3, 'c', EmbeddedMessage(Test1))
    # Fill the message.
    msg = Test3()
    msg.c = Test1()
    msg.c.a = 150
    
Data types
----------

There are the following data types supported for now:

    UVarint
    Varint
    Bool
    Fixed64         # 8-byte string.
    UInt64
    Int64
    Float64
    Fixed32         # 4-byte string.
    UInt32
    Int32
    Float32
    Bytes           # Pure bytes string.
    Unicode         # Unicode string.
    MarshalableCode # Python code object. Serialized with marshal module.

Some techniques
---------------

### Streaming messages

There Protocol Buffer format is not self delimiting. But you can use wrap you message type in `EmbeddedMessage` class and write/read it sequentially.

More info
---------

See `encoding` to see the API and `run-tests` modules to see more usage samples.
    
