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

    def testRectangleTooFar( self ):
        # logs\navdata_150314_112527.bin 25
        self.assertEqual( matchCircRect(
            circles=[((318, 335), 39)],
            rectangles=[((432, 23), (51, 10), -71), ((512, 20), (51, 11), -57), ((591, 16), (52, 11), -49), 
                ((318, 335), (11, 39), 0), ((221, 174), (77, 18), -4), ((19, 337), (39, 7), -9), 
                ((381, 241), (22, 85), -5), ((318, 261), (72, 15), 0)]), 
            ((318, 335), (318, 261)) ) # instead of (221, 174)
        # index out of range
        self.assertEqual( matchCircRect(
            circles=[((549, 162), 39), ((282, 142), 19), ((282, 142), 21), ((196, 157), 37)],
            rectangles=[((355, 4), (7, 23), -90), ((4, 137), (7, 24), 0)]), None )

    def testMissingDetection150331( self ):
        self.assertEqual( matchCircRect(
            circles=[((244, 272), 28)],
            rectangles=[((245, 272), (28, 8), -86), ((255, 183), (147, 10), 0), ((241, 330), (58, 13),0)]), ((244, 272), (241, 330)) )

if __name__ == "__main__":
    unittest.main() 
# vim: expandtab sw=4 ts=4 

