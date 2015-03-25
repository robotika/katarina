"""
  LogIO - logged input and outputs
"""

import struct
import gzip
import socket

class LoggedSocket:
    def __init__( self, logFilename ):
        if logFilename.endswith(".gz"):
            self.logf = gzip.open( logFilename,"wb" )
        else:
            self.logf = open( logFilename,"wb" )
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def bind( self, pair ):
        return self.soc.bind( pair )

    def recv( self, bufSize ):
        # TODO socket.timeout
        data = self.soc.recv( bufSize )
        if len(data) > 0:
            self.logf.write(data)
            self.logf.flush()
        return data

    def sendto( self, data, pair ):
        # ??? bidirectional socket??
        self.logf.write(data)
        self.logf.flush()
        return self.soc.sendto( data, pair )

    def separator( self, sep ):
        "data log separator"
        self.logf.write( sep )
        self.logf.flush()


class ReplayLog:
    def __init__( self, filename, headerFormat, verbose=False, checkAssert=True ):
        if filename.endswith(".gz"):
            self.f = gzip.open(filename, "rb")
        else:
            self.f = open(filename, "rb")
        self.headerFormat = headerFormat
        self.verbose = verbose
        self.checkAssert = checkAssert


    def bind( self, pair ):
        pass # fake

    def recv( self, bufSize ):
        data = self.f.read( struct.calcsize(self.headerFormat) ) # packet length
        if len(data) == 0:
            raise EOFError
        size = struct.unpack( self.headerFormat, data )[-1]
        # TODO if for is header included in packet size + assert
        return data + self.f.read( size - struct.calcsize(self.headerFormat) )

    def sendto( self, data, pair ):
        refData = self.f.read( len(data) )
        if self.checkAssert:
            assert refData == data, (refData, data)

    def separator( self, sep ):
        "verify data separator"
        data = self.f.read( len(sep) )
        if self.checkAssert:
            assert data == sep, (data, sep)

    def debugRead( self, size ):
        data = self.f.read( size )
        if len(data) != size:
            raise EOFError
        return data

# vim: expandtab sw=4 ts=4 

