#include <Arduino.h>
#include <AccelStepper.h>
#include <string.h>

namespace {
  constexpr uint32_t kBaudRate = 115200;
  constexpr uint8_t kLineBufferSize = 64;
  // 15 RPM = (15 * 2048) / 60 = ~512 steps/sec
  constexpr float kMaxSpeed = 512.0f;
  constexpr float kMaxAcceleration = 500.0f;

  // 28BYJ-48 with ULN2003 driver uses 4-wire control.
  // Pin order for AccelStepper FULL4WIRE should be IN1, IN3, IN2, IN4.
  constexpr uint8_t kMotorAIn1 = 2;
  constexpr uint8_t kMotorAIn2 = 3;
  constexpr uint8_t kMotorAIn3 = 4;
  constexpr uint8_t kMotorAIn4 = 5;

  constexpr uint8_t kMotorBIn1 = 6;
  constexpr uint8_t kMotorBIn2 = 7;
  constexpr uint8_t kMotorBIn3 = 8;
  constexpr uint8_t kMotorBIn4 = 9;

  AccelStepper stepperA(AccelStepper::FULL4WIRE, kMotorAIn1, kMotorAIn3, kMotorAIn2, kMotorAIn4);
  AccelStepper stepperB(AccelStepper::FULL4WIRE, kMotorBIn1, kMotorBIn3, kMotorBIn2, kMotorBIn4);

  char lineBuffer[kLineBufferSize];
  uint8_t lineLength = 0;
  bool isMoving = false;

  void sendError(const char *message) {
    Serial.print("error ");
    Serial.println(message);
  }

  void resetLineBuffer() {
    lineLength = 0;
    lineBuffer[0] = '\0';
  }

  void handleCommand(char *line) {
    while (*line == ' ' || *line == '\t') {
      ++line;
    }

    if (*line == '\0') {
      return;
    }

    char *command = strtok(line, " \t");
    if (!command) {
      return;
    }

    if (strcasecmp(command, "GOTO") != 0) {
      sendError("invalid command");
      return;
    }

    char *aToken = strtok(nullptr, " \t");
    char *bToken = strtok(nullptr, " \t");
    if (!aToken || !bToken) {
      sendError("invalid command");
      return;
    }

    char *endPtr = nullptr;
    long aSteps = strtol(aToken, &endPtr, 10);
    if (endPtr == aToken || *endPtr != '\0') {
      sendError("invalid command");
      return;
    }

    endPtr = nullptr;
    long bSteps = strtol(bToken, &endPtr, 10);
    if (endPtr == bToken || *endPtr != '\0') {
      sendError("invalid command");
      return;
    }

    if (isMoving && (stepperA.distanceToGo() != 0 || stepperB.distanceToGo() != 0)) {
      Serial.println("busy");
      return;
    }

    stepperA.moveTo(aSteps);
    stepperB.moveTo(bSteps);
    isMoving = true;
    Serial.println("ok");
  }
}

void setup() {
  Serial.begin(kBaudRate);

  stepperA.setMaxSpeed(kMaxSpeed);
  stepperA.setAcceleration(kMaxAcceleration);
  stepperB.setMaxSpeed(kMaxSpeed);
  stepperB.setAcceleration(kMaxAcceleration);

  resetLineBuffer();
}

void loop() {
  while (Serial.available() > 0) {
    char c = static_cast<char>(Serial.read());
    if (c == '\r') {
      continue;
    }

    if (c == '\n') {
      lineBuffer[lineLength] = '\0';
      handleCommand(lineBuffer);
      resetLineBuffer();
      continue;
    }

    if (lineLength < kLineBufferSize - 1) {
      lineBuffer[lineLength++] = c;
    } else {
      sendError("line too long");
      resetLineBuffer();
    }
  }

  stepperA.run();
  stepperB.run();

  if (isMoving && stepperA.distanceToGo() == 0 && stepperB.distanceToGo() == 0) {
    Serial.println("complete");
    isMoving = false;
  }
}