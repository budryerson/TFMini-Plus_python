'''=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
* File Name: TFMPlus_h.py
* Version: 0.0.1
* Described: A Python definitions module for the
             'TMMPlus.py' module in support of the
             Benewake TFMini-Plus Lidar sensor.
* Developer: Bud Ryerson
* Inception: v0.0.1 - 13 MAR 2021
* Last work: 18 MAR 2021
*
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-'''

# Buffer sizes
TFMP_FRAME_SIZE =  9   # Size of one data frame = 9 bytes
TFMP_COMMAND_MAX = 8   # Longest command = 8 bytes
TFMP_REPLY_SIZE =  8   # Longest command reply = 8 bytes

# Timeout Limits for various functions
TFMP_MAX_READS          = 20   # readData() sets SERIAL error
MAX_BYTES_BEFORE_HEADER = 20   # getData() sets HEADER error
MAX_ATTEMPTS_TO_MEASURE = 20

TFMP_DEFAULT_ADDRESS    = 0x10  # default I2C slave address
                                # as hexidecimal integer
# System Error Status Condition
TFMP_READY        =  0  # no error
TFMP_SERIAL       =  1  # serial timeout
TFMP_HEADER       =  2  # no header found
TFMP_CHECKSUM     =  3  # checksum doesn't match
TFMP_TIMEOUT      =  4  # I2C timeout
TFMP_PASS         =  5  # reply from some system commands
TFMP_FAIL         =  6  #           "
TFMP_I2CREAD      =  7
TFMP_I2CWRITE     =  8
TFMP_I2CLENGTH    =  9
TFMP_WEAK         = 10  # Signal Strength ≤ 100
TFMP_STRONG       = 11  # Signal Strength saturation
TFMP_FLOOD        = 12  # Ambient Light saturation
TFMP_MEASURE      = 13


''' - - - - - -  TFMini Plus data formats  - - - - - - - - -
  Data Frame format:
  Byte0  Byte1  Byte2   Byte3   Byte4   Byte5   Byte6   Byte7   Byte8
  0x59   0x59   Dist_L  Dist_H  Flux_L  Flux_H  Temp_L  Temp_H  CheckSum_
  Data Frame Header character: Hex 0x59, Decimal 89, or "Y"

  Command format:
  Byte0  Byte1   Byte2   Byte3 to Len-2  Byte Len-1
  0x5A   Length  Cmd ID  Payload if any   Checksum
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - '''

# The 'sendCommand( cmnd, param)' function expects a 32bit
# command (cmnd) integer to be in the the following format:
# 0x     00       00       00       00
#     one byte  command  command   reply
#     payload   number   length    length
OBTAIN_FIRMWARE_VERSION   = 0x00010407   # returns 3 byte firmware version
TRIGGER_DETECTION         = 0x00040400   # frame rate must be set to zero
                                         # returns a 9 byte data frame
SYSTEM_RESET              = 0x00020405   # returns a 1 byte pass/fail (0/1)
RESTORE_FACTORY_SETTINGS  = 0x00100405   #           "
SAVE_SETTINGS             = 0x00110405   # This must follow every command
                                         # that modifies volatile parameters.
                                         # Returns a 1 byte pass/fail (0/1)

SET_FRAME_RATE            = 0x00030606   # Each of these commands return
SET_BAUD_RATE             = 0x00060808   # an echo of the command
STANDARD_FORMAT_CM        = 0x01050505   #           "
PIXHAWK_FORMAT            = 0x02050505   #           "
STANDARD_FORMAT_MM        = 0x06050505   #           "
ENABLE_OUTPUT             = 0x00070505   #           "
DISABLE_OUTPUT            = 0x01070505   #           "
SET_I2C_ADDRESS           = 0x100B0505   #           "

SET_SERIAL_MODE           = 0x000A0500   # default is Serial (UART)
SET_I2C_MODE              = 0x010A0500   # set device as I2C slave

I2C_FORMAT_CM             = 0x01000500   # returns a 9 byte data frame
I2C_FORMAT_MM             = 0x06000500   #           "

# *  *  *  *  *  *  *  Description of I/O Mode  *  *  *  *  *  *  *
# Normally, device Pin 3 is either Serial transmit (TX) or I2C clock (SCL).
# When 'I/O Mode' is set other than 'Standard,' Pin 3 becomes a simple HI/LO
# (near/far) binary output.  Thereafter, only Pin 2, the Serial RX line, is
# functional, and only Serial data sent to the device is possible.
#SET_IO_MODE_STANDARD     = 0x003B0900   # 'Standard' is default mode
#SET_IO_MODE_HILO         = 0x013B0900   # I/O, near high and far low
#SET_IO_MODE_LOHI         = 0x023B0900   # I/O, near low and far high
# *  *  *  This library does not support the I/O Mode interface  *  *  *

# Command Parameters
BAUD_9600          = 0x002580   # UART serial baud rate
BAUD_14400         = 0x003840   # expressed in hexidecimal
BAUD_19200         = 0x004B00
BAUD_56000         = 0x00DAC0
BAUD_115200        = 0x01C200
BAUD_460800        = 0x070800
BAUD_921600        = 0x0E1000

FRAME_0            = 0x0000    # internal measurement rate
FRAME_1            = 0x0001    # expressed in hexidecimal
FRAME_2            = 0x0002
FRAME_5            = 0x0003
FRAME_10           = 0x000A
FRAME_20           = 0x0014
FRAME_25           = 0x0019
FRAME_50           = 0x0032
FRAME_100          = 0x0064
FRAME_125          = 0x007D
FRAME_200          = 0x00C8
FRAME_250          = 0x00FA
FRAME_500          = 0x01F4
FRAME_1000         = 0x03E8

# If this module is executed by itself
if __name__ == "__main__":
    print( "This Python module contains variables for" +\
           " the'TFMPlus.py' module that supports the" +\
           " Benewake TFMini-Plus Lidar device")

