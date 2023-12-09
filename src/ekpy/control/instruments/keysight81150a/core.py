'''
This is for the KEYSIGHT 81150A Arbitrary Pulse Generator and requires the KEYSIGHT I/O Libraries to function
'''
import numpy as np

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

def create_arbitrary_waveform():
    

