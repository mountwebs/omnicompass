#!/usr/bin/env python3
"""Interactive CLI for controlling azimuth/altitude arrow over serial."""
from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass
from typing import Optional

import serial
from serial import Serial, SerialException


@dataclass
class GearMath:
    """Holds mechanical conversion constants and helpers."""

    motor_steps_per_rev: int = int(32.0 * 64.0)
    microsteps: int = 1
    gear_ratio: float = 50.0 / 13.0

    @property
    def steps_per_motor_rev(self) -> int:
        return self.motor_steps_per_rev * self.microsteps

    @property
    def steps_per_big_gear_rev(self) -> float:
        return self.steps_per_motor_rev * self.gear_ratio

    @property
    def steps_per_big_gear_deg(self) -> float:
        return self.steps_per_big_gear_rev / 360.0

    def deg_to_steps(self, degrees: float) -> int:
        return round(degrees * self.steps_per_big_gear_deg)

    def steps_to_deg(self, steps: int) -> float:
        return steps / self.steps_per_big_gear_deg


@dataclass
class ControllerState:
    a_steps: int = 0
    b_steps: int = 0

    def yaw_deg(self, math: GearMath) -> float:
        return math.steps_to_deg(self.a_steps)

    def pitch_deg(self, math: GearMath) -> float:
        return math.steps_to_deg(self.b_steps - self.a_steps)


@dataclass
class SerialConfig:
    port: Optional[str]
    baudrate: int = 115200
    read_timeout: float = 0.2
    busy_retry_delay: float = 0.5


