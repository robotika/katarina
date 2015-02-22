#!/usr/bin/python
"""
  Manual control
"""
import sys


class ManualControlException( Exception ):
  pass


if sys.platform == 'win32':
    import msvcrt  # for kbhit

    def myKbhit():
        if not msvcrt.kbhit():
            return 0
        key = msvcrt.getch()
        if key == '\xe0': # Arrows
            key = (key, msvcrt.getch())
        return key

else:
    # TODO if pygame is not available try linux io
    import pygame

    def myKbhit():
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                return 1 # or key value??
        return 0

    # requires
    # pygame.init()
    # screen = pygame.display.set_mode((100,100))



# vim: expandtab sw=4 ts=4 

