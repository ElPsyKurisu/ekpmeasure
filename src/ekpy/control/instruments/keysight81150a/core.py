'''
This is for the KEYSIGHT 81150A Arbitrary Pulse Generator and requires the KEYSIGHT I/O Libraries to function
'''
import numpy as np

__all__ = ('idn', 'reset','setup','acquire', 'initialize', 'configure_timebase', 'configure_channel', 'configure_scale', 
           'configure_trigger_characteristics', 'configure_trigger_edge',)

def idn(scope):
    return scope.query("*idn?")


def reset(scope):
    scope.write("*RST")