class ReadOnceBuffer(bytearray):
    """Class that automatically deletes the piece of a bytearray that you
    slice. Peek can be used to avoid deletion."""
    
    def __init__(self, data=None):
        self.bytes = bytearray() if data is None else bytearray(data)

    def peek(self, start, stop):
        return self.bytes.__getitem__(slice(start, stop))

    def __add__(self, data):
        self.bytes += data

    def __iadd__(self, data):
        self.bytes += data
        return self

    def __str__(self):
        return str(self.bytes)

    def __repr__(self):
        return repr(self.bytes)

    def __len__(self):
        return len(self.bytes)

    def __getitem__(self, slicer):
        ret = self.bytes.__getitem__(slicer)
        self.bytes.__delitem__(slicer)

        return ret