'''=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
 # Filename: TFMPlus.py
 # Inception: 10 MAR 2021
 # Described: Python module for the Benewake TFMini-Plus Lidar sensor
 #            The TFMini-Plus is a unique product, and the various
 #            TFMini Libraries are not compatible with the Plus.
 # Developer: Bud Ryerson
 # Version:   0.0.1 10MAR21
 #
 # Default settings for the TFMini-Plus are a 115200 serial baud rate
 # and a 100Hz measurement frame rate. The device will begin returning
 # measurement data immediately on power up.
 #
 # 'begin()' function passes a serial stream to library and
 #  returns TRUE/FALSE whether serial data is available.
 #  Function also sets a public one byte status code.
 #  Status codes are defined within the library.
 #
 # 'getData( dist, flux, temp)' passes back measurement data
 #  • dist = distance in centimeters,
 #  • flux = signal strength in arbitrary units, and
 #  • temp = an encoded number in degrees centigrade
 #  Function returns TRUE/FALSE whether completed without error.
 #  Error, if any, is saved as a one byte 'status' code.
 #
 # 'sendCommand( cmnd, param)' sends a 32bit command code (cmnd)
 #  and a 32bit parameter value (param). Returns TRUE/FALSE and
 #  sets a one byte status code.
 #  Commands are selected from the library's list of defined commands.
 #  Parameter values can be entered directly (115200, 250, etc) but
 #  for safety, they should be chosen from the Library's defined lists.
 #  An incorrect value can render the device uncommunicative.
 #
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-'''

import time
import serial
from TFMPlus_h import *  #  definitions module

status = 0           # error status code
dist =   0           # distance to target
flux =   0           # signal quality or intensity
temp =   0           # internal chip temperature
version = bytearray( 3)   # firmware version number

#  Return TRUE/FALSE whether receiving serial data from
#  device, and set system status to provide more information.
def begin( port, rate):
    ''' Set serial port and test for data'''
    global pStream
    pStream = serial.Serial( port, rate)
    time.sleep(0.2)             #  Give port 200ms to initalize
    if( pStream.inWaiting() > 0):    #  If data present...
        status = TFMP_READY     #  return status as READY
        return True
    else:                       #  Otherwise...
        status = TFMP_SERIAL    #  return status as SERIAL ERROR
        return False

#  Return TRUE/FALSE whether data received without error
#  and set system status to provide more information.
def getData():
    ''' Get serial frame data from device'''
    
    # make data variables global
    global status, dist, flux, temp

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  Step 1 - Get data from the device.
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  Set 1 second timeout if HEADER code never appears
    #  or serial data never becomes available.
    serialTimeout = time.time() + 1000
    #  Flush all but last frame of data from the serial buffer.
    while( pStream.inWaiting() > TFMP_FRAME_SIZE):
        pStream.read()
    #  Read one byte from the serial buffer into the data buffer's
    #  'plus one' position, then left shift the whole array 1 byte
    #  and repeat until the two HEADER bytes show up as the first
    #  two bytes in the array.
    frame = bytearray( TFMP_FRAME_SIZE)   #  'frame' data buffer
    while( frame[ 0] != 0x59) or ( frame[ 1] != 0x59):
        if( pStream.inWaiting()):
            #  Read 1 byte into the 'frame' plus one position.
            frame.append( pStream.read()[0])
            #  Shift entire length of 'frame' one byte left.
            frame = frame[ 1:]
        #  If no HEADER or serial data not available
        #  after more than one second...
        if( time.time() >  serialTimeout):
            status = TFMP_HEADER   #  ...then set error
            return False

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  Step 2 - Perform a checksum test.
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  Clear the 'chkSum' variable declared in 'TFMPlus.h'
    chkSum = 0
    #  Add together all bytes but the last.
    for i in range( TFMP_FRAME_SIZE -1):
        chkSum += frame[ i]
    #   If the low order byte does not equal the last byte...
    if( ( chkSum & 0xFF) != frame[ TFMP_FRAME_SIZE -1]):
        status = TFMP_CHECKSUM  #  ...then set error
        return False

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  Step 3 - Interpret the frame data
    #           and if okay, then go home
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    dist = (frame[3] * 256) + frame[2]
    flux = (frame[5] * 256) + frame[4]
    temp = (frame[7] * 256) + frame[6]
    #  Convert temp code to degrees Celsius.
    temp = ( temp >> 3) - 256
    #  Convert Celsius to degrees Farenheit
    #  temp = ( temp * 9 / 5) + 32

    #  - - Evaluate Abnormal Data Values - -
    #  Values are from the TFMini-S Product Manual
    #  Signal strength <= 100
    if( dist == -1):     status = TFMP_WEAK
    #  Signal Strength saturation
    elif( flux == -1):   status = TFMP_STRONG
    #  Ambient Light saturation
    elif( dist == -4):   status = TFMP_FLOOD
    #  Data is apparently okay
    else:                status = TFMP_READY

    if( status != TFMP_READY):
        return False;
    else:
        return True;

