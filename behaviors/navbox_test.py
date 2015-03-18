from navbox import *
import unittest


class NavBoxTest( unittest.TestCase ): 
    def testMatchCirRect( self ):
        self.assertEqual( matchCircRect(circles=[],rectangles=[]), None )
        circles = [((467.87, 303.77), 26.93)]
        rectangles = [((467.51, 303.77), (25.29, 7.58), -2.602), 
                      ((519.88, 303.19), (12.06, 54.44), -6.911)]
        self.assertEqual( matchCircRect(circles=circles,rectangles=rectangles), ((467.87, 303.77),(519.88, 303.19)) )

if __name__ == "__main__":
    unittest.main() 
# vim: expandtab sw=4 ts=4 

