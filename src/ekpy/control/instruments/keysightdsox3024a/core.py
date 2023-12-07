import numpy as np

'''
This is for the KEYSIGHT DSOX3024a Oscilloscope and requires the KEYSIGHT I/O Libraries to function
'''

def get_address(scope):
    scope.write("*idn?")