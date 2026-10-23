// Arduino Nano 33 BLE Sense Rev2
// Collect 8192 samples at a target of 10 kHz, then transmit over USB Serial.
// NOTE: micros()-scheduled analogRead is not hardware-timed ADC sampling.
#define ADC_PIN A0
#define SAMPLE_RATE 10000UL
#define NUM_SAMPLES 4096
#define SAMPLE_INTERVAL (1000000UL / SAMPLE_RATE)  // 100 us, NOT 200 us!

uint16_t samples[NUM_SAMPLES];

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  while (!Serial) {
    delay(10);
  }
  Serial.println("READY - Send s to start sampling");
}

void loop() {
  if (!Serial.available()) return;
  char command = Serial.read();
  if (command != 's' && command != 'S') return;

  uint32_t nextSample = micros() + 2000UL;
  uint32_t overruns = 0;
  for (int i = 0; i < NUM_SAMPLES; i++) {
    while ((int32_t)(micros() - nextSample) < 0) {
      // Wait until the scheduled time for this sample.
    }
    samples[i] = analogRead(ADC_PIN);
    nextSample += SAMPLE_INTERVAL;
    if ((int32_t)(micros() - nextSample) > 0) {
      overruns++;
    }
  }

  // Do not print during the acquisition loop: transfer after capture.
  Serial.print("START,");
  Serial.print(SAMPLE_RATE);
  Serial.print(",");
  Serial.println(NUM_SAMPLES);

  for (int i = 0; i < NUM_SAMPLES; i++) {
    Serial.println(samples[i]);
  }

  Serial.print("END,");
  Serial.println(overruns);
  Serial.println("READY - Send s to start sampling");
}
