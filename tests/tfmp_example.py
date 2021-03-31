'''=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
* File Name: TFMP_example.py
* Inception: 14 MAR 2021
* Developer: Bud Ryerson
# Version:   0.0.1
* Last work: 30 MAR 2021

* Description: Python script to test the Benewake TFMini Plus
* time-of-flight Lidar ranging sensor in Serial (UART) mode
* using the 'TFMPlus.py' module in development.

* Default settings for the TFMini-Plus are a 115200 serial baud rate
* and a 100Hz measurement frame rate. The device will begin returning
* three measurement datums right away:
*   Distance in centimeters,
*   Signal strength in arbitrary units and
*   Temperature encoded for degrees centigrade

* Use the 'sendCommand()' to send a command and a parameter.
* Returns a boolean result and sets a one byte status code.
* Commands are defined in the module's list of commands.
* Parameters can be entered directly (115200, 250, etc) but for
* safety, they should be chosen from the module's defined lists.

* NOTE:
*   GPIO15 (RPi Rx pin) connects to the TFMPlus Tx pin and
*   GPIO14 (RPi Tx pin) connects to the TFMPlus Rx pin
*

* Press Ctrl-C to break the loop
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-'''

# Skip a line and say 'Hello!'
print( "\n\rTFMPlus Module Example - 18MAR2021")

import time
import sys
import tfmp_main as tfmP    # Import main module v0.0.1
from tfmp_defines import *  # Import definitions for main module

serialPort = "/dev/serial0"  # Raspberry Pi normal serial port
serialRate = 115200          # TFMini-Plus default baud rate

# - - - Set and Test serial communication - - - -
print( "Serial port: ", end= '')
if( tfmP.begin( serialPort, serialRate)):
    print( "ready.")
else:
    print( "not ready")
    sys.exit()   #  quit the program if serial not ready

# - - Perform a system reset - - - - - - - -
print( "System reset: ", end= '')
if( tfmP.sendCommand( SYSTEM_RESET, 0)):
    print( "passed.")
else:
    tfmP.printReply()
time.sleep(0.5)  # allow 500ms for reset to complete

# - - Display the firmware version - - - - - - - - -
print( "Firmware version: ", end= '')
if( tfmP.sendCommand( OBTAIN_FIRMWARE_VERSION, 0)):
    print( str( tfmP.version[ 0]) + '.', end= '') # print three numbers
    print( str( tfmP.version[ 1]) + '.', end= '') # separated by a dot
    print( str( tfmP.version[ 2]))
else:
    tfmP.printReply()

# - - Set the data frame-rate to 20Hz - - - - - - - -
print( "Data-Frame rate: ", end= '')
if( tfmP.sendCommand( SET_FRAME_RATE, FRAME_20)):
    print( str(FRAME_20) + 'Hz')
else:
    tfmP.printReply()

# - - - - - - - - - - - - - - - - - - - - - - - -
time.sleep(0.5)            # And wait for half a second.


# - - - - - -  the main program loop begins here  - - - - - - -
try:
    while True:
        time.sleep(0.05)   # Loop delay 50ms to match the 20Hz data frame rate
        # Use the 'getData' function to get data from device
        if( tfmP.getData()):
            print( f" Dist: {tfmP.dist:{3}}cm ", end= '')   # display distance,
            print( f"Flux: {tfmP.flux:{4}d} ",   end= '')   # display signal strength/quality,
            print( f"Temp: {tfmP.temp:{2}}°C",  )   # display temperature,
        else:                  # If the command fails...
          tfmP.printFrame()    # display the error and HEX data
#
except KeyboardInterrupt:
    print( 'Keyboard Interrupt')
#    
except: # catch all other exceptions
    eType = sys.exc_info()[0]  # return exception type
    print( eType)
#
finally:
    print( "That's all folks!")
    sys.exit()                   # clean up the OS and exit
#
# - - - - - -  the main program sequence ends here  - - - - - - -