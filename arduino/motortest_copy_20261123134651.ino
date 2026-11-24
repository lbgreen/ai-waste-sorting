// Sorting trash bin - two 28BYJ-48 steppers with ULN2003 drivers
// No library needed. Gentle start/stop.
//   Flap 1: coils ALWAYS powered (holds its position)
//   Flap 2: coils powered only while open; switched OFF when back at 0
//
// SORTING COMMANDS (Serial Monitor at 9600 baud, or the Python window):
//   P -> paper:      flap 1 to +90 AND flap 2 to 30 at the same time, wait, both back to 0
//   G -> general:    flap 1 to +90, wait, back to 0   (flap 2 stays at 0)
//   R -> recycling:  flap 1 to -90, wait, back to 0   (flap 2 stays at 0)
//   After each one the Arduino sends "DONE".
//
// MANUAL / TEST COMMANDS:
//   A / B  -> flap 1 to +90 / -90 and back
//   C / D  -> flap 2 open to 30 / close to 0
//   + / -  -> nudge flap 1      Z -> "flap 1 is at 0 now"
//   > / <  -> nudge flap 2      X -> "flap 2 is at 0 now"
//
// Wiring:
//   Flap 1 driver: IN1->D8,  IN2->D9,  IN3->D10, IN4->D11
//   Flap 2 driver: IN1->D4,  IN2->D5,  IN3->D6,  IN4->D7
//   Both drivers' + and - -> external 5V supply (about 2 A),
//   with the supply's GND connected to the Arduino GND.
//
// Both flaps: wherever the shaft is at power-on counts as 0 degrees.

// ---------- settings ----------
const long STEPS_PER_REV  = 2048;   // 28BYJ-48 full-step
const int  HOLD_MS        = 1000;   // time the flaps stay open before returning (ms)
const int  FLAP2_ANGLE    = 30;     // flap 2 open angle. Turns the wrong way? Use -30
const int  NUDGE_STEPS    = 10;     // about 1.8 degrees per nudge

// Speed: bigger number = slower = more torque
const long START_DELAY_US = 8000;
const long RUN_DELAY_US   = 4000;
const long RAMP_STEPS     = 80;

// Full-step sequence, two coils on at a time (strongest mode)
const byte SEQ[4][4] = {
  {1, 1, 0, 0},
  {0, 1, 1, 0},
  {0, 0, 1, 1},
  {1, 0, 0, 1}
};

// ---------- one motor ----------
struct Motor {
  int  pins[4];       // IN1, IN2, IN3, IN4
  int  phase;         // which row of SEQ is powered now
  long currentStep;   // position in steps (0 = rest position)
};

Motor m1 = {{8, 9, 10, 11}, 0, 0};
Motor m2 = {{4, 5, 6, 7},   0, 0};

void applyPhase(Motor &m) {
  for (int i = 0; i < 4; i++) {
    digitalWrite(m.pins[i], SEQ[m.phase][i]);
  }
}

void releaseMotor(Motor &m) {        // all coils off (motor goes limp)
  for (int i = 0; i < 4; i++) {
    digitalWrite(m.pins[i], LOW);
  }
}

void stepOnce(Motor &m, int dir) {
  m.phase = (m.phase + dir + 4) % 4;
  applyPhase(m);
  m.currentStep += dir;
}

// Move a number of steps with a gentle start and stop
void moveSteps(Motor &m, long n) {
  if (n == 0) return;
  applyPhase(m);                     // make sure coils are on before moving
  int  dir   = (n > 0) ? 1 : -1;
  long total = abs(n);

  for (long i = 0; i < total; i++) {
    long fromEdge = min(i, total - 1 - i);
    long d;
    if (fromEdge >= RAMP_STEPS) {
      d = RUN_DELAY_US;
    } else {
      d = START_DELAY_US - (START_DELAY_US - RUN_DELAY_US) * fromEdge / RAMP_STEPS;
    }
    stepOnce(m, dir);
    delayMicroseconds(d);
  }
}

