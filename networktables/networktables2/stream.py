import struct

__all__ = ["WriteStream", "ReadStream", "StreamEOF"]

_bool = struct.Struct('?')
_byte = struct.Struct('b')
_ubyte = struct.Struct('B')
_short = struct.Struct('>h')
_ushort = struct.Struct('>H')
_char = struct.Struct('>H')
_int = struct.Struct('>i')
_long = struct.Struct('>q')
_float = struct.Struct('>f')
_double = struct.Struct('>d')

class StreamEOF(IOError):
    pass

class WriteStream:
    """A Java-compatible stream writer."""
    def __init__(self, f):
        self.f = f

    def flush(self):
        self.f.flush()

    def close(self):
        self.f.close()

    def write(self, val):
        self.f.write(val)

    def writeBoolean(self, val):
        self.f.write(_bool.pack(val))

    def writeByte(self, val):
        self.f.write(_byte.pack(val))

    def writeUnsignedByte(self, val):
        self.f.write(_ubyte.pack(val))

    def writeShort(self, val):
        self.f.write(_short.pack(val))

    def writeUnsignedShort(self, val):
        self.f.write(_ushort.pack(val))

    def writeChar(self, val):
        self.f.write(_char.pack(val))

    def writeInt(self, val):
        self.f.write(_int.pack(val))

    def writeLong(self, val):
        self.f.write(_long.pack(val))

    def writeFloat(self, val):
        self.f.write(_float.pack(val))

    def writeDouble(self, val):
        self.f.write(_double.pack(val))

    def writeBytes(self, val):
        self.f.write(bytes(val))

    def writeChars(self, val):
        for x in val:
            self.f.write(_char.pack(x))

    def writeUTF(self, val):
        b = val.encode('utf8')
        self.f.write(_short.pack(len(b)))
        self.f.write(b)

class ReadStream:
    """A Java-compatible stream reader."""
    def __init__(self, f):
        self.f = f

    def close(self):
        self.f.close()

    def read(self, size=-1):
        data = self.f.read(size)
        if size is not None and size > 0 and len(data) != size:
            raise StreamEOF("end of file")
        return data

    def skip(self, n):
        self.read(n)

    def readBoolean(self):
        return _bool.unpack(self.read(_bool.size))[0]

    def readByte(self):
        return _byte.unpack(self.read(_byte.size))[0]

    def readUnsignedByte(self):
        return _ubyte.unpack(self.read(_ubyte.size))[0]

    def readShort(self):
        return _short.unpack(self.read(_short.size))[0]

    def readUnsignedShort(self):
        return _ushort.unpack(self.read(_ushort.size))[0]

    def readChar(self):
        return _char.unpack(self.read(_char.size))[0]

    def readInt(self):
        return _int.unpack(self.read(_int.size))[0]

    def readLong(self):
        return _long.unpack(self.read(_long.size))[0]

    def readFloat(self):
        return _float.unpack(self.read(_float.size))[0]

    def readDouble(self):
        return _double.unpack(self.read(_double.size))[0]

    def readBytes(self, n):
        return self.read(n)

    def readChars(self, n):
        return [_char.unpack(self.read(_char.size))[0] for i in range(n)]

    def readUTF(self):
        size = _short.unpack(self.read(_short.size))[0]
        return self.read(size).decode('utf8')

