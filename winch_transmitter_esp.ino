const int inputPinDown = 13;
const int inputPinUp = 12;

const int outputPinDown = 27;
const int outputPinUp = 26;
const int outputPinIdle = 25;
int currentOutputPin;

const int ledPin = 17;

int inputStateDown = HIGH;
int inputStateUp = HIGH;

// Pairing button
unsigned long buttonPressTime = 0;
const int buttonPin = 4;

void setup() {
  pinMode(inputPinDown, INPUT_PULLUP);
  pinMode(inputPinUp, INPUT_PULLUP);
  pinMode(outputPinDown, OUTPUT);
  pinMode(outputPinUp, OUTPUT);
  pinMode(outputPinIdle, OUTPUT);
  currentOutputPin = outputPinIdle;

  digitalWrite(outputPinDown, HIGH);
  digitalWrite(outputPinUp, HIGH);
  digitalWrite(outputPinIdle, HIGH);

  pinMode(ledPin, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);
}

void setOutputPin() {
  inputStateDown = digitalRead(inputPinDown);
  inputStateUp = digitalRead(inputPinUp);

  if (inputStateDown == LOW) {
    currentOutputPin = outputPinDown;
  }
  else if (inputStateUp == LOW) {
    currentOutputPin = outputPinUp;     
  }
  else {
    currentOutputPin = outputPinIdle;
  }
}

void sendSignal() {
  digitalWrite(currentOutputPin, LOW);
  digitalWrite(ledPin, HIGH);
  delay(100);
  digitalWrite(currentOutputPin, HIGH);
  digitalWrite(ledPin, LOW);
  delay(200);
}

void checkButtonHold() {
  if (digitalRead(buttonPin) == LOW) {
    unsigned long currentTime = millis();
    if (currentTime - buttonPressTime > 2000) {
      pairingMode();
    }
  } 
  else {
    buttonPressTime = millis();
  }
}

void pairingMode() {
  digitalWrite(ledPin, HIGH);

  // Wait for user to release held button
  while (true) {
    if (digitalRead(buttonPin) == HIGH) { 
      break;
    delay(200);
    }
  }

  // Enter pairing mode
  bool buttonHeld = false;
  while (true) {
    digitalWrite(ledPin, HIGH);
    
    if (buttonHeld) {
      break;
    }

    if (digitalRead(buttonPin) == HIGH) {
      delay(50);
      continue;
    }

    unsigned long startTime = millis();
    while (digitalRead(buttonPin) == LOW) {
      if (millis() - startTime > 2000) {
        buttonHeld = true;
        digitalWrite(ledPin, LOW);
      }
      delay(50);
    }

    if (!buttonHeld) {
      setOutputPin();
      sendSignal();
    }
  }
}

void loop() {
  checkButtonHold();
  setOutputPin();
  sendSignal();
}
