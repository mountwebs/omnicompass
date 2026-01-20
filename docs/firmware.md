# Firmware Spec: Arduino Nano Stepper Controller

## Goal
Develop the firmware for an **Arduino Nano** that controls two stepper motors (A and B) representing the gears of the azimuth/altitude arrow. The firmware parses serial commands to move motors to absolute positions and reports status back to the host.

## Hardware & Libraries
- **Microcontroller**: Arduino Nano (ATmega328P)
- **Motor Drivers**: ULN2003 Driver Boards
- **Motors**: 2x 28BYJ-48 Stepper Motors (Unipolar, 2048 steps/revolution)
- **Library**: `AccelStepper` (for non-blocking acceleration/deceleration)

---

## Serial Communication
- **Baud Rate**: `115200`
- **Line Ending**: `\n` (Newline)
- **Input Buffer**: Capable of holding at least one full command line (e.g., 32-64 bytes).

### Command Protocol (Receiver Side)

The firmware listens for ASCII text commands. Commands are case-insensitive.

#### 1. `GOTO <A_steps> <B_steps>`
Moves motor A and motor B to the specified **absolute** step positions.

- **Parameters**: 
  - `A_steps` (long integers): Target absolute position for Motor A.
  - `B_steps` (long integers): Target absolute position for Motor B.

- **Behavior**:
  - If the system is currently **IDLE**:
    1. Parse the values.
    2. Respond with `ok\n`.
    3. Update stepper targets using `moveTo()`.
    4. Begin motion.
  - If the system is currently **MOVING** (motors imply busy):
    1. Respond with `busy\n`.
    2. Ignore the new command (do not overwrite current target).
  - If parsing fails (invalid number of arguments, non-numeric):
    1. Respond with `error invalid command\n` (or similar).

---

## Motion Control Logic

### Setup
- Initialize Serial at 115200.
- Configure `AccelStepper` instances for Motor A and Motor B using `FULL4WIRE` interface (pins IN1-IN4).
- Set `setMaxSpeed` and `setAcceleration`.
  - **Max Speed**: e.g., 700-1000 steps/sec (depends on voltage).
  - **Acceleration**: Max 500 steps/sec².
- reliable "home" position is assumed to be 0 at startup (Power-on = Position 0).

### Main Loop
The `loop()` function needs to handle two tasks concurrently:
1. **Serial Processing**: Read incoming bytes, assemble commands, and process them.
2. **Motor Stepping**: Call `stepper.run()` as frequently as possible to generate step pulses.

### State Reporting
To fulfill the requirement of sending `complete` when done:

- Track a global state flag, e.g., `isMoving`.
- In each loop iteration:
  - Check `stepperA.distanceToGo()` and `stepperB.distanceToGo()`.
  - If `isMoving` is `true`:
    - If **both** motors have `distanceToGo() == 0`:
      - Send `complete\n`.
      - Set `isMoving = false`.
  - If `isMoving` is `false`:
    - (Wait for new commands).

---

## Pin Configuration (Dra - assuming ULN2003 Driver*

| Component | Pin Name | Arduino Pin |
|-----------|----------|-------------|
| **Motor A** | IN1, IN2 | D2, D3      |
|           | IN3, IN4 | D4, D5      |
| **Motor B** | IN1, IN2 | D6, D7      |
|           | IN3, IN4 | D8, D9      
| **Enable**| EN (Shared)| D8 (Optional)|

---

## Error Handling
- **Parse Errors**: If input is not `GOTO <int> <int>`, send `error`.
- **Bounds**: `long` integer overflow is unlikely given mechanical constraints, but standard `long` range is sufficient.
- **Buffer Overflow**: If a line is too long, discard and send `error`.

## Example Interaction
```
(User sends)    GOTO 400 800\n
(Arduino)       ok\n
... (Motors moving) ...
(Arduino)       complete\n

(User sends)    GOTO 1000 1000\n
(Arduino)       ok\n
(User sends)    GOTO 0 0\n  <-- Sent while still moving
(Arduino)       busy\n
... (Motors finish arriving at 1000, 1000) ...
(Arduino)       complete\n
```
