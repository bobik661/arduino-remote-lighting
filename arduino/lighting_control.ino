// Arduino Uno: управление нагрузкой на D8 командами ON/OFF по USB Serial.
const byte LIGHT_PIN = 8;
String inputLine = "";
void setup() {
  pinMode(LIGHT_PIN, OUTPUT);
  digitalWrite(LIGHT_PIN, LOW);
  Serial.begin(9600);
  inputLine.reserve(16);
  Serial.println("READY");
}
void loop() {
  while (Serial.available() > 0) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      inputLine.trim(); inputLine.toUpperCase();
      if (inputLine == "ON") { digitalWrite(LIGHT_PIN, HIGH); Serial.println("STATE:ON"); }
      else if (inputLine == "OFF") { digitalWrite(LIGHT_PIN, LOW); Serial.println("STATE:OFF"); }
      inputLine = "";
    } else if (inputLine.length() < 16) inputLine += c;
  }
}
