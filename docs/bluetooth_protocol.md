# eFIRE Bluetooth Protocol

## Basic Communication

Communication with the eFIRE controller is facilitated the through Generic
Attribute Profile (GATT) via a Bluetooth LE connection.

Commands can be sent to the controller through the write characteristic at
UUID `0000ff01-0000-1000-8000-00805f9b34fb`. Responses to these commands
can be read by subscribing to notifications on the read characteristic at
UUID `0000ff02-0000-1000-8000-00805f9b34fb`.

## General packet format

The eFIRE Controller uses a binary protocol that follows a TLV schema.

```{packetdiag}
{
  colwidth = 16

  * Header (0xAB) [len=8]
  * Message Type (0xAA or 0xBB) [len=8]
  * Length [len=8]
  * Command [len=8]
  * (Variable length data) [style=dashed, len=16]
  * Checksum (XOR) [len=8]
  * Footer (0x55) [len=8]
}
```

Message Type specifies whether the packet is a request (`0xAA`) or a response (`0xBB`).

The length is given as an unsigned 8-bit integer and denotes the length of the
remaining packet including the footer. Specifically, the length includes the
following fields: Command, Data, Checksum and Footer.

The commands are detailed in their own section below.

The checksum is an XOR over the following fields: Length, Command, Data.

A complete message in this format with a valid checksum could look like this:

`0xAB 0xBB 0x06 0xF2 0x00 0x08 0x00 0xFF 0x55`

This is a response from the <project:#get-ble-version> command.

## Commands

This section describes all commands that can be sent to the controller and their
respective parameters.

(ifc-cmd1)=

### `0x27`: IFC CMD1

This command interacts with the first set of settings of the IFC. This first set
of settings comprises of:

1. Power (0 or 1)
2. Thermostat (0 or 1)
3. Night Light Level (0-6)
4. Continuous Pilot (0 or 1)

Payload format:

```{packetdiag}
{
  colwidth = 16
  node_height = 120
  scale_direction = rtl

  * Power State [len=1, rotate=270]
  * Thermostat Mode [len=1, rotate=270]
  * [len=2]
  * Night Light [len=3, rotate=270]
  * Pilot Mode [len=1, rotate=270]
  * [len=8]
}
```

:parameters:

    ```{describe} CMD1 Payload (2 bytes)
    The first byte is always `0x00`.

    Example: `0x00E3` for Power On, Thermostate enabled, Night Light Level 6,
    Continuous Pilot enabled.
    ```

:return:

    - `0x00`: Success
    - `0x01`: Failure

(ifc-cmd2)=

### `0x28`: IFC CMD2

This command interacts with the second set of settings of the IFC. This second set
of settings comprises of:

1. Flame Height (0-6)
2. Blower Speed (0-6)
3. Aux Relay (0 or 1)
4. Split Flow (0 or 1)

Payload format:

```{packetdiag}
{
  colwidth = 16
  node_height = 120
  scale_direction = rtl

  * Flame Height [len=3, rotate=270]
  * AUX Relay [len=1, rotate=270]
  * Blower Speed [len=3, rotate=270]
  * Split Flow Valve [len=1, rotate=270]
  * [len=8]
}
```

:parameters:

    ```{describe} CMD2 Payload (2 bytes)
    The first byte is always `0x00`.

    Example: `0x00EE` for Flame Height 6, AUX Relay on, Blower Speed 6,
    Split Flow Valve enabled
    ```

:return:

    - `0x00`: Success
    - `0x01`: Failure

### `0xB1`: Set LED Power

Turns the LED Controller on or off.

:parameters:

    ```{describe} Desired LED state (3 bytes)
    - `0xFFFFFF`: On
    - `0x000000`: Off
    ```

:return:

    - `0x00`: Success
    - `0x01`: Failure

### `0xC1`: Set LED Color

Set the LED color on the LED controller.

:parameters:

    ```{describe} Desired LED color in hex RGB format (3 bytes)
    Example: `0xFFFFFF` for white
    ```

:return:

    - `0x00`: Success
    - `0x01`: Failure

### `0xC3`: Set Timer

Set the sleep timer on the controller.

:parameters:

    ```{describe} Hours (1 byte)
    Example: `0x03` for 3 hours
    ```

    ```{describe} Minutes (1 byte)
    Example: `0x0f` for 15 minutes
    ```

    ```{describe} Timer state (1 byte)
    - `0x01`: Enable Timer
    - `0x00`: Disable Timer
    ```

:return:

    - `0x00`: Success
    - `0x01`: Failure

### `0xC4`: Set Power

Turns the burner on or off.

:parameters:

    ```{describe} Desired burner state (1 byte)
    - `0xFF`: On
    - `0x00`: Off
    ```

:return:

    - `0x00`: Success
    - `0x01`: Failure

### `0xC5`: Send Password

Sends a password to the controller.

Used without any preceding password management commands this will authenticate
the connection using the supplied password.
When used in conjunction with the `0xC6` command while supplying the `0xF5`
parameter it is used to set a new password.

