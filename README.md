# tfmplus
### PLEASE NOTE:

**v0.1.0** - This version reverses and corrects the `ENABLE_OUTPUT` and `DISABLE_OUTPUT` commands.<br />

Also, three commands names are changed in this version:
<br />&nbsp;&nbsp;&#9679;&nbsp;`OBTAIN_FIRMWARE_VERSION`  is now `GET_FIRMWARE_VERSION`
<br />&nbsp;&nbsp;&#9679;&nbsp;`RESTORE_FACTORY_SETTINGS` is now `HARD_RESET`
<br />&nbsp;&nbsp;&#9679;&nbsp;`SYSTEM_RESET`             is now `SOFT_RESET`<br />
<hr />

### Python module for the TFMini-Plus, TFMini-S and TFLuna in serial (UART) communications mode.

The **TFMini-Plus** is largely compatible with the **TFMini-S** and the **TF-Luna**, which are also able to use this module.  One difference is that upon command to change communication mode (`SET_I2C_MODE`, `SET_SERIAL_MODE`) the **TFMini-Plus** switches immediately, whereas the **TFMini-S** requires an additional `SAVE_SETTING` command.  This module is *not compatible* with the **TFMini**, which is an entirely different product with its own command set and data structure.

With hardware v1.3.5 and firmware v1.9.0 and above, the TFMini-Plus communication interface can be configured to use either the default **UART** (serial) or the **I2C** (two-wire) protocol.  Additionally, the device can be configured to output a binary (high/low) voltage level to signal that a detected object is within or beyond a user-defined range.  Please see the comments below and the manufacturer's Product Manual for more information about the **I/O** output mode.

The UART serial baud-rate is user-programmable, but only the following rates are supported:<br />
9600, 14400, 19200, 56000, 115200, 460800, and 921600.

Device data-frame output rates are programmable up to 10KHz, but the internal measuring frame rate is fixed at 4KHz.<br />
"Standard" output rates are: 1, 2, 5, 10, 20, 25, 50, 100, 125, 200, 250, 500, and 1000Hz.<br />
If the output rate is set to 0 (zero), single data-frames can be triggered by using the `TRIGGER_DETECTION` command.

After a getData() command, three module variables are updated:
<br />&nbsp;&nbsp;&#9679;&nbsp; `dist` Distance to target in centimeters. Range: 0 - 1200
<br />&nbsp;&nbsp;&#9679;&nbsp; `flux` Strength or quality of return signal or error. Range: -1, 0 - 32767
<br />&nbsp;&nbsp;&#9679;&nbsp; `temp` Temperature of device chip in code. Range: -25°C to 125°C

The default TFMini-Plus communication interface is UART (serial); the default baud-rate is 115200 and the default data-frame rate is 100Hz.  Upon power-up in serial mode, the device will immediately start sending asynchronous frames of measurement data at the frame-rate.

This module supports **only** the default, UART (serial) communication interface.  For communication in I2C mode, please install and import the TFMini-Plus-I2C module, `tfmpi2c`.  Read more below about using the I2C mode of the device.
<hr />

### Three `tfmplus` module functions
The three module functions are all defined in the main module file, `__init__.py` along with parameters, commands and status codes.

`begin( port, rate)` passes the serial port name and baud rate of the host device to the module and returns a boolean value indicating whether serial data is available. The function also sets a public one-byte `status` or error code.

`getData()` reads a serial data-frame from the device and extracts the three measurement data values.  It sets the `status` error code byte and returns a boolean value indicating 'pass/fail'.  If no serial data is received or no header sequence \[`0x5959`\] is detected within one (1) second, the function sets an appropriate `status` error code and 'fails'.  Given the asynchronous nature of the device, the serial buffer is flushed before reading and the `frame` and `reply` data arrays are zeroed out to delete any residual data.  This helps with valid data recognition and error discrimination.

`sendCommand( cmnd, param)` sends a coded command and a coded parameter to the device.  It sets the `status` error code byte and returns a boolean 'pass/fail' value.  A proper command (`cmnd`) must be selected from the module's list of twenty defined commands.  A parameter (`param`) may be entered directly as an unsigned number, but it is better to choose from the module's defined parameters because **an erroneous parameter can block communication and there is no external means of resetting the device to factory defaults.**

