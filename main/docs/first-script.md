# Prototype Spec: Python CLI Controller for Azimuth/Altitude Arrow (Serial)

## Goal
Build a **simple Python script** that:
1. Runs an **interactive CLI** where the user enters a target direction as:
   - **Azimuth**: `0..360` degrees (wrap allowed)
   - **Altitude**: `-90..+90` degrees
2. Converts the target direction into **stepper motor step targets** (A and B motors / gears).
3. Sends a command over **serial** to a microcontroller.
4. Handles microcontroller responses:
   - `ok` when a command is accepted
   - `busy` if the controller is executing a previous move
   - `complete` when the move finishes

This is a **prototype**, prioritize clarity over features.

---

## System Overview

### Components
- **Python Host Script**
  - Interactive CLI
  - Tracks current state (current azimuth/altitude and motor steps)
  - Computes required steps for motors
  - Sends steps to microcontroller
  - Waits for completion
- **Microcontroller**
  - Executes motion control (timing, acceleration, stepping)
  - Responds over serial with short status messages

---

## Coordinate + Mechanism Model

### User Coordinate Space
- `azimuth_deg` (Yaw): `0..360` degrees
- `altitude_deg` (Pitch): `-90..+90` degrees

### Gear Space (Big gears A and B, in degrees)
Use the differential relationship:

- `Yaw = A`
- `Pitch = B - A`

So to reach a desired `(Yaw, Pitch)`:

- `A_target_deg = Yaw_target_deg`
- `B_target_deg = Yaw_target_deg + Pitch_target_deg`

### Step Conversion
We command the microcontroller in **motor steps**.

Parameters (configurable constants in the Python script):
- `motor_steps_per_rev` (e.g. `200`)
- `microsteps` (e.g. `16`)
- `gear_ratio` (motor revs per 1 big-gear rev), e.g. `20` for 1:20
- Therefore:
  - `steps_per_motor_rev = motor_steps_per_rev * microsteps`
  - `steps_per_big_gear_rev = steps_per_motor_rev * gear_ratio`
  - `steps_per_big_gear_deg = steps_per_big_gear_rev / 360.0`

Convert degrees (big gear) → steps (motor):
- `A_target_steps = round(A_target_deg * steps_per_big_gear_deg)`
- `B_target_steps = round(B_target_deg * steps_per_big_gear_deg)`

**Important note (prototype assumption):**
- At startup, the system is manually aligned to **(0°, 0°)** and the script assumes:
  - `A_current_steps = 0`
  - `B_current_steps = 0`
---

## Angle Rules

### Azimuth Handling
- Accept input `0..360` (allow `360` and treat as `0`).
- Use wrap so `azimuth_deg = azimuth_deg % 360`.

### Altitude Handling
- Must be clamped/validated to `[-90, +90]`.
- If outside, reject input with a message.

### Move Strategy (Simple Prototype)
- For prototype simplicity, do **not** attempt shortest-path wrap.
---

## Serial Protocol (Text-Based)

### Transport
- Serial over USB (e.g. `/dev/ttyUSB0`, `/dev/ttyACM0`, or `COM3`)
- Baud rate: configurable, default `115200`
- Line endings: `\n`

### Messages Sent From Python → Microcontroller
Single command to set target step positions:

**Format**
- `GOTO <A_steps> <B_steps>\n`

**Example**
- `GOTO 32000 24000\n`

Meaning: move until motor A step counter equals `A_steps` and motor B step counter equals `B_steps`
(absolute positions).

### Messages Received From Microcontroller → Python
One of the following lines (case-insensitive is fine, but script can assume lowercase):

- `ok`  
  Means the command is accepted and motion has started (or will start immediately).

- `busy`  
  Means the controller is currently executing a move and cannot accept a new one.

- `complete`  
  Means the controller has reached the target for the last accepted command.

- `error <message>` for parse/validation errors.

---

## Python Script Behavior

### Startup
- Open serial port.
- Print current assumed state: `azimuth=0`, `altitude=0`, `A_steps=0`, `B_steps=0`.
- Show short help:
  - Input formats
  - How to quit (`q`)

### Interactive CLI Loop
1. Prompt user:
   - `Enter azimuth altitude (deg): `
   - Example: `120 15`
2. Parse and validate:
   - Must be two numbers (float allowed, then converted to degrees).
   - Altitude must be in range `[-90, +90]`.
   - Azimuth wrapped to `[0, 360)`.
3. Compute targets:
   - `A_target_deg = azimuth_deg`
   - `B_target_deg = azimuth_deg + altitude_deg`
   - Convert to steps using `steps_per_big_gear_deg`
4. Send command:
   - Send `GOTO A_target_steps B_target_steps\n`
5. Read response loop:
   - If response is `busy`:
     - Print `Controller busy; waiting...`
     - Wait and keep reading until not busy (or retry sending after a delay).
     - Simplest approach: keep trying the same command every ~0.5s until you get `ok`.
   - If response is `ok`:
     - Print `Move accepted. Waiting for complete...`
     - Block until `complete` is received.
   - If response is `complete` without prior `ok`:
     - Treat as completion anyway (robustness).
   - If response is `error ...`:
     - Print it and return to prompt.
6. On `complete`:
   - Update local state:
     - `A_current_steps = A_target_steps`
     - `B_current_steps = B_target_steps`
   - Derive and print:
     - `yaw_deg = A_current_steps / steps_per_big_gear_deg`
     - `pitch_deg = (B_current_steps - A_current_steps) / steps_per_big_gear_deg`
   - Return to prompt.

### Quit
- On `q|quit|exit`, close serial and exit.

---

## Configuration Requirements
The script should have easy-to-edit constants at the top or via CLI args:
- `port` (string)
- `baud` (int, default 115200)
- `motor_steps_per_rev` (int, default 200)
- `microsteps` (int, default 16)
- `gear_ratio` (float/int, default 20)
- `read_timeout` (seconds, e.g. 0.2)
- `busy_retry_delay` (seconds, e.g. 0.5)

---

## Implementation Constraints (Prototype)
- Keep dependencies minimal:
  - Use `pyserial`
  - Standard library only otherwise
- Keep code in one file (e.g. `arrow_cli.py`)
- Keep logic straightforward; no threading required.
- Serial reads should be line-based (`readline()`), robust to empty lines/timeouts.

---

## Acceptance Criteria
- User can enter azimuth/altitude values.
- Script sends correct `GOTO` step values over serial.
- Script handles `busy` by waiting/retrying.
- Script waits for `complete` before allowing the next command.
- Script prints clear status messages and maintains local position state.

---
