
'''
This is for the KEYSIGHT DSOX3024a Oscilloscope and requires the KEYSIGHT I/O Libraries to function
'''
import numpy as np

__all__ = ('idn', 'reset','setup','acquire', 'initialize', 'configure_timebase', 'configure_channel', 'configure_scale', 
           'configure_trigger_characteristics', 'configure_trigger_edge',)

def idn(scope):
    return scope.query("*idn?")


def reset(scope):
    scope.write("*RST")

def setup(scope, channel: str=1, voltage_range: str=16, voltage_offset: str=1.00, delay: str='100e-6',
          time_range: str='1e-3', autoscale=True):
    """
    Sets up the oscilliscope with the given paramaters. If autoscale is turned on it will ignore
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

'''
Below I am just remaking the LabVIEW program in python, or making my version of them, Note
inside the program I will say if it is just a copy else it is a substitute
'''

def initialize(scope):
    """
    This program simply resets and clears the registry for the scope to make sure its ready to go
    args:
        scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
    """
    
    scope.write("*RST")
    scope.write("*CLS")


def configure_timebase(scope, time_base_type: str='MAIN', position: str='0.0',
                       range: str='0.001', reference: str='CENTer', scale: str='50', vernier=False, ref_bnc=False):
    """Configures the timebase of the oscilliscope. Adapted from LabVIEW program 'Configure Timebase (Basic)'
    Should call initialize first.

    args:
        scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
        time_base_type (str): Allowed values are 'MAIN', 'WINDow', 'XY', and 'ROLL', note must use main for data acquisition
        position (str): The position in the scope
        range (str): The x range of the scope min is 2ns, max is 50s
        scale (str): The x scale of the scope in units of s/div
        vernier (boolean): Enables Vernier scale
        ref_bnc (boolean): Enables REF BNC
    """
    scope.write("TIMe:MODE {}".format(time_base_type))
    scope.write("TIMe:POS {}".format(position))
    scope.write("TIMe:RANG {}".format(range))
    scope.write("TIMe:REF {}".format(reference))
    scope.write("TIMe:SCAL {}".format(scale))
    if vernier:
        scope.write("TIMe:VERN ON")
    else:
        scope.write("TIMe:VERN OFF")
    if ref_bnc:
        scope.write("TIMe:REFC ON")
    else:
        scope.write("TIMe:REFC OFF")

def configure_channel(scope, channel: str='1', scale_mode=True, vertical_scale: str='5', vertical_range: str='40',
                              vertical_offset: str='0.0', coupling: str='DC', probe_attenuation: str='1.0', 
                              impedance: str='ONEM', enable_channel=True):
    """Sets up the voltage measurement on the desired channel with the desired paramaters. Taken from
    LabVIEW. 

    args:
        scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
        channel (str): Desired channel allowed values are 1,2,3,4
        scale_mode (boolean): Allows us to select between a vertical scale or range setting [see options below]
        vertical_scale (str): The vertical scale in units of v/div
        vertical_range (str): The verticale scale range min: 8mv, max: 40V
        vertical_offset (str): The offset for the vertical scale in units of volts
        coupling (str): 'AC' or 'DC' values allowed
        probe_attenuation (str): Multiplicative factor to attenuate signal to stil be able to read, max is most likely 10:1
        impedance (str): Configures if we are in high impedance mode or impedance match. Allowed factors are 'ONEM' for 1 M Ohm and 'FIFT' for 50 Ohm
        enable_channel (boolean): Enables the channel
    """
    if scale_mode:
        scope.write("CHANel{}:SCAL {}".format(channel, vertical_scale))
    else:
        scope.write("CHANel{}:RANG {}".format(channel, vertical_range))
    scope.write("CHANel{}:OFFS {}".format(channel, vertical_offset))
    scope.write("CHANel{}:COUP {}".format(channel, coupling))
    scope.write("CHANel{}:PROB {}".format(channel, probe_attenuation))
    scope.write("CHANel{}:IMP {}".format(channel, impedance))
    if enable_channel:
        scope.write("CHANel{}:DISP ON".format(channel))
    else:
        scope.write("CHANel{}:DISP OFF".format(channel))

def configure_scale(scope, channel: str='1', time_scale: str='0.0001', vertical_scale: str='5'):
    """Configures both the time scale and the vertical axis scale. Taken from
    LabVIEW. 'Scales the time (horizontal) and vertical axes for the selected analog channel.'

    args:
        scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
        channel (str): Desired channel allowed values are 1,2,3,4
        time_scale (str): In units of sec/div
        vertical scale (str): in units of volts/div
    """
    scope.write("TIMebase:SCALe {}".format(time_scale))
    scope.write("CHANnel{}:SCALe {}".format(vertical_scale))

def configure_trigger_characteristics(scope, type: str='EDGE', holdoff_time: str='4E-8', low_voltage_level: str='1',
                                      high_voltage_level: str='1', trigger_source: str='CHAN1', sweep: str='AUTO',
                                       enable_high_freq_filter=False, enable_noise_filter=False):
    """Configures the trigger characteristics Taken from LabVIEW. 'Configures the basic settings of the trigger.'
    args:
        scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
        type (str): Trigger type, accepted params are: [EDGE (Edge), GLIT (Glitch), PATT (Pattern), TV (TV), EBUR (Edge Burst), RUNT (Runt), NFC (Setup Hold), TRAN (Transition), SBUS1 (Serial Bus 1), SBUS2 (Serial Bus 2), USB (USB), DEL (Delay), OR (OR), NFC (Near Field Communication)]
        holdoff_time (str): Additional Delay in units of sec before re-arming trigger circuit
        low_voltage_level (str): The low trigger voltage level units of volts
        high_voltage_level (str): The high trigger voltage level units of volts
        trigger_source (str): Desired channel to trigger on allowed values are [CHAN1,CHAN2,CHAN3,CHAN4, EXT (there are more)]
        sweep (str): Allowed values are [AUTO (automatic), NORM (Normal)]
        enable_high_freq_filter (boolean): Toggles the high frequency filter
        enable_noise_filter (boolean): Toggles the noise filter
    """
    if enable_high_freq_filter:
        scope.write(":TRIG:HFR ON")
    else:
        scope.write(":TRIG:HFR OFF")
    scope.write(":TRIG:HOLD {}".format(holdoff_time))
    scope.write(":TRIG:LEV:HIGH {}, CHAN{}".format(high_voltage_level, trigger_source))
    scope.write(":TRIG:LEV:LOW {}, CHAN{}".format(low_voltage_level, trigger_source))
    scope.write(":TRIG:MODE {}".format(type))
    if enable_noise_filter:
        scope.write(":TRIG:NREJ ON")
    else:
        scope.write(":TRIG:NREJ OFF")
    scope.write(":TRIG:SWE {}".format(sweep))

def configure_trigger_edge(scope, trigger_source: str='CHAN1', input_coupling: str='AC', edge_slope: str='POS', 
                           level: str='0', filter_type: str='OFF'):
    """Configures the trigger characteristics Taken from LabVIEW. 'Configures the basic settings of the trigger.'
    args:
        scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
        trigger_source (str): Desired channel/source to trigger on allowed values are: [CHAN1,CHAN2,CHAN3,CHAN4,DIG0,DIG1 (there are more)]
        input_coupling (str): Allowed values = [AC, DC, LFR (Low Frequency Coupling)]
        edge_slope (str): Allowed values = [POS, NEG, EITH (either), ALT (alternate)]
        level (str): Trigger level in volts
        filter_type (str): Allowed values = [OFF, LFR (High-pass filter), HFR (Low-pass filter)] Note: Low Frequency reject == High-pass
    """
    scope.write(":TRIG:SOUR {}".format(trigger_source))
    scope.write(":TRIG:COUP {}".format(input_coupling))
    scope.write(":TRIG:LEV {}".format(level))
    scope.write(":TRIG:REJ {}".format(filter_type))
    scope.write(":TRIG:SLOP {}".format(edge_slope))


'''
end of labview copying
'''


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






    
       