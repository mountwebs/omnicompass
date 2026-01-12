# Arrow Controller Serial Communication Protocol

This document specifies a simple, robust serial communication protocol for controlling a two-axis arrow (azimuth + altitude) using an Arduino-based controller.

The protocol is inspired by GRBL principles but simplified for **single-command-at-a-time execution**.

---

## 1. Goals and Constraints

- Arduino controls an arrow that can point in any direction.
- Two motors: **Azimuth (AZ)** and **Altitude (ALT)**.
- The controller receives commands over **serial (UART / USB serial)**.
- One motion command at a time.
- The controller:
  - Accepts a target coordinate
  - Replies immediately with `ok` or `error`
  - Executes the move
  - Sends a **completion message** when the target is reached

---

## 2. Transport & Framing

- **Transport:** UART serial (USB serial is fine)
- **Encoding:** ASCII
- **Framing:** Line-based, newline-terminated (`\n`, optional `\r\n`)
- **Rule:** One command per line

---

## 3. Device State Model

The controller is always in one of the following states:

- `IDLE` — ready to accept a new target
- `BUSY` — executing a motion command
- `ALARM` — fault condition (limits, motor error, etc.)

### Acceptance Rules

- Motion commands are accepted **only in `IDLE`**
- Status, stop, and reset commands are accepted in **any state**

---

## 4. Commands (PC → Arduino)

### 4.1 Motion Command: `GOTO`

**Recommended format (key=value):**

```
GOTO AZ=<azimuth_deg> ALT=<altitude_deg>
```

Example:
```
GOTO AZ=123.45 ALT=67.89
```

#### Units and Ranges

- `AZ`: degrees, typically `[0, 360)` (wrap allowed)
- `ALT`: degrees, typically `[-90, +90]` (or mechanical limits)

#### Optional Fields (future-proofing)

- `SPD=<deg_per_s>` — motion speed
- `ID=<int>` — sender-provided command ID

Example:
```
GOTO AZ=10.0 ALT=20.0 SPD=45 ID=17
```

---

### 4.2 Status Query

Single-character command:

```
?
```

Requests an immediate status snapshot.

---

### 4.3 Stop / Abort

Single-character command:

```
!
```

Stops motion as soon as possible and transitions to `IDLE` or `ALARM`.

---

### 4.4 Reset / Clear Alarm (Optional)

```
RESET
```

Resets the controller or clears an alarm condition.

---

## 5. Responses (Arduino → PC)

### 5.1 Immediate Acknowledgement

Sent after a full command line is received and validated.

#### Success:
```
ok
```

#### Error:
```
error:<code> <message>
```

Suggested error codes:

| Code | Meaning |
|----|--------|
| 1 | bad_format |
| 2 | out_of_range |
| 3 | busy |
| 4 | alarm |
| 5 | checksum (optional future use) |

---

### 5.2 Motion Completion Event (Asynchronous)

Sent when the arrow has reached the target.

With ID:
```
DONE ID=<id> AZ=<finalAz> ALT=<finalAlt>
```

Without ID:
```
DONE AZ=<finalAz> ALT=<finalAlt>
```

Example:
```
DONE ID=17 AZ=10.00 ALT=20.00
```

---

### 5.3 Status Report (Response to `?`)

GRBL-style, machine-readable format:

```
<STATE|AZ=<az>|ALT=<alt>|TAZ=<targetAz>|TALT=<targetAlt>|ERR=<err>>
```

Examples:

While moving:
```
<BUSY|AZ=3.25|ALT=6.10|TAZ=10.00|TALT=20.00>
```

Idle:
```
<IDLE|AZ=10.00|ALT=20.00>
```

Alarm:
```
<ALARM|ERR=limit_hit>
```

---

### 5.4 Startup Banner

Sent on boot or reset:

```
ArrowCtrl 1.0 ready
```

---

## 6. Sender (PC) Behavior

1. Wait for startup banner (optional but recommended)
2. Send `GOTO ...`
3. Wait for `ok` or `error`
4. After `ok`, **do not send another `GOTO`** until `DONE` is received
5. Optionally poll with `?` at ~5–10 Hz for UI updates

---

## 7. Robustness Rules

### 7.1 Line Length Limit

- Maximum line length (recommended): 64–96 characters
- If exceeded:
  - Flush until newline
  - Respond with `error:1 bad_format`

### 7.2 Resynchronization

- Sender may send `?` to recover state
- Reconnect or reset if no response

### 7.3 Numeric Format

- Optional sign (`+` / `-`)
- Decimal numbers allowed
- Scientific notation **not supported**

---

## 8. Example Session

```
ArrowCtrl 1.0 ready
```

```
GOTO AZ=10.0 ALT=20.0 ID=17
```

```
ok
```

```
?
```

```
<BUSY|AZ=3.25|ALT=6.10|TAZ=10.00|TALT=20.00|ID=17>
```

```
DONE ID=17 AZ=10.00 ALT=20.00
```

---

## 9. Implementation Notes (Arduino)

- Read serial bytes into a buffer until newline
- Strip `\r`
- Parse commands by prefix (`GOTO`, `?`, `!`)
- Validate ranges before accepting
- On `GOTO` acceptance:
  - Store target
  - Set state to `BUSY`
  - Send `ok`
- When motion completes:
  - Set state to `IDLE`
  - Send `DONE`

---

**End of protocol specification**

