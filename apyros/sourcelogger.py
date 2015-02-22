#!/usr/bin/python
"""
  SourceLogger from Eduro project
"""

class SourceLogger:
  def __init__( self, sourceGet, filename ):
    self.sourceGet = sourceGet
    self.counter = 0
    self.prevData = None
    if self.sourceGet != None:
      self.file = open( filename, 'w' )
    else:
      self.file = open( filename )
      try:
        self.counterLimit = int(self.file.readline())
      except ValueError:
        # case when given device was not started
        print "EMPTY FILE!!!"
        self.counterLimit = 10000 # "infinity"


  def get( self ):
    if self.sourceGet != None:
      data = self.sourceGet()
      if data != None and data != self.prevData:
        self.file.write( str(self.counter) + "\n" )
        self.file.write( repr(data) + "\n" )
        self.file.flush()
        self.counter = 1
        self.prevData = data
        return self.prevData
    else:
      if self.counter >= self.counterLimit:
        self.counter = 1
        self.prevData = eval( self.file.readline() )
        nextCnt = self.file.readline()
        self.counterLimit = float('inf') if nextCnt == '' else int(nextCnt)
        return self.prevData
    self.counter += 1
    return None

  def generator( self ):
    assert( self.sourceGet is None )
    while 1:
      line = self.file.readline()
      if len(line) == 0:
        break
      self.prevData = eval( line )
      self.counterLimit = int(self.file.readline())
      yield self.prevData

  def __del__( self ):
    if self.sourceGet != None:
      self.file.write( str(self.counter) + "\n" )
    self.file.close()