Any change of device settings (i.e. frame rate or baud rate) must be followed by a `SAVE_SETTINGS` command or else the modified values may be lost when power is removed.  `SYSTEM_RESET` and `RESTORE_FACTORY_SETTINGS` do not require a `SAVE_SETTINGS` command.

Benewake is not forthcoming about the internals of the device, however they did share this:
>Some commands that modify internal parameters are processed within 1ms.  Some commands require the MCU to communicate with other chips may take several ms.  And some commands, such as saving configuration and restoring the factory need to erase the FLASH of the MCU, which may take several hundred ms.

Also included:
<br />&nbsp;&nbsp;&#9679;&nbsp; A python script 'tfmp_test.py' is in `tests`.
<br />&nbsp;&nbsp;&#9679;&nbsp; Recent copies of the manufacturer's Data-sheet and Product Manual are in `docs`.

All of the code for this module and the test script is richly commented to assist with understanding and in problem solving.
<hr />

### Using the I2C version of the device
According to Benewake:
>1- the measuring frequency of the module should be 2.5 times larger than the IIC reading frquency.
<br />2- the iic reading frequency should not exceed 100hz<br />

Because the Data-Frame Rate is limited to 1000Hz, this condition implies a 400Hz data sampling limit in I2C mode.  Benewake says sampling should not exceed 100Hz.  They don't say why; but you might keep that limitation in mind when you consider using the I2C interface.

To configure the device for I2C communication, a command must be sent using the UART interface.  Therefore, this reconfiguration should be made prior to the device's service installation, either by using this module's `SET_I2C_MODE` command or the serial GUI test application and code supplied by the manufacturer.

The `SET_I2C_MODE` command does not require a subsequent `SAVE_SETTINGS` command.  The device will remain in I2C mode after power has been removed and restored.  The only way to return to serial mode is with the `SET_SERIAL_MODE` command.  Even a `RESTORE_FACTORY_SETTINGS` command will NOT restore the device to its default, UART communication interface mode.

The device functions as an I2C slave device and the default address is `16` (`0x10` Hex) but is user-programmable by sending the `SET_I2C_ADDRESS` command and a parameter in the range of `1` to `127`.  The new setting will take effect immediately and permanently without a `SAVE_SETTINGS` command, however the `RESTORE_FACTORY_SETTINGS` command will restore the default address.  The I2C address can be set while still in serial communication mode or, if in I2C mode, an example script included in the TFMini-Plus-I2C module can be used to test and change the address.
<hr>

### Using the I/O modes of the device
The so-called I/O modes are not supported by this module.  Please do not attempt to use any I/O commands that you may find to be defined in this module.

The I/O output mode is enabled and disabled by this 9 byte command:<br />
5A 09 3B MODE DL DH ZL ZH SU

Command byte number:<br />
0 &nbsp;&nbsp; `0x5A`:  Header byte, starts every command frame<br />
1 &nbsp;&nbsp; `0x09`:  Command length, number of bytes in command frame<br />
2 &nbsp;&nbsp; `0x3B`:  Command number<br />
<br />
3 &nbsp;&nbsp; MODE:<br />
&nbsp;&nbsp;&nbsp;&nbsp; `0x00`: I/O Mode OFF, standard data output mode<br />
&nbsp;&nbsp;&nbsp;&nbsp; `0x01`: I/O Mode ON, output: near = high and far = low<br />
&nbsp;&nbsp;&nbsp;&nbsp; `0x02`: I/O Mode ON, output: near = low and far = high<br />
<br />
4 &nbsp;&nbsp; DL: Near distance lo order byte of 16 bit integer<br />
5 &nbsp;&nbsp; DH: Near distance hi order byte<br />
<br />
6 &nbsp;&nbsp; ZL: Zone width lo byte<br />
7 &nbsp;&nbsp; ZL: Zone width hi byte<br />
<br />
8 &nbsp;&nbsp;SU: Checkbyte (the lo order byte of the sum of all the other bytes in the frame)<br />
<br />
If an object's distance is greater than the Near distance (D) plus the Zone width (Z) then the object is "far."<br />
If the distance is less than the Near distance (D) then the object is "near".<br />
The Zone is a neutral area. Any object distances measured in this range do not change the output.<br />
The output can be set to be either high when the object is near and low when it's far (Mode 1); or low when it's near and high when it's far (Mode 2).<br />
The high level is 3.3V, the low level is 0V.

