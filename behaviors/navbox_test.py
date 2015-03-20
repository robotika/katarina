from navbox import *
import unittest


class NavBoxTest( unittest.TestCase ): 
    def testMatchCirRect( self ):
        self.assertEqual( matchCircRect(circles=[],rectangles=[]), None )
        circles = [((467.87, 303.77), 26.93)]
        rectangles = [((467.51, 303.77), (25.29, 7.58), -2.602), 
                      ((519.88, 303.19), (12.06, 54.44), -6.911)]
        self.assertEqual( matchCircRect(circles=circles,rectangles=rectangles), ((467.87, 303.77),(519.88, 303.19)) )
        
        self.assertEqual( matchCircRect(
            circles = [((1124, 732), 66)],
            rectangles = [((1123, 730), (64, 21), -1), ((897, 758), (40, 398), 0), ((1249, 728), (30, 135), -6)] ),
            ((1124, 732), (1249, 728)) )
        
    def testMatchCirRectBug( self ):
        self.assertEqual( matchCircRect(circles=[],
            rectangles=[((76.5, 21.5), (43.0, 153.0), -90.0), ((335.5, 357.0), (277.0, 20.0), 0.0), 
                        ((395.5, 20.5), (215.0, 41.0), -0.0)] ), None )

if __name__ == "__main__":
    unittest.main() 
# vim: expandtab sw=4 ts=4 

