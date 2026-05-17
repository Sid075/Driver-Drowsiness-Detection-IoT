int IN1 = 8;
int IN2 = 9;
int ENA = 10;

int LED = 7;

void setup() {

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(LED, OUTPUT);

  Serial.begin(9600);

  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  analogWrite(ENA, 255);

  digitalWrite(LED, LOW);
}

void loop() {

  if (Serial.available()) {

    char level = Serial.read();

    if (level == '0') {

      analogWrite(ENA, 255);
      digitalWrite(LED, LOW);
    }

    else if (level == '1') {

      analogWrite(ENA, 255);
      digitalWrite(LED, LOW);
    }

    else if (level == '2') {

      analogWrite(ENA, 180);
      digitalWrite(LED, LOW);
    }

    else if (level == '3') {

      analogWrite(ENA, 100);

      digitalWrite(LED, HIGH);
      delay(400);
      digitalWrite(LED, LOW);
      delay(400);
    }

    else if (level == '4') {

      analogWrite(ENA, 0);

      digitalWrite(LED, HIGH);
      delay(120);
      digitalWrite(LED, LOW);
      delay(120);
    }
  }
}
