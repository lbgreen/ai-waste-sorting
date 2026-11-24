// Manual sorting-bin hardware test. No camera/AI connection.
// Each 28BYJ-48 motor needs its own ULN2003 driver and an external 5 V supply.
// Flap 1: IN1..IN4 -> D8,D9,D10,D11.
// Flap 2, first driver:  IN1..IN4 -> D4,D5,D6,D7.
// Flap 2, second driver: IN1..IN4 -> D7,D6,D5,D4 (opposite rotation).
// Share supply ground with Arduino GND. Never join motor output pins.
// Check both shafts' directions before connecting them mechanically.
// At every reset the current shaft positions are ASSUMED to be 0 degrees.

const long STEPS_PER_REV = 2048;  // nominal 28BYJ-48 full-step output revolution
const int HOLD_MS = 1000;
const int FLAP2_ANGLE = 30;        // change sign if opening direction is reversed
const int NUDGE_STEPS = 10;
const int FLAP1_LIMIT = 90;
const int FLAP2_LIMIT = 30;
const unsigned long POSITION_INTERVAL_MS = 80;

// Larger delay means lower speed; tune only after an unloaded direction test.
const long START_DELAY_US = 8000;
const long RUN_DELAY_US = 4000;
const long RAMP_STEPS = 80;

const byte SEQ[4][4] = {
  {1, 1, 0, 0},
  {0, 1, 1, 0},
  {0, 0, 1, 1},
  {1, 0, 0, 1}
};

struct Motor {
  byte pins[4];
  byte phase;
  long currentStep;
};

Motor m1 = {{8, 9, 10, 11}, 0, 0};
Motor m2 = {{4, 5, 6, 7}, 0, 0};
bool stopRequested = false;
unsigned long lastPositionMs = 0;

long angleToSteps(int angle) {
  return (long)angle * STEPS_PER_REV / 360;
}

void applyPhase(Motor &m) {
  for (byte i = 0; i < 4; i++) digitalWrite(m.pins[i], SEQ[m.phase][i]);
}

void releaseMotor(Motor &m) {
  for (byte i = 0; i < 4; i++) digitalWrite(m.pins[i], LOW);
}

void publishPosition(bool force = false) {
  unsigned long now = millis();
  if (!force && now - lastPositionMs < POSITION_INTERVAL_MS) return;
  Serial.print(F("POS "));
  Serial.print(m1.currentStep);
  Serial.print(' ');
  Serial.println(m2.currentStep);
  lastPositionMs = now;
}

// During a move, only ! is accepted. Other queued commands are discarded.
void pollStop() {
  while (Serial.available() > 0) {
    if (Serial.read() == '!') stopRequested = true;
  }
}

void stepOnce(Motor &m, int dir) {
  m.phase = (m.phase + dir + 4) % 4;
  applyPhase(m);
  m.currentStep += dir;
}

long stepDelay(long index, long total) {
  long fromEdge = min(index, total - 1 - index);
  if (fromEdge >= RAMP_STEPS) return RUN_DELAY_US;
  return START_DELAY_US - (START_DELAY_US - RUN_DELAY_US) * fromEdge / RAMP_STEPS;
}

bool moveSteps(Motor &m, long delta) {
  if (delta == 0) return true;
  applyPhase(m);
  int dir = delta > 0 ? 1 : -1;
  long total = abs(delta);
  for (long i = 0; i < total; i++) {
    pollStop();
    if (stopRequested) return false;
    stepOnce(m, dir);
    publishPosition();
    delayMicroseconds(stepDelay(i, total));
  }
  return true;
}

bool moveToAngle(Motor &m, int angle) {
  return moveSteps(m, angleToSteps(angle) - m.currentStep);
}

