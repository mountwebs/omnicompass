# OmniCompass Main Control Scripts

This directory contains the high-level Python scripts for controlling the OmniCompass hardware.

## Environment Setup

Ensure you have Python 3 installed. It is recommended to use a virtual environment to manage dependencies.

### Installation

1. Navigate to this directory:
   ```bash
   cd main
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Arrow CLI (`arrow_cli.py`)

The `arrow_cli.py` script provides an interactive command-line interface to control the compass arrow's azimuth (yaw) and altitude (pitch).

### Basic Usage

If you have the hardware connected via USB:

1. Identify your serial port (e.g., `/dev/tty.usbmodem...` on macOS or `COM3` on Windows).
2. Run the script:
   ```bash
   python arrow_cli.py --port /dev/tty.usbmodem1101
   ```

You can also set the environment variable to avoid typing the port every time:
```bash
export OMNICOMPASS_SERIAL_PORT=/dev/tty.usbmodem1101
python arrow_cli.py
```

### Test Mode

To test the interface without connecting to hardware (mock mode):

```bash
python arrow_cli.py --test
```

### Interactive Commands

Once the CLI is running:
- **Move**: Enter two numbers separated by a space: `azimuth altitude`.
  - Example: `90 10` (90 degrees azimuth, 10 degrees altitude).
  - Azimuth is 0-360°. Altitude is -90° to +90°.
- **Quit**: Type `q`, `quit`, or `exit`.

### Configuration Options

The script is pre-configured for the standard 28BYJ-48 motor and the project's custom gearing. You can override these defaults if needed:

| Argument | Description | Default |
|----------|-------------|---------|
| `--port` / `-p` | Serial port path | Environment `OMNICOMPASS_SERIAL_PORT` |
| `--test` / `-t` | Run in mock mode (no hardware) | False |
| `--baud` | Serial baud rate | 115200 |
| `--motor-steps` | Steps per motor revolution | 2048 |
| `--gear-ratio` | External gear ratio | ~3.846 (50/13) |

Example custom run:
```bash
python arrow_cli.py --port /dev/ttyUSB0 --gear-ratio 4.0
```
