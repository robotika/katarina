#!/usr/bin/python
"""
  Test request of all drone settings.
  status: TESTED, Charles/France 2015-04-20 ... integrated into Bebop initial config()
  usage:
       ./test_allsettings.py <dummytask> [<metalog> [<F>]]
"""
import sys
import os
import inspect

BEBOP_ROOT = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"..")))
if BEBOP_ROOT not in sys.path:
    sys.path.insert(0, BEBOP_ROOT) # access to drone source without installation

from bebop import Bebop
from commands import requestAllSettingsCmd
from commands import requestAllStatesCmd

from apyros.metalog import MetaLog, disableAsserts
from apyros.manual import myKbhit, ManualControlException



def testAllSettings( drone ):
    drone.update( cmd=requestAllSettingsCmd() )
    for i in xrange(200):
        sys.stderr.write('.')
        drone.update( cmd=None )

def testAllStates( drone ):
    drone.update( cmd=requestAllStatesCmd() )
    for i in xrange(200):
        sys.stderr.write('.')
        drone.update( cmd=None )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)

    metalog=None
    if len(sys.argv) > 2:
        metalog = MetaLog( filename=sys.argv[2] )
    if len(sys.argv) > 3 and sys.argv[3] == 'F':
        disableAsserts()

    drone = Bebop( metalog=metalog, onlyIFrames=True )
    testAllSettings( drone )
    testAllStates( drone )
    print "Battery:", drone.battery # this time you should not see None any more

# vim: expandtab sw=4 ts=4 

