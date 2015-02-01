#!/usr/bin/python
"""
  Parsing of incomming messages from Parrot Bebop
  usage:
       ./navdata.py <logged file>
"""
import sys

def parseData( data ):
    assert data[0] == chr(0x2), ord(data[0])    
    assert ord(data[1]) in [0x7F, 0x0], ord(data[1])
    counter = ord(data[2])
    size = ord(data[3])
    print ord(data[1]), counter, "size", size
    data = data[size:]
    return data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    data = open(sys.argv[1], "rb").read()
    while data:
        data = parseData( data )

# vim: expandtab sw=4 ts=4 

