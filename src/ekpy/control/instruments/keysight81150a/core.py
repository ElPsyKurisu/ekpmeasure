'''
This is for the KEYSIGHT 81150A Arbitrary Pulse Generator and requires the KEYSIGHT I/O Libraries to function
'''
import numpy as np
from typing import Union

__all__ = ('idn', 'reset', 'initialize', )

def idn(wavegen):
    return wavegen.query("*idn?")


def reset(wavegen):
    wavegen.write("*RST")

'''
Below I am just remaking the LabVIEW program in python, or making my version of them, Note
inside the program I will say if it is just a copy else it is a substitute
'''

def initialize(wavegen):
    """
    This program simply resets and clears the registry for the pulse generator to make sure its ready to go
    args:
        wavegen (pyvisa.resources.gpib.GPIBInstrument): Keysight 81150A
    """
    
    wavegen.write("*RST")
    wavegen.write("*CLS")

def configure_impedance(wavegen, channel: str='1', output_impedance: str='50.0', input_impedance: str='50.0'):
    """
    This program configures the output and input impedance of the wavegen. Taken from LabVIEW.
    args:
        wavegen (pyvisa.resources.gpib.GPIBInstrument): Keysight 81150A
        channel (str): Desired Channel to configure accepted params are [1,2]
        output_impedance (str): The desired output impedance in units of Ohms
        input_impedance (str): The desired input impedance in units of Ohms

    """
    wavegen.write(":OUTP{}:IMP:EXT {}".format(channel, input_impedance))
    wavegen.write(":OUTP{}:IMP {}".format(channel, output_impedance))

def configure_output_amplifier(wavegen, channel: str='1', type: str='HIV'):
    """
    This program configures the output amplifier for eiither maximum bandwith or amplitude. Taken from LabVIEW.
    args:
        wavegen (pyvisa.resources.gpib.GPIBInstrument): Keysight 81150A
        channel (str): Desired Channel to configure accepted params are [1,2]
        type (str): Amplifier Type args = [HIV (MAximum Amplitude), HIB (Maximum Bandwith)]
    """
    wavegen.write("OUTP{}:ROUT {}".format(channel, type))

def configure_trigger(wavegen, channel: str='1', source: str='IMM', mode: str='EDGE', slope: str='POS'):
    """
    This program configures the output amplifier for eiither maximum bandwith or amplitude. Taken from LabVIEW.
    args:
        wavegen (pyvisa.resources.gpib.GPIBInstrument): Keysight 81150A
        channel (str): Desired Channel to configure accepted params are [1,2]
        source (str): Trigger source allowed args = [IMM (immediate), INT2 (internal), EXT (external), MAN (software trigger)]
        mode (str): The type of triggering allowed args = [EDGE (edge), LEV (level)]
        slope (str): The slope of triggering allowed args = [POS (positive), NEG (negative), EIT (either)]
    """ 
    wavegen.write(":ARM:SOUR{} {}".format(channel, source))
    wavegen.write(":ARM:SENS{} {}".format(channel, mode))
    wavegen.write(":ARM:SLOP {}".format(slope))

def create_arbitrary_waveform(wavegen, data, name: str='ARB1',):
    """
    This program creates an arbitrary waveform within the limitations of the
    Keysight 81150A which has a limit of 2 - 524288 data points.
    args:
        wavegen (pyvisa.resources.gpib.GPIBInstrument): Keysight 81150A
        channel (str): Desired Channel to configure accepted params are [1,2]
        source (str): Trigger source allowed args = [IMM (immediate), INT2 (internal), EXT (external), MAN (software trigger)]
        mode (str): The type of triggering allowed args = [EDGE (edge), LEV (level)]
        slope (str): The slope of triggering allowed args = [POS (positive), NEG (negative), EIT (either)]
    """  
    #will want to include error handling in this one.


#https://github.com/jeremyherbert/barbutils/blob/master/barbutils.py
#upper frequnecy range is 120MHZ so do not go above that
#maybe i can use this barb stuff to read the waveforms too...
#finds avg max - min /2 can probably use githubn library to generate barb file then pass that

def configure_arb_waveform(wavegen, channel: str='1', name='ARB1', gain: str='1.0', offset: str='0.00', freq: str='1000'):
    """
    This program configures arbitrary waveform already saved on the instrument. Taken from LabVIEW. 
    args:
        wavegen (pyvisa.resources.gpib.GPIBInstrument): Keysight 81150A
        channel (str): Desired Channel to configure accepted params are [1,2]
        name (str): The Arbitrary Waveform name as saved on the instrument
        gain (str): The V_pp by which the waveform should be gained by
        offset (str): The voltage offset in units of volts
        freq (str): the frequency in units of Hz for the arbitrary waveform
    """
    wavegen.write(":FUNC{}:USER {}:FUNC{} USER".format(channel, name, channel))
    wavegen.write(":VOLT{} {}".format(channel, gain))
    wavegen.write(":FREQ{} {}".format(channel, freq))
    wavegen.write(":VOLT{}:OFFS {}".format(channel, offset))  


'''
Helper functions:
'''

def scale_waveform_data(data: Union[np.array, list]) -> np.array:
    '''
    Scales the data between -1 and 1 then multiplies by instrument specific
    scaling factor (8191 for ours)
    '''
    data = np.array(data)
    normalized = 2*(data - np.min(data))/np.ptp(data) - 1
    return normalized * 8191