:parameters:

    ```{describe} Password as ASCII encoded bytes (variable length)
    Example: `0x30303030` for a password of "0000"
    ```
    :::{warning}
    Maximum length and non-numeric passwords have not been tested!
    :::

:return:

    - `0x00`: Password successfully set
    - `0x01`: Set password failed
    - `0x19`: Invalid password
    - `0x35`: Password accepted

### `0xC6`: Password Management

Initiate a password management action. Used in conjunction with `0xC5` to set a
new password.

:parameters:

    ```{describe} Password action to initiate (1 byte)
    - `0x3F`: Reset Password
    - `0xF5`: Set Password
    ```

:return:

    - `0x00`: Success
    - `0x01`: Failure

### `0xC7`: Sync Timer

Sync local and controller timer values. The eFIRE app presumably uses this to
remove time drift between the app timer display and the remaining time on the controller.

:parameters:

    ```{describe} Hours (1 byte)
    Example: `0x03` for 3 hours
    ```

    ```{describe} Minutes (1 byte)
    Example: `0x0f` for 15 minutes
    ```

    ```{describe} Seconds (1 byte)
    Example: `0x30` for 48 seconds
    ```

:return:

    - `0x00`: Success
    - `0x01`: Failure

### `0xE0`: Get LED Controller Power State

Get the power state of the optional LED controller.

:return:

    - `0x000000`: LEDs are off
    - `0xFFFFFF`: LEDs are on

### `0xE1`: Get LED Color

Get the current color setting from the LED controller.

:return:

    - RGB Hex value of the color

      Example: `0xFF0000` for red

### `0xE2`: Get LED Mode

Get the current mode setting from the LED controller.

:return:

    - `0x010101`: Cycle (i.e. rainbow cycle)
    - `0x020202`: Hold (i.e. single color)
    - `0xFFFFFF`: Ember Bed (i.e. fire effect)

### `0xE3`: Get IFC CMD1 State

Get the current IFC CMD1 state.

:return:

    Returns 2-bytes corresponding to the format described in the
    <project:#ifc-cmd1> section.

    Example: `0x00E3`

### `0xE4`: Get IFC CMD2 State

Get the current IFC CMD2 state.

:return:

    Returns 2-bytes corresponding to the format described in the
    <project:#ifc-cmd2> section.

    Example: `0x00EE`

### `0xE6`: Get Timer

Get the timer settings.

:return:

    ```{describe} Hours (1 byte)
    Example: `0x03` for 3 hours
    ```

    ```{describe} Minutes (1 byte)
    Example: `0x0f` for 15 minutes
    ```

    ```{describe} Timer state (1 byte)
    - `0x01`: Timer enabled
    - `0x00`: Timer enabled
    ```

    ```{describe} Seconds (1 byte)
    Example: `0x30` for 48 seconds
    ```

### `0xE7`: Get Power State

Get the power state of the fireplace.

:return:

    ```{describe} Current fireplace power state (1 byte)
    - `0x00`: Off
    - `0xFF`: On
    ```

### `0xE8`: Get Password

Get the password currently set on the controller.

:return:

    ```{describe} Password as ASCII encoded bytes (variable length)
    Example: `0x30303030` for a password of "0000"
    ```

### `0xE9`: Query Set Password Result

Returns the result from the last password set command.

:return:

    ```{describe} Current fireplace power state (1 byte)
    - `0x25`: Password set failed
    - `0x53`: Password set successful
    ```

### `0xEA`: Time Sync

read time sync from ctrl

### `0xEB`: Get LED Controller State

Return the current overall state of the LED controller.

:return:

    ```{describe} Current LED controller power state (1 byte)
    - `0x00`: Off
    - `0xFF`: On
    ```

    ```{describe} Current LED controller RGB Hex color setting (3 bytes)
    Example `0xFF0000` for red
    ```

    ```{describe} Current LED controller mode (1 byte)
    - `0x01`: Cycle (i.e. rainbow cycle)
    - `0x02`: Hold (i.e. single color)
    - `0xFF`: Ember Bed (i.e. fire effect)
    ```

### `0xF1`: Set LED Controller Mode

Set the LED Controller mode.

:parameters:

    ```{describe} Desired LED controller mode (1 byte)
    - `0x10`: Ember Bed (i.e. fire effect)
    - `0x20`: Cycle (i.e. rainbow cycle)
    - `0x30`: Hold (i.e. single color)
    ```

:return:

    - `0x00`: Success
    - `0x01`: Failure

(get-ble-version)=

### `0xF2`: Get BLE Version

Get the firmware version of the BLE module.

:return:

    ```{describe} BLE Firmware version (3 bytes)
    Example: `0x000800` is parsed by the app as version string "8"
    ```

### `0xF3`: Get MCU Version

Get the firmware version of the MCU.

:return:

    ```{describe} MCU Firmware version (3 bytes)
    Example: `0x010104` is parsed by the app as version string "1.14"
    ```

### `0xF4`: Get Auxiliary Control

:::{note}
Untested. Does not return anything on my device
:::

Return whether the fireplace is currently controlled by the RF remote.

If the fireplace is controlled by the RF remote Bluetooth commands have no
effect and state reported by the controller is invalid.