class ArrowCli:
    def __init__(self, serial_conn: Optional[Serial], math: GearMath, config: SerialConfig, test_mode: bool = False) -> None:
        self.serial = serial_conn
        self.math = math
        self.config = config
        self.state = ControllerState()
        self.test_mode = test_mode

    def run(self) -> None:
        self._print_banner()
        while True:
            try:
                raw = input("Enter azimuth altitude (deg): ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")
                break

            if not raw:
                continue

            lowered = raw.lower()
            if lowered in {"q", "quit", "exit"}:
                print("Goodbye.")
                break

            azimuth_deg, altitude_deg = self._parse_input(raw)
            if azimuth_deg is None:
                continue

            a_target_deg = azimuth_deg
            b_target_deg = azimuth_deg + altitude_deg
            a_target_steps = self.math.deg_to_steps(a_target_deg)
            b_target_steps = self.math.deg_to_steps(b_target_deg)

            print(
                f"Commanding yaw={azimuth_deg:.2f}°, pitch={altitude_deg:.2f}° -> "
                f"A={a_target_steps} steps, B={b_target_steps} steps"
            )
            self._execute_move(a_target_steps, b_target_steps)

    def _parse_input(self, raw: str) -> tuple[Optional[float], Optional[float]]:
        parts = raw.split()
        if len(parts) != 2:
            print("Please provide azimuth and altitude, e.g. '120 15'.")
            return None, None

        try:
            azimuth = float(parts[0]) % 360.0
            altitude = float(parts[1])
        except ValueError:
            print("Inputs must be numeric values.")
            return None, None

        if altitude < -90.0 or altitude > 90.0:
            print("Altitude must be within [-90, 90] degrees.")
            return None, None

        return azimuth, altitude

    def _execute_move(self, a_target: int, b_target: int) -> None:
        command = f"GOTO {a_target} {b_target}\n"
        
        if self.test_mode:
            print(f"[TEST] Sending: {command.strip()}")
            
            # Show simulated movement
            current_a = self.state.a_steps
            current_b = self.state.b_steps
            delta_a = a_target - current_a
            delta_b = b_target - current_b
            
            print(f"[TEST] Simulating motor move:")
            print(f"       Motor A: {current_a} -> {a_target} (delta {delta_a})")
            print(f"       Motor B: {current_b} -> {b_target} (delta {delta_b})")

            self._update_state(a_target, b_target)
            return

        encoded = command.encode("ascii")

        while True:
            try:
                self.serial.write(encoded)
                self.serial.flush()
            except SerialException as exc:
                print(f"Serial write failed: {exc}")
                return

            response = self._await_acceptance()
            if response == "busy":
                print("Controller busy; retrying...")
                time.sleep(self.config.busy_retry_delay)
                continue  # resend command

            if response == "ok":
                print("Move accepted. Waiting for complete...")
                self._wait_for_complete()
                self._update_state(a_target, b_target)
                return

            if response == "complete":
                print("Move already complete.")
                self._update_state(a_target, b_target)
                return

            # response could be None or error string already printed
            return

    def _await_acceptance(self) -> Optional[str]:
        while True:
            line = self._readline()
            if line is None:
                return None

            if line in {"ok", "busy", "complete"}:
                return line

            if line.startswith("error"):
                print(f"Controller error: {line}")
                return None

            print(f"Ignoring unexpected response: {line}")

    def _wait_for_complete(self) -> None:
        while True:
            line = self._readline()
            if line is None:
                continue

            if line == "complete":
                print("Move complete.")
                return

            if line.startswith("error"):
                print(f"Controller error: {line}")
                return

            print(f"Status: {line}")

    def _readline(self) -> Optional[str]:
        try:
            raw = self.serial.readline()
        except SerialException as exc:
            print(f"Serial read failed: {exc}")
            return None

        if not raw:
            return None

        return raw.decode("ascii", errors="ignore").strip().lower()

    def _update_state(self, a_steps: int, b_steps: int) -> None:
        self.state.a_steps = a_steps
        self.state.b_steps = b_steps
        yaw = self.state.yaw_deg(self.math)
        pitch = self.state.pitch_deg(self.math)
        print(
            f"Current state -> yaw={yaw:.2f}°, pitch={pitch:.2f}°, "
            f"A_steps={self.state.a_steps}, B_steps={self.state.b_steps}"
        )

    def _print_banner(self) -> None:
        print("OmniCompass Arrow Controller CLI")
        print("Assuming startup alignment at yaw=0°, pitch=0° (A=0, B=0).")
        print("Enter azimuth altitude in degrees (e.g. '90 10'). Type 'q' to quit.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--port",
        "-p",
        default=os.environ.get("OMNICOMPASS_SERIAL_PORT"),
        help="Serial port path (e.g. /dev/ttyACM0 or COM3).",
    )
    parser.add_argument("--baud", type=int, default=115200, help="Serial baud rate.")
    parser.add_argument(
        "--motor-steps", type=int, default=int(32.0 * 64.0), help="Full steps per motor revolution."
    )
    parser.add_argument(
        "--microsteps", type=int, default=1, help="Microsteps configured on driver."
    )
    parser.add_argument(
        "--gear-ratio",
        type=float,
        default=50.0 / 13.0,
        help="Motor revolutions per big-gear revolution.",
    )
    parser.add_argument(
        "--read-timeout",
        type=float,
        default=0.2,
        help="Serial read timeout in seconds.",
    )
    parser.add_argument(
        "--busy-retry",
        type=float,
        default=0.5,
        help="Delay before resending command after 'busy' response.",
    )
    parser.add_argument(
        "--test",
        "-t",
        action="store_true",
        help="Run in test mode without serial connection.",
    )
    args = parser.parse_args()

    if not args.test and not args.port:
        parser.error("Serial port is required. Use --port or set OMNICOMPASS_SERIAL_PORT.")

    return args


def main() -> int:
    args = parse_args()
    math = GearMath(
        motor_steps_per_rev=args.motor_steps,
        microsteps=args.microsteps,
        gear_ratio=args.gear_ratio,
    )
    config = SerialConfig(
        port=args.port,
        baudrate=args.baud,
        read_timeout=args.read_timeout,
        busy_retry_delay=args.busy_retry,
    )

    if args.test:
        print("Running in TEST mode (no serial connection).")
        cli = ArrowCli(None, math, config, test_mode=True)
        cli.run()
        return 0

    try:
        with serial.Serial(
            port=config.port,
            baudrate=config.baudrate,
            timeout=config.read_timeout,
        ) as ser:
            cli = ArrowCli(ser, math, config)
            cli.run()
    except SerialException as exc:
        print(f"Failed to open serial port: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
