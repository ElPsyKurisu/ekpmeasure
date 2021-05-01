from ..misc import _get_number_and_suffix


__all__ = ('start_pulse_gen', 'stop_pulse_gen', 'trigger', 'set_function_to_pulse',
    'set_run_mode_to_burst', 'set_ncylces_for_burst_mode', 'set_offset', 'set_low_voltage', 
    'set_high_voltage', 'set_pulsewidth','set_polarity')

time_suffix_to_scientific_dict = {'ms':'e-3', 's':'e0', 'us':'e-6', 'ns':'e-9'}
voltage_suffix_to_scientific_dict = {'mv':'e-3', 'v':'e0'}

def start_pulse_gen(pulse_gen, channel = 1, both = False):
    """
    Start the pulse generator.

    args:
        pulse_gen (pyvisa.resources.gpib.GPIBInstrument): Tektronix AFG 3252
        channel (int): 1 or 2. Which channel to turn on
        both (bool): Turn on both channels

    """
    if type(channel) != int:
        raise TypeError('channel must be type int. Recieved type: {}'.format(type(channel)))

    if both:
        pulse_gen.write('OUTPut1:STATe ON')
        pulse_gen.write('OUTPut2:STATe ON')
    else:
        pulse_gen.write('OUTPut{}:STATe ON'.format(channel))
    return

def stop_pulse_gen(pulse_gen, channel = 1, both = False):
    """
    Stops the pulse generator.

    args:
        pulse_gen (pyvisa.resources.gpib.GPIBInstrument): Tektronix AFG 3252
        channel (int): 1 or 2. Which channel to turn off
        both (bool): Turn off both channels

    """
    if type(channel) != int:
        raise TypeError('channel must be type int. Recieved type: {}'.format(type(channel)))

    if both:
        pulse_gen.write('OUTPut1:STATe OFF')
        pulse_gen.write('OUTPut2:STATe OFF')
    else:
        pulse_gen.write('OUTPut{}:STATe OFF'.format(channel))
    return

def set_low_voltage(pulse_gen, low_v, channel = 1, both = False):
    """Specify the low voltage for the pulse generator. 

    args:
        pulse_gen (pyvisa.resources.gpib.GPIBInstrument): Tektronix AFG 3252
        low_v (str): Low voltage. Example '0V'
        channel (int): Which channel.
        both (bool): Set high voltage and pulsewidth for both channels. 

    """
    stop_pulse_gen(pulse_gen, channel = channel, both = both)

    low_v = low_v.lower()
    v_number, v_suffix = _get_number_and_suffix(low_v)
    low_v = str(v_number) + voltage_suffix_to_scientific_dict[v_suffix]

    if not both:
        pulse_gen.write('SOURce1:VOLTage:LEVel:IMMediate:low {}'.format(low_v))
        pulse_gen.write('SOURce2:VOLTage:LEVel:IMMediate:low {}'.format(low_v))
    else:
        pulse_gen.write('SOURce{}:VOLTage:LEVel:IMMediate:low {}'.format(channel, low_v))

    return

def set_high_voltage(pulse_gen, high_v, channel = 1, both = False):
    """Specify the high voltage for the pulse generator. 

    args:
        pulse_gen (pyvisa.resources.gpib.GPIBInstrument): Tektronix AFG 3252
        high_v (str): High voltage. Example '1V'
        channel (int): Which channel.
        both (bool): Set high voltage and pulsewidth for both channels. 

    """
    stop_pulse_gen(pulse_gen, channel = channel, both = both)

    high_v = high_v.lower()
    v_number, v_suffix = _get_number_and_suffix(high_v)
    high_v = str(v_number) + voltage_suffix_to_scientific_dict[v_suffix]

    if not both:
        pulse_gen.write('SOURce1:VOLTage:LEVel:IMMediate:high {}'.format(high_v))
        pulse_gen.write('SOURce2:VOLTage:LEVel:IMMediate:high {}'.format(high_v))
    else:
        pulse_gen.write('SOURce{}:VOLTage:LEVel:IMMediate:high {}'.format(channel, high_v))

    return