#  = = = = =  SEND A COMMAND TO THE DEVICE  = = = = = = = = = =0
#
#  Create a proper command byte array, send the command,
#  get a repsonse, and return the status
def sendCommand( cmnd, param):
    ''' Send serial command and get reply data'''

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  Step 1 - Build the command data to send to the device
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # From 32bit 'cmnd' integer, create a four byte array of:
    # reply length, command length, command number and a one byte parameter
    cmndData = bytearray( cmnd.to_bytes( TFMP_COMMAND_MAX, byteorder = 'little'))

    replyLen = cmndData[ 0]        #  Save the first byte as reply length.
    cmndLen = cmndData[ 1]         #  Save the second byte as command length.
    cmndData[ 0] = 0x5A            #  Set the first byte to HEADER code.

    if( cmnd == SET_FRAME_RATE):    #  If the command is Set FrameRate...
        cmndData[3:2] = param.to_bytes( 2, byteorder = 'little')     #  add the 2 byte FrameRate parameter.
    elif( cmnd == SET_BAUD_RATE):   #  If the command is Set BaudRate...
        cmndData[3:3] = param.to_bytes( 3, byteorder = 'little')     #  add the 3 byte BaudRate parameter.

    cmndData = cmndData[0:cmndLen]  # re-establish command data length
    
    #  Create a checksum byte for the command data array.
    chkSum = 0
    #  Add together all bytes but the last.
    for i in range( cmndLen -1):
        chkSum += cmndData[ i]
    #  and save it as the last byte of command data.
    cmndData[ cmndLen - 1] = ( chkSum & 0xFF)
    
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  Step 2 - Send the command data array to the device
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    pStream.reset_input_buffer()    #  flush input buffer
    pStream.reset_output_buffer()   #  flush output buffer
    pStream.write( cmndData)        #  send command data
        
    #  + + + + + + + + + + + + + + + + + + + + + + + + +
    #  If the command does not expect a reply, then we're
    #  finished here. Go home.
    if( replyLen == 0):
        return True
    #  + + + + + + + + + + + + + + + + + + + + + + + + +

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  Step 3 - Get command reply data back from the device.
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  Set a one second timer to timeout if HEADER never appears
    #  or serial data never becomes available
    serialTimeout = time.time() + 1000
    #  Establish 'reply' bytearray and fill with zeros
    reply = bytearray( replyLen)
    
    #  1) Read one byte from serial buffer
    #  2) Append byte to end of 'reply'
    #  3) Left shift entire array by one byte.
    #  4) Repeat until 'HEADER' and 'replyLen'
    #     appear as first two bytes in array.
    while( reply[ 0] != 0x5A) or (reply[ 1] != replyLen):
        if( pStream.inWaiting()):
            #  Read 1 byte into the 'frame' plus one position.
            reply.append( pStream.read()[0])
            #  Shift entire length of 'frame' one byte left.
            reply = reply[ 1:]
        #  If HEADER/replyLen combo does do not
        #  appear after more than one second...
        if( time.time() >  serialTimeout):
            status = TFMP_HEADER   #  ...then set error type
            return False           # and return 'False'.

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  Step 4 - Perform a checksum test.
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  Clear the 'chkSum' variable declared in 'TFMPlus.h'
    chkSum = 0
    #  Add together all bytes but the last.
    for i in range( replyLen -1):
        chkSum += reply[ i]
    #  If the low order byte does not equal the last byte...
    if( ( chkSum & 0xFF) != reply[ replyLen - 1]):
      status = TFMP_CHECKSUM  #  ...then set error
      return False            #  and return 'False.'

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  Step 5 - Interpret different command responses.
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    if( cmnd == OBTAIN_FIRMWARE_VERSION):
        version[ 0] = reply[ 5]  #  set firmware version.
        version[ 1] = reply[ 4]
        version[ 2] = reply[ 3]
    else:
        if( cmnd == SYSTEM_RESET or
            cmnd == RESTORE_FACTORY_SETTINGS or
            cmnd == SAVE_SETTINGS ):
            if( reply[ 3] == 1):    #  If PASS/FAIL byte non-zero...
                status = TFMP_FAIL  #  then set status to 'FAIL'...
                return False        #  and return 'False'.

    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #  Step 6 - Set status to 'READY' and return 'True'
    #  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    status = TFMP_READY
    return True

