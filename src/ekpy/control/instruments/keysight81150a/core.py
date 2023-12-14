'''
This is for the KEYSIGHT 81150A Arbitrary Pulse Generator and requires the KEYSIGHT I/O Libraries to function
'''
import numpy as np
from typing import Union
import struct

__all__ = ('idn', 'reset', 'initialize', 'configure_impedance', 'configure_output_amplifier', 'configure_trigger',
            'create_arbitrary_waveform', 'configure_arb_waveform', 'enable_output',)

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

def create_arbitrary_waveform(wavegen, data: Union[np.array, list], name: str='ARB1'):
    """
    This program creates an arbitrary waveform within the limitations of the
    Keysight 81150A which has a limit of 2 - 524288 data points. In order to send data
    in accordance with the 488.2 block format which looks like #ABC, where '#' marks the start
    of the data flow and 'A' refers to the number of digits in the byte count, 'B' refers to the
    byte count and 'C' refers to the actual data in binary. The data is first scaled between
    -8191 to 8191 in accordance to our instrument. Adapted from LabVIEW (note their arrays
    contain 10,000 elements). 
    Note: Will NOT save waveform in non-volatile memory if all the user available slots are
    filled (There are 4 allowed at 1 time plus 1 in volatile memory).

    args:
        wavegen (pyvisa.resources.gpib.GPIBInstrument): Keysight 81150A
        channel (str): Desired Channel to configure accepted params are [1,2]
        source (str): Trigger source allowed args = [IMM (immediate), INT2 (internal), EXT (external), MAN (software trigger)]
        mode (str): The type of triggering allowed args = [EDGE (edge), LEV (level)]
        slope (str): The slope of triggering allowed args = [POS (positive), NEG (negative), EIT (either)]
    """  
    #will want to include error handling in this one.
    data = np.array(data)
    scaled_data = scale_waveform_data(data)
    scaled_data = scaled_data.astype(np.int16)
    size_of_data = str(2*len(scaled_data)) #multiply by 2 to account for negative values?
    #want to send stuff accoprding to format whcih is #ABC
    a = len(size_of_data.encode('utf-8')) 
    b = size_of_data
    #c is the binary data to be passed
    c = scaled_data.tobytes()
    #i think im done?
    wavegen.write(":FORM:BORD NORM")
    wavegen.write(":DATA:DAC VOLATILE, #{}{}{}".format(a,b,c))
    wavegen.write(":DATA:COPY {}, VOLATILE".format(name))

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

def enable_output(wavegen, channel: str='1', on=True):
    """
    This program enables the selected output. Taken from LabVIEW. 
    args:
        wavegen (pyvisa.resources.gpib.GPIBInstrument): Keysight 81150A
        channel (str): Desired Channel to configure accepted params are [1,2]
        on (boolean): True for on, False for off
    """
    if on:
        wavegen.write(":OUTP{} ON".format(channel))
    else:
        wavegen.write(":OUTP{} OFF".format(channel))

def send_software_trigger(wavegen):
    """
    This program sends the software trigger. Taken from LabVIEW. 
    args:
        wavegen (pyvisa.resources.gpib.GPIBInstrument): Keysight 81150A
    """
    wavegen.write(":TRIG")

def stop(wavegen):
    """Stop the scope.

	args:
		wavegen (pyvisa.resources.ENET-Serial INSTR): Keysight 81150A
	"""
    enable_output(wavegen, '1', False)
    enable_output(wavegen, '2', False)


'''
Helper functions:
'''

def scale_waveform_data(data: np.array) -> np.array:
    '''
    Scales the data between -1 and 1 then multiplies by instrument specific
    scaling factor (8191 for ours)
    '''
    normalized = 2*(data - np.min(data))/np.ptp(data) - 1
    return normalized * 8191

size_of_data = str(16)
#want to send stuff accoprding to format whcih is #ABC
a = len(size_of_data.encode('utf-8'))
print(a)