def set_pulsewidth(pulse_gen, pw, channel = 1, both = False):
    """Specify the pulse width.

    args:
        pulse_gen (pyvisa.resources.gpib.GPIBInstrument): Tektronix AFG 3252
        pw (str): Pulsewidth. Example '1ms'
        channel (int): Which channel.
        both (bool): Set high voltage and pulsewidth for both channels. 

    """   

    pw = pw.lower()
    pw_number, pw_suffix = _get_number_and_suffix(pw) 
    pw = str(pw_number) + time_suffix_to_scientific_dict[pw_suffix]

    if not both:
        pulse_gen.write('SOURce1:PULSe:WIDTh {}'.format(pw))
        pulse_gen.write('SOURce2:PULSe:WIDTh {}'.format(pw))
    else:
        pulse_gen.write('SOURce{}:PULSe:WIDTh {}'.format(channel, pw))

    return

def trigger(pulse_gen,):
    """Manual trigger for the 3252.
    
    args:
        pulse_gen (pyvisa.resources.gpib.GPIBInstrument): Tektronix AFG 3252
    """

    pulse_gen.write('TRIG')
    return

def set_run_mode_to_burst(pulse_gen, channel = 1, both = False):
    """
    Set the pulse generator to burst mode.

    args:
        pulse_gen (pyvisa.resources.gpib.GPIBInstrument): Tektronix AFG 3252
        channel (int): 1 or 2. Which channel
        both (bool): Set both channels to burst

    """
    if type(channel) != int:
        raise TypeError('channel must be type int. Recieved type: {}'.format(type(channel)))

    if both:
        pulse_gen.write('source1:burst:state on')
        pulse_gen.write('source2:burst:state on')
    else:
        pulse_gen.write('source{}:burst:state on'.format(channel))
    return


def set_ncylces_for_burst_mode(pulse_gen, ncycles = 1, channel = 1, both = False):
    """
    Set ncycles in burst mode

    args:
        pulse_gen (pyvisa.resources.gpib.GPIBInstrument): Tektronix AFG 3252
        ncycles (int): How many cycles.
        channel (int): 1 or 2. Which channel
        both (bool): Set both channels

    """
    if type(channel) != int:
        raise TypeError('channel must be type int. Recieved type: {}'.format(type(channel)))

    if both:
        pulse_gen.write('source1:burst:ncycles {}'.format(ncycles))
        pulse_gen.write('source2:burst:ncycles {}'.format(ncycles))
    else:
        pulse_gen.write('source{}:burst:ncycles {}'.format(channel, ncycles))
    return

def set_function_to_pulse(pulse_gen, channel = 1, both = False):
    """
    Set the pulse generator to output a pulse.

    args:
        pulse_gen (pyvisa.resources.gpib.GPIBInstrument): Tektronix AFG 3252
        channel (int): 1 or 2. Which channel
        both (bool): Set both channels

    """
    if type(channel) != int:
        raise TypeError('channel must be type int. Recieved type: {}'.format(type(channel)))

    if both:
        pulse_gen.write('source1:function:shape pulse')
        pulse_gen.write('source2:function:shape pulse')
    else:
        pulse_gen.write('source{}:function:shape pulse'.format(channel))
    return

def set_offset(pulse_gen, offset = '0e0', channel = 1, both = False):
    """
    Set offset. 

    args:
        pulse_gen (pyvisa.resources.gpib.GPIBInstrument): Tektronix AFG 3252
        offset (str): Offset
        channel (int): 1 or 2. Which channel
        both (bool): Set both channels

    """
    if type(channel) != int:
        raise TypeError('channel must be type int. Recieved type: {}'.format(type(channel)))

    if both:
        pulse_gen.write('source1:votage:level:IMMediate:offset {}'.format(offset))
        pulse_gen.write('source2:votage:level:IMMediate:offset {}'.format(offset))
    else:
        pulse_gen.write('source{}:votage:level:IMMediate:offset {}'.format(channel, offset))
    return

def set_polarity(pulse_gen, inverted = False, channel = 1, both = False):
    """Set the polarity of the channel.

    args:
        pulse_gen (pyvisa.resources.gpib.GPIBInstrument): Tektronix AFG 3252
        inverted (bool): Invert.
        channel (int): 1 or 2. Which channel
        both (bool): Set both channels
    """
    if type(channel) != int:
        raise TypeError('channel must be type int. Recieved type: {}'.format(type(channel)))

    if inverted:
        polarity = 'inv'
    else:
        polarity = 'norm'

    if both:
        pulse_gen.write('output1:polarity {}'.format(polarity))
        pulse_gen.write('output2:polarity {}'.format(polarity))
    else:
        pulse_gen.write('output{}:polarity {}'.format(channel, polarity))
    return