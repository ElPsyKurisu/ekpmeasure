
'''
This is for the KEYSIGHT DSOX3024a Oscilloscope and requires the KEYSIGHT I/O Libraries to function.
'''
import numpy as np
import time

__all__ = ('idn', 'reset','setup','acquire', 'initialize', 'configure_timebase', 'configure_channel', 'configure_scale', 
           'configure_trigger_characteristics', 'configure_trigger_edge', 'wait_for_acq_complete', 'error_query',
             'setup_acquire', 'setup_wf', 'query_wf', 'query_wf_settings', 'query_increments',)

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

def wait_for_acq_complete(scope, timeout=100):
    """
    Ensures that the acquisition of data is complete. Taken from LabVIEW. 'Waits for the current waveform acquisition to finish,
    This VI should be called after initiate and before fetch waveform'. Honestly, seems antiquated and seems simpler to use
    *OPC? or *WAI Note in programming guide it says just use *OPC?
    args:
        scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
        timeout (int): In units of 0.01 seconds
    """
    scope.write("*CLS")
    scope.write("*OPC")
    loop_count = timeout
    while True:
        if loop_count > 10:
            print("Timed Out")
            break
        scope.write("*STB?")
        status = int(scope.read())
        binary = bin(status)[7] #checks of the index 5 bit is a 1 since bin goes like 0bxxxx
        if binary is '1':
            break
        loop_count += 1
        time.sleep(.01)
        
def error_query(scope):
    """Queries the instrument for any errors. Taken from LabVIEW. 
    args:
        scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
    returns:
        tuple with the first element being the error code, and the next element the error message
    """ 
    output = scope.query(":SYST:ERR?")
    number, message = output.split(',')
    message = message.strip()
    return number, message

def fetch_waveform(scope, channel: str='1', type: str='NORMal', bind_source_channel: str='None', format: str='ASCii', count: str='10000', timeout: str='1'):
    """Returns the specified channels waveform. Taken from LabVIEW but edited to work better in python (diff functions).
    'Data encoding method was changed to WORD/U16 in driver REV 1.3.1. This would increase precision. If you want the previous behavior before REV 1.3.1 (using BYTE/U8), 
    please change the command ':WAV:FORM WORD' to ':WAV:FORM BYTE' in the Data encoding string in both the Default case and the 0..3, 13..28 case. 
    Another change that must be made is about the type input of the Type Cast function downstream.'
    args:
        scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
        channel (str): Desired channel allowed values are 1,2,3,4
        type (str): Allowed values are 'NORMal', 'AVERage', 'PEAK', and 'HRESolution' [high resolution]
        bind_source_channel (str): Allows for displaying sub-channels allowed args are [None, SUB0, SUB1]
        format (str): The format to return the data in when queried. Example args are [ASCii, WORD (U16)]
        timeout (str) Length in seconds to timeout for
    returns:
        data ()
    """ 
    scope.write(":WAV:SOUR CHAN{}".format(channel))
    if bind_source_channel == 'SUB0' or bind_source_channel == 'SUB1': #to ensure nothing else is passed
        scope.write(":WAV:SOUR:SUB{}".format(bind_source_channel))
    scope.write(":ACQuire:TYPE {}".format(type))
    scope.write(":WAVeform:FORMat {}".format(format))
    scope.write(":WAV:BYT MSBF;:WAV:FORM WORD;") #sets encoding to U16 for higher resolution
    scope.write(":WAV:XOR?;:WAV:XINC?;:WAV:XREF?;:WAV:YOR?;:WAV:YINC?;:WAV:YREF?;")

'''
end of labview copying
'''

def setup_acquire(scope, complete=None, count=None, mode=None, averages=None, type=None):
    """Returns the specified channels waveform with averaging or not and of a specified format/count  
    args:
        scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
        complete (str): Determines the number of time buckets that must be "full" before aquisition is considered complete.
        count (str): In avereging mode, count specifies number of values to be averaged before aqusition is considered complete.
                    Note that it ranges from [2 to 65536] but if you use count='1' its the same as type='HRES'
        averages (str): Sets the number of averages for the waveforms [2,4,8,16,32,64,128,256] $not mentioned in 3000 guide
        mode (str): Sets in real time or equivalent time [RTIMe, ETIMe]
        type (str): Allowed values are 'NORMal', 'AVERage', 'PEAK', and 'HRESolution' [high resolution]
    """ 
    if complete is not None:
        scope.write(":ACQuire:COMPlete {}".format(complete))
    if count is not None:
        scope.write(":ACQuire:COUNt {}".format(count))
    if mode is not None:
        scope.write(":ACQuire:MODE {}".format(mode))
    if averages is not None:
        scope.write(":ACQuire:AVERages {}".format(averages))
    if type is not None:
        scope.write(":ACQuire:TYPE {}".format(type))

def setup_wf(scope, source: str='CHAN1', byte_order: str='MSBF', format: str='byte', points: str='1000', 
             points_mode: str='NORMal', unsigned: str='OFF'):
    """Sets up the waveform with averaging or not and of a specified format/count  
    args:
        scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
        source (str): Desired channel allowed values are [CHAN1, CHAN2, CHAN3, CHAN4, FUNC, SBUS1, etc]
        byte_order (str): Either MSBF (most significant byte first) or LSBF (least significant byte first)
        format (str): Format of data allowed args are [ASCii (floating point), WORD (16bit two-bytes), BYTE (8-bit)]
        points (str): Number of data points for the waveform to return allowed args are [100,250,500,1000]
        points_mode (str): Mode for points allowed args are [NORM (normal), MAX (maximum), RAW]
        unsigned (str): Allows to switch between unsigned and signed integers [OFF (signed), ON (unsigned)]
    """ 
    scope.write(":WAVeform:SOURce {}".format(source))
    scope.write(":WAVeform:BYTeorder {}".format(byte_order))
    scope.write(":WAVeform:FORMat {}".format(format))
    scope.write(":WAVeform:POINts {}".format(points))
    scope.write(":WAVeform:POINts:MODE {}".format(points_mode))
    scope.write(":WAVeform:UNSigned {}".format(unsigned))


