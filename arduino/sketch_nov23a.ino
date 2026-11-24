// TEST: flap 2 only (28BYJ-48 + ULN2003)
// Repeats forever: 0 -> 40 degrees, wait, back to 0, wait
// Coils are powered while moving and while open, switched OFF at 0.
//
// Wiring (flap 2 driver -> Arduino):
//   IN1 -> D4
//   IN2 -> D5
//   IN3 -> D6
//   IN4 -> D7
//   +   -> external 5V supply, GND shared with the Arduino
//   -   -> GND
//
// Wherever the shaft is at power-on counts as 0 degrees.
// Open the Serial Monitor (9600 baud) to see what it is doing.

const int  PINS[4]        = {4, 5, 6, 7};   // IN1, IN2, IN3, IN4
const int  OPEN_ANGLE     = 40;             // turns the wrong way? use -40
const int  PAUSE_MS       = 5000;           // wait at each position (ms) = 5 seconds

const long STEPS_PER_REV  = 2048;           // 28BYJ-48 full-step
const long START_DELAY_US = 8000;           // bigger = slower = more torque
const long RUN_DELAY_US   = 4000;
const long RAMP_STEPS     = 80;

const byte SEQ[4][4] = {
  {1, 1, 0, 0},
  {0, 1, 1, 0},
  {0, 0, 1, 1},
  {1, 0, 0, 1}
};

int  phase       = 0;
long currentStep = 0;

void applyPhase() {
  for (int i = 0; i < 4; i++) digitalWrite(PINS[i], SEQ[phase][i]);
}

void releaseMotor() {
  for (int i = 0; i < 4; i++) digitalWrite(PINS[i], LOW);
}

void moveToAngle(int angle) {
  long n = (long)angle * STEPS_PER_REV / 360 - currentStep;
  if (n == 0) return;
  applyPhase();
  int  dir   = (n > 0) ? 1 : -1;
  long total = abs(n);

  for (long i = 0; i < total; i++) {
    long fromEdge = min(i, total - 1 - i);
    long d = (fromEdge >= RAMP_STEPS)
             ? RUN_DELAY_US
             : START_DELAY_US - (START_DELAY_US - RUN_DELAY_US) * fromEdge / RAMP_STEPS;
    phase = (phase + dir + 4) % 4;
    applyPhase();
    currentStep += dir;
    delayMicroseconds(d);
  }
}

void setup() {
  for (int i = 0; i < 4; i++) pinMode(PINS[i], OUTPUT);
  releaseMotor();
  Serial.begin(9600);
  Serial.println("Flap 2 test: 0 <-> 40 degrees");
}

void loop() {
  Serial.println("at 0, waiting 5 s");
  delay(PAUSE_MS);          // wait at 0 (coils off)

  Serial.println("-> 40");
  moveToAngle(OPEN_ANGLE);
  Serial.println("at 40, waiting 5 s");
  delay(PAUSE_MS);          // wait at 40 (stays powered)

  Serial.println("-> 0");
  moveToAngle(0);
  delay(100);
  releaseMotor();           // no power at 0
}
