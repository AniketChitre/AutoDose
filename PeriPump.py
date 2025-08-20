#---------------------------------------------------------------------------------#
# LIBRARY MANAGING THE COMMUNICATION WITH A REGLO ICC WITH 4 INDEPENDENT CHANNELS #
#---------------------------------------------------------------------------------#

import serial
import time

class RegloICC:
    # Initialize the pump
    def __init__(self, COM):
        self.COM = COM
        # Open the serial port with the data format corresponding to the RegloICC pump
        self.sp = serial.Serial(self.COM, 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
        self.direction = [0, 0, 0, 0]  # 0 = clockwise, 1 = counter-clockwise
        self.mode = [0, 0, 0, 0]  # 0 = RPM, 1 = Flow Rate, 2 = Volume (over time), one can add here all other modes
        self.speed = [0, 0, 0, 0]  # rotation speed for each channel in RPM mode
        # Change the size of 'direction', 'mode' and 'speed' according to the total number of channels to control.
        # In the case herein, 4 channels are being independently controlled

    # Delete the pump
    def __del__(self):
        self.sp.close()

    # Start the corresponding channel
    def start_channel(self, channel):
        command = f'{channel}H\r'.encode() # 'H' to start the channel
        # \r for the carriage return [CR] required to tell the pump that the command is finished
        self.sp.write(command) # write the command to the pump
        time.sleep(0.1) # give the pump time to process the command after sending it before reading the response
        return self.sp.read(self.sp.in_waiting).decode() # read the pump response

    # Stop the corresponding channel
    def stop_channel(self, channel):
        command = f'{channel}I\r'.encode() # 'I' to stop the channel
        self.sp.write(command)
        time.sleep(0.1)
        return self.sp.read(self.sp.in_waiting).decode()

    # Set the rotation direction for a single channel
    def set_direction(self, channel, direction):
        if direction == 1:
            command = f'{channel}K\r'.encode() # counter-clockwise
        else:
            command = f'{channel}J\r'.encode() # clockwise
        self.sp.write(command)
        self.direction[channel - 1] = direction # pyhton count starts from 0
        time.sleep(0.1)
        return self.sp.read(self.sp.in_waiting).decode()

    # Get the rotation direction of a single channel
    def get_direction(self, channel):
        command = f'{channel}xD\r'.encode() # 'xD' to get the rotation direction
        self.sp.write(command)
        time.sleep(0.1)
        # read the rotation direction from the corresponding channel
        return self.sp.read(self.sp.in_waiting).decode()

    # Set the speed for a single channel in RPM when in RPM mode
    def set_speed(self, channel, speed): # in RPM, with speed less then 100
        speed = max(min(speed, 100), 0) # speed between 0 and 100 RPM
        speed_string = f'{int(speed):03d}{int((speed - int(speed)) * 100)}' # format speed explained below
        command = f'{channel}S0{speed_string}\r'.encode()
        self.sp.write(command) # set the speed for the corresponding channel
        self.speed[channel - 1] = speed
        time.sleep(0.1)
        return self.sp.read(self.sp.in_waiting).decode()

#--------------------------------------------------------------------------------#
# SPEED_STRING EXAMPLE                                                           #
## Speed value :                                                                 #
# speed = 123.456                                                                #
#                                                                                #
## Convert the integer part to a string with at least three digits :             #
# integer_part = f'{int(speed):03d}'; ## --&gt; Result: '123'                       #
#                                                                                #
## Convert the decimal part to a string with two digits :                        #
# decimal_part = f'{int((speed - int(speed)) * 100)}'; ## --&gt; Result: '45'       #
#                                                                                #
## Concatenate the two parts :                                                   #
# speed_string = f'{int(speed):03d}{int((speed - int(speed)) * 100)}';           #
## --&gt; Result: '12345' representing 123.45 in fixed-point notation               #
#                                                                                #
## When the two strings are concatenated, the result is a string that represents #
## the original speed value in a fixed-point notation with three digits before   #
## the decimal point and two digits after, without the decimal separator.        #
#--------------------------------------------------------------------------------#

    # Read out speed of a single channel in RPM when in RPM mode
    def get_speed(self, channel):
        command = f'{channel}S\r'.encode() # 'S' to get the setting speed in RPM
        self.sp.write(command)
        time.sleep(0.1)
        return self.sp.read(self.sp.in_waiting).decode()

    # Set the operational mode for a single channel (you can add all other modes)
    def set_mode(self, channel, mode):
        if mode == 0:
            command = f'{channel}L\r'.encode()  # RPM mode
        elif mode == 1:
            command = f'{channel}M\r'.encode()  # Flow rate mode
        else:
            command = f'{channel}G\r'.encode()  # Volume (over time) mode
        self.sp.write(command)
        self.mode[channel - 1] = mode
        time.sleep(0.1)
        return self.sp.read(self.sp.in_waiting).decode()

    # Get the operational mode of a single channel
    def get_mode(self, channel):
        command = f'{channel}xM\r'.encode() # 'xM' to get the operational mode
        self.sp.write(command)
        time.sleep(0.1)
        return self.sp.read(self.sp.in_waiting).decode()

#----------------------------------------------------------------------------#
#   EXAMPLES ON HOW TO USE THE DEFINED CLASS TO CONTROL THE Reglo ICC PUMP   #
#----------------------------------------------------------------------------#