def query_wf(scope, byte_order: str='MSBF', unsigned: str='OFF'):
    """Returns the specified channels waveform with averaging or not and of a specified format/count, call
    setup_wf first to intialize it correctly. This function only calls queries. First calls preamble to get
    data format. Then parses data and converts data to usable format.
    GET_PREAMBLE - The preamble block contains all of the current
    ' WAVEFORM settings. It is returned in the form <preamble_block><NL>
    ' where <preamble_block> is:
    ' FORMAT : int16-0= BYTE, 1 = WORD, 4 = ASCII.
    ' TYPE : int16-0= NORMAL, 1 = PEAK DETECT, 2 = AVERAGE
    ' POINTS : int32 - number of data points transferred.
    ' COUNT : int32 - 1 and is always 1.
    ' XINCREMENT : float64 - time difference between data points.
    ' XORIGIN : float64 - always the first data point in memory.
    ' XREFERENCE : int32 - specifies the data point associated with
    ' x-origin.
    ' YINCREMENT : float32 - voltage diff between data points.
    ' YORIGIN : float32 - value is the voltage at center screen.
    ' YREFERENCE : int32 - specifies the data point where y-origin
    ' occurs 
    args:
        scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
        byte_order (str): Either MSBF (most significant byte first) or LSBF (least significant byte first)
        unsigned (str): Allows to switch between unsigned and signed integers [OFF (signed), ON (unsigned)]

    returns:
        preamble_dict (dict) Dictionary with all params labeled. (MetaData)
        time (list): Python list with all the scaled time (x_data array)
        wfm (list): Python list with all the scaled y_values (y_data array) 
    """ 
    preamble = scope.query(":WAVeform:PREamble?")
    preamble_list = preamble.split()
    preamble_dict = {
    'format': np.int16(preamble_list[0]),
    'type': np.int16(preamble_list[1]),
    'points': np.int32(preamble_list[2]),
    'count': np.int32(preamble_list[3]),
    'x_increment': np.float64(preamble_list[4]),
    'x_origin': np.float64(preamble_list[5]),
    'x_reference': np.int32(preamble_list[6]),
    'y_increment': np.float32(preamble_list[7]),
    'y_origin': np.float32(preamble_list[8]),
    'y_reference': np.int32(preamble_list[9]),
    }
    if byte_order == 'MSBF':
        is_big_endian = True
    if byte_order == 'LSBF':
        is_big_endian = False
    if unsigned == 'OFF':
        is_unsigned = False
    if unsigned == 'ON':
        is_unsigned = True
    if preamble_dict["type"] == 0 and not is_unsigned:
        data = scope.query_binary_values("WAVeform:DATA?", datatype='b', is_big_endian=is_big_endian)
    if preamble_dict["type"] == 0 and is_unsigned:
        data = scope.query_binary_values("WAVeform:DATA?", datatype='B', is_big_endian=is_big_endian)
    if preamble_dict["type"] == 1 and is_unsigned:
        data = scope.query_binary_values("WAVeform:DATA?", datatype='h', is_big_endian=is_big_endian)
    if preamble_dict["type"] == 1 and is_unsigned:
        data = scope.query_binary_values("WAVeform:DATA?", datatype='H', is_big_endian=is_big_endian)
    if preamble_dict["type"] == 4:
        data = scope.query_ascii_values("WAVeform:DATA?")
    time = []
    wfm = []
    for t in range(preamble_dict["points"]):
        time.append((t* preamble_dict["x_increment"]) + preamble_dict["x_origin"])
    for d in data:
        wfm.append((d * preamble_dict["y_increment"]) + preamble_dict["y_origin"])
    return preamble_dict, time, wfm

    


def query_wf_settings(scope):
    """
    Asks the scope for the current waveform settings, response taken from example matlab code
    may be innaccurate since original matlab code said 2 for ASCII but its 4:
    FORMAT: int16 - 0 = BYTE, 1 = WORD, 4 = ASCII.
    TYPE: int16 - 0 = NORMAL, 1 = PEAK DETECT, 2 = AVERAGE
    POINTS: int32 - number of data points transferred.
    COUNT: int32 - 1 and is always 1.
    XINCREMENT: float64 - time difference between data points.
    XORIGIN: float64 - always the first data point in memory.
    XREFERENCE: int32 - specifies the data point associated with
    x-origin.
    YINCREMENT: float32 - voltage diff between data points.
    YORIGIN: float32 - value is the voltage at center screen.
    YREFERENCE: int32 - specifies the data point where y-origin
    occurs. 
    args:
        scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
    returns:
        preamble (str): See above for params"""

    return scope.query(":WAVEFORM:PREAMBLE?")

def query_increments(scope):
    """
    Asks the scope what the x and y increments are of the scope, e.g. returns
    the value between two data points: 'For time domain waveforms, this is the time 
    difference between consecutive data points.' - from 3000 series docs.

    args:
        scope (pyvisa.resources.gpib.GPIBInstrument): Keysight DSOX3024a
    returns:
        x_increment, y_increment (tuple): x is in seconds usually, y is in volts usually
    """
    x_increment = scope.query(":WAVeform:XINCrement?")
    y_increment = scope.query(":WAVeform:YINCrement?")
    return x_increment, y_increment

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


'''
Note KEY commands in the programming guide are quite interesting to look at
and allow you to program sequences of physical button presses.
'''





    
       