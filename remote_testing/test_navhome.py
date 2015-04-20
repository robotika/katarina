#!/usr/bin/python
"""
  Test request for navigate home
  status: !NOT TESTED! (requested Aldo/Mexico)
  1) MAKE SURE YOUR MANUAL CONTROL WORKS BEFORE THE TEST
  2) if user != Aldo -> change home lat/lon

  usage:
       ./test_navhome.py <dummytask> [<metalog> [<F>]]
"""
import sys
import os
import inspect

BEBOP_ROOT = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"..")))
if BEBOP_ROOT not in sys.path:
    sys.path.insert(0, BEBOP_ROOT) # access to drone source without installation

from bebop import Bebop
from commands import setHomeCmd, navigateHomeCmd

from apyros.metalog import MetaLog, disableAsserts
from apyros.manual import myKbhit, ManualControlException



def testNavHome( drone, lat, lon ):
    drone.update( cmd=setHomeCmd(lat=lat, lon=lon, altitude=1.5) ) # I am not sure about the altitude purpose
    for i in xrange(50):
        sys.stderr.write('.')
        drone.update( cmd=None )
    drone.videoEnable()
    try:
        drone.trim()
        drone.takeoff()
        drone.flyToAltitude( 1.5 )
        drone.update( cmd=navigateHomeCmd() )
        for i in xrange(1000):
            sys.stderr.write('.')
            drone.update( cmd=None )
            if drone.navigateHomeState == 3: # pending - another confirmation?
                print "PENDING"
                break
        drone.update( cmd=navigateHomeCmd() )
        for i in xrange(1000):
            sys.stderr.write('.')
            drone.update( cmd=None )
        drone.update( cmd=navigateHomeCmd(False) )
        drone.land()
    except ManualControlException, e:
        print
        print "ManualControlException"
#        drone.update( cmd=navigateHomeCmd(False) ) # is it necessary to STOP it first??
        drone.hover()
        if drone.flyingState is None or drone.flyingState == 1: # taking off
            drone.emergency()
        drone.land()


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
    testNavHome( drone, lat=25.6653, lon=-100.244313333 )
    print "Battery:", drone.battery # this time you should not see None any more

# vim: expandtab sw=4 ts=4 

