int LED = 13;
int state = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  pinMode(LED, OUTPUT);

}

void loop() {
  // put your main code here, to run repeatedly:

  commands();

}

void commands(){
  if(Serial.available() > 0){

    int input = Serial.read();

    switch(input){

      case '1':
        light_on();
        break;
      case '0':
        light_off();
        break;
      case 's':
        delay(10);
        light_state();
    }
  }
}

void light_on(){
  digitalWrite(LED, HIGH);
  
}
void light_off(){
  digitalWrite(LED, LOW);
  
}
void light_state(){
  state = digitalRead(LED);
  
  if(state == HIGH){
    Serial.print("1");
  }
  if(state == LOW){
    Serial.print("0");
  }
  
}