#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  - - - - -    The following is for testing purposes    - - - -
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#============   For troubleshooting  ========
# for i in range( len(cmndData)):
#     print( f" {cmndData[i]:0{2}X}", end='')
# print()
#===============================================

#  Called by either 'printFrame()' or 'printReply()'
#  Print status condition either 'READY' or error type
def printStatus():
    ''' Print staus condition'''
    print("Status: ", end= '')
    if( status == TFMP_READY):       print( "READY", end= '')
    elif( status == TFMP_SERIAL):    print( "SERIAL", end= '')
    elif( status == TFMP_HEADER):    print( "HEADER", end= '')
    elif( status == TFMP_CHECKSUM):  print( "CHECKSUM", end= '')
    elif( status == TFMP_TIMEOUT):   print( "TIMEOUT", end= '')
    elif( status == TFMP_PASS):      print( "PASS", end= '')
    elif( status == TFMP_FAIL):      print( "FAIL", end= '')
    elif( status == TFMP_I2CREAD):   print( "I2C-READ", end= '')
    elif( status == TFMP_I2CWRITE):  print( "I2C-WRITE", end= '')
    elif( status == TFMP_I2CLENGTH): print( "I2C-LENGTH", end= '')
    elif( status == TFMP_WEAK):      print( "Signal weak", end= '')
    elif( status == TFMP_STRONG):    print( "Signal saturation", end= '')
    elif( status == TFMP_FLOOD):     print( "Ambient light saturation", end= '')
    else:                            print( "OTHER", end= '')
    print()

#  Print error type and HEX values
#  of each byte in the data frame
def printFrame():
    '''Print status and frame data'''
    printStatus();
    print("Data:", end= '')  # no carriage return
    for i in range( TFMP_FRAME_SIZE):
        #  >>> f"{value:#0{padding}X}"
        # Pad hex number with 0s to length of n characters
        print(f" {frame[ i]:0{2}X}", end='')
    print()
    
#  Print error type and HEX values of
#  each byte in the command response frame.
def printReply():
    '''Print status and reply data'''
    printStatus()
    #  Print the Hex value of each byte
    for i in range( TFMP_REPLY_SIZE):
        print(f" {reply[ i]:0{2}X}", end='')    
    print()

# If this module is executed by itself
if __name__ == "__main__":
    print( "This Python module supports the" +\
           " Benewake TFMini-Plus Lidar device")
        
