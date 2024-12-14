#define TREBLE1 11
#define TREBLE2 10
#define BASS_R 9
#define BASS_L 8

void bassOn(int intensity){
  analogWrite(BASS_R, intensity);
  digitalWrite(BASS_L, LOW);
}

void bassBreak(){
  digitalWrite(BASS_R,LOW);
  digitalWrite(BASS_L, HIGH);
  delay(50);
  digitalWrite(BASS_L,LOW);
}

void setup() {
  Serial.begin(9600);
  pinMode(TREBLE1, OUTPUT);
  pinMode(TREBLE2, OUTPUT);
  pinMode(BASS_R, OUTPUT);
  pinMode(BASS_L, OUTPUT);
  digitalWrite(TREBLE1, LOW);
  digitalWrite(TREBLE2, LOW);
  digitalWrite(BASS_R, LOW);
  digitalWrite(BASS_L, LOW);
  digitalWrite(1,LOW);
  //testaBaixo();

}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    //Serial.println(command);
    if(command.startsWith("on")) {
      digitalWrite(TREBLE1, HIGH);
      digitalWrite(TREBLE2, HIGH);
      }
    else if(command.startsWith("off")) {
      digitalWrite(TREBLE1, LOW);
      digitalWrite(TREBLE2, LOW);
      }
    else if(command=="bass off") bassBreak();
    else if(command.startsWith("bass")) bassOn(command.substring(5).toInt());
  }
}