// Move BOTH flaps at the same time. They start together and finish together:
// the motor with the longer move sets the pace, the other one steps in between.
void moveBoth(int angle1, int angle2) {
  long d1 = (long)angle1 * STEPS_PER_REV / 360 - m1.currentStep;
  long d2 = (long)angle2 * STEPS_PER_REV / 360 - m2.currentStep;
  int  dir1 = (d1 > 0) ? 1 : -1;
  int  dir2 = (d2 > 0) ? 1 : -1;
  long n1 = abs(d1);
  long n2 = abs(d2);
  long total = max(n1, n2);
  if (total == 0) return;

  if (n1 > 0) applyPhase(m1);        // make sure coils are on before moving
  if (n2 > 0) applyPhase(m2);

  long done1 = 0, done2 = 0;
  for (long i = 0; i < total; i++) {
    // how many steps each motor should have done by now
    if (done1 < (i + 1) * n1 / total) { stepOnce(m1, dir1); done1++; }
    if (done2 < (i + 1) * n2 / total) { stepOnce(m2, dir2); done2++; }

    long fromEdge = min(i, total - 1 - i);
    long d;
    if (fromEdge >= RAMP_STEPS) {
      d = RUN_DELAY_US;
    } else {
      d = START_DELAY_US - (START_DELAY_US - RUN_DELAY_US) * fromEdge / RAMP_STEPS;
    }
    delayMicroseconds(d);
  }
}

void moveToAngle(Motor &m, int angle) {
  long target = (long)angle * STEPS_PER_REV / 360;
  moveSteps(m, target - m.currentStep);
}

// ---------- flap 2 helpers ----------
void openFlap2() {
  Serial.println("Flap 2 -> open");
  moveToAngle(m2, FLAP2_ANGLE);      // stays powered while open
}

void closeFlap2() {
  Serial.println("Flap 2 -> 0");
  moveToAngle(m2, 0);
  delay(100);                        // let it settle
  releaseMotor(m2);                  // no power needed at 0
}

// ---------- flap 1 helper ----------
void flap1TipAndReturn(int angle) {
  Serial.print("Flap 1 -> ");
  Serial.println(angle);
  moveToAngle(m1, angle);
  delay(HOLD_MS);
  Serial.println("Flap 1 -> 0");
  moveToAngle(m1, 0);                // stays powered (holds at 0)
}

// ---------- sorting sequences ----------
void sortPaper() {
  Serial.println("PAPER");
  moveBoth(90, FLAP2_ANGLE);         // flap 1 -> +90 and flap 2 -> 30 at the same time
  delay(HOLD_MS);
  moveBoth(0, 0);                    // both back to 0 at the same time
  delay(100);                        // let flap 2 settle
  releaseMotor(m2);                  // flap 2: no power at 0 (flap 1 keeps holding)
  Serial.println("DONE");
}

void sortGeneral() {
  Serial.println("GENERAL");
  flap1TipAndReturn(90);
  Serial.println("DONE");
}

void sortRecycling() {
  Serial.println("RECYCLING");
  flap1TipAndReturn(-90);
  Serial.println("DONE");
}

void setup() {
  for (int i = 0; i < 4; i++) {
    pinMode(m1.pins[i], OUTPUT);
    pinMode(m2.pins[i], OUTPUT);
  }
  applyPhase(m1);     // flap 1 holds from power-on
  releaseMotor(m2);   // flap 2 is off at 0
  Serial.begin(9600);
  Serial.println("Ready. P = paper, G = general, R = recycling");
}

void loop() {
  if (Serial.available() > 0) {
    char c = Serial.read();

    switch (c) {
      // ----- sorting -----
      case 'P': case 'p': sortPaper();     break;
      case 'G': case 'g': sortGeneral();   break;
      case 'R': case 'r': sortRecycling(); break;

      // ----- manual flap 1 -----
      case 'A': case 'a': flap1TipAndReturn(90);  Serial.println("DONE"); break;
      case 'B': case 'b': flap1TipAndReturn(-90); Serial.println("DONE"); break;
      case '+': moveSteps(m1,  NUDGE_STEPS); Serial.println("Flap 1 nudged +"); break;
      case '-': moveSteps(m1, -NUDGE_STEPS); Serial.println("Flap 1 nudged -"); break;
      case 'Z': case 'z': m1.currentStep = 0; Serial.println("Flap 1 zero set"); break;

      // ----- manual flap 2 -----
      case 'C': case 'c': openFlap2();  Serial.println("DONE"); break;
      case 'D': case 'd': closeFlap2(); Serial.println("DONE"); break;
      case '>': moveSteps(m2,  NUDGE_STEPS); Serial.println("Flap 2 nudged +"); break;
      case '<': moveSteps(m2, -NUDGE_STEPS); Serial.println("Flap 2 nudged -"); break;
      case 'X': case 'x':
        m2.currentStep = 0;
        releaseMotor(m2);
        Serial.println("Flap 2 zero set");
        break;
    }

    // throw away anything sent while a motor was moving
    while (Serial.available() > 0) {
      Serial.read();
    }
  }
}