// Interleave steps so both flaps start and finish together.
bool moveBoth(int angle1, int angle2) {
  long d1 = angleToSteps(angle1) - m1.currentStep;
  long d2 = angleToSteps(angle2) - m2.currentStep;
  long n1 = abs(d1), n2 = abs(d2);
  long total = max(n1, n2);
  if (total == 0) return true;
  if (n1 > 0) applyPhase(m1);
  if (n2 > 0) applyPhase(m2);
  long done1 = 0, done2 = 0;
  for (long i = 0; i < total; i++) {
    pollStop();
    if (stopRequested) return false;
    if (done1 < (i + 1) * n1 / total) {
      stepOnce(m1, d1 > 0 ? 1 : -1);
      done1++;
    }
    if (done2 < (i + 1) * n2 / total) {
      stepOnce(m2, d2 > 0 ? 1 : -1);
      done2++;
    }
    publishPosition();
    delayMicroseconds(stepDelay(i, total));
  }
  return true;
}

bool holdOpen() {
  unsigned long start = millis();
  while (millis() - start < HOLD_MS) {
    pollStop();
    if (stopRequested) return false;
    delay(5);
  }
  return true;
}

void finishCommand(bool completed) {
  if (m2.currentStep == 0) releaseMotor(m2);
  publishPosition(true);
  Serial.println(completed ? F("DONE") : F("STOPPED"));
}

bool atHome() {
  return m1.currentStep == 0 && m2.currentStep == 0;
}

void reject(const __FlashStringHelper *reason) {
  Serial.print(F("ERROR "));
  Serial.println(reason);
  publishPosition(true);
  Serial.println(F("DONE"));
}

void setup() {
  for (byte i = 0; i < 4; i++) {
    pinMode(m1.pins[i], OUTPUT);
    pinMode(m2.pins[i], OUTPUT);
  }
  applyPhase(m1);    // flap 1 keeps holding at its assumed zero
  releaseMotor(m2);  // flap 2 has no holding torque at zero
  Serial.begin(9600);
  Serial.println(F("READY"));
  publishPosition(true);
}

void loop() {
  if (Serial.available() == 0) return;
  char c = Serial.read();
  if (c == '\n' || c == '\r') return;
  if (c == '?') {
    Serial.println(F("READY"));
    publishPosition(true);
    return;
  }
  if (c == '!') {
    publishPosition(true);
    Serial.println(F("STOPPED"));
    return;
  }

  stopRequested = false;
  bool completed = true;
  switch (c) {
    case 'P': case 'p':
    case 'G': case 'g':
    case 'R': case 'r':
      if (!atHome()) { reject(F("NOT_HOME")); return; }
      Serial.println(F("BUSY"));
      if (c == 'P' || c == 'p') {
        completed = moveBoth(90, FLAP2_ANGLE) && holdOpen() && moveBoth(0, 0);
      } else {
        int angle = (c == 'G' || c == 'g') ? 90 : -90;
        completed = moveToAngle(m1, angle) && holdOpen() && moveToAngle(m1, 0);
      }
      break;
    case '1': completed = moveToAngle(m1, 90); break;
    case '2': completed = moveToAngle(m1, -90); break;
    case '0': completed = moveToAngle(m1, 0); break;
    case '3': case 'C': case 'c': completed = moveToAngle(m2, FLAP2_ANGLE); break;
    case '4': case 'D': case 'd': completed = moveToAngle(m2, 0); break;
    case 'A': case 'a':
    case 'B': case 'b': {
      int angle = (c == 'A' || c == 'a') ? 90 : -90;
      completed = moveToAngle(m1, angle) && holdOpen() && moveToAngle(m1, 0);
      break;
    }
    case '+': case '-': {
      long target = m1.currentStep + (c == '+' ? NUDGE_STEPS : -NUDGE_STEPS);
      if (abs(target) > angleToSteps(FLAP1_LIMIT)) { reject(F("FLAP1_LIMIT")); return; }
      completed = moveSteps(m1, target - m1.currentStep);
      break;
    }
    case '>': case '<': {
      long target = m2.currentStep + (c == '>' ? NUDGE_STEPS : -NUDGE_STEPS);
      if (abs(target) > angleToSteps(FLAP2_LIMIT)) { reject(F("FLAP2_LIMIT")); return; }
      completed = moveSteps(m2, target - m2.currentStep);
      break;
    }
    case 'Z': case 'z': m1.currentStep = 0; break;
    case 'X': case 'x': m2.currentStep = 0; break;
    default: reject(F("UNKNOWN_COMMAND")); return;
  }
  finishCommand(completed);
}
