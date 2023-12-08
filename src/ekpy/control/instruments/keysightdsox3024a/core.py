
'''
This is for the KEYSIGHT DSOX3024a Oscilloscope and requires the KEYSIGHT I/O Libraries to function
'''
import numpy as np

__all__ = ('idn', 'reset','setup','acquire',)

def idn(scope):
    return scope.query("*idn?")


def reset(scope):
    scope.write("*RST")

def setup(scope, channel: str=1, voltage_range: str=16, voltage_offset: str=1.00, delay: str='100e-6',
          time_range: str='1e-3', autoscale=True):
    """Sets up the oscilliscope with the given paramaters. If autoscale is turned on it will ignore
    all other arguments and simply autoscale the instrument. Otherwise sample paramters are given
    as the default values. First the Program resets the instrument and after passing in desired parameters
    it sets the scope up for acquiring.

    args:
        scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
        channel (str): Desired channel allowed values are 1,2,3,4
        voltage_range (str): The y scale of the oscilloscope, max is 40V, min is 8mV
        voltage_offset (str): The offset for the voltage in units of volts
        delay (str): The delay in units of s
        time_range (str): The x scale of the oscilloscope, min 2ns, max 50s
    """
    reset(scope)
    if autoscale:
        scope.write(":AUToscale")
    else:
        scope.write("CHANel{}:RANGe {}".format(channel, voltage_range))
        scope.write("CHANel{}:OFFSet {}".format(channel, voltage_offset))
        scope.write("CHANel{}:TIMebase:RANGe {}".format(channel, time_range))
        scope.write("CHANel{}:TIMebase:DELay {}".format(channel, delay))
    scope.write(":ACQuire:TYPE NORMal")

def acquire(scope, channel: str='1', type: str='NORMal', complete: str='100', count: str='10',
            format: str='ASCii', points: str='500'):
    """Sets up the oscilliscope to acquire data and acquires it. Should run .setup() command first


    args:
        scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
        channel (str): Desired channel allowed values are 1,2,3,4
        type (str): Allowed values are 'NORMal', 'AVERage', 'PEAK', and 'HRESolution' [high resolution]
        voltage_offset (str): The offset for the voltage in units of volts
        delay (str): The delay in units of s
        time_range (str): The x scale of the oscilloscope, min 2ns, max 50s
    """
    scope.write(":ACQuire:TYPE {}".format(type))
    scope.write(":ACQuire:COMPlete {}".format(complete))
    scope.write(":ACQuire:COUNt {}".format(count))
    scope.write(":DIGitize CHANnel{}".format(channel))
    scope.write(":WAVeform:FORMat {}".format(format))
    scope.write(":WAVeform:POINts {}".format(points))
    wf = scope.query("WAVeform:DATA?")
    data = np.array([float(d) for d in wf[:-1].split(',')])
    return data






    
       