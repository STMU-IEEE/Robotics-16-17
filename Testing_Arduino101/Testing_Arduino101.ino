#include <NewPing.h>

#define TRIGGER_PIN1 2
#define ECHO_PIN1 4

#define TRIGGER_PIN2 5
#define ECHO_PIN2 6

#define TRIGGER_PIN3 7
#define ECHO_PIN3 8

#define TRIGGER_PIN4 10
#define ECHO_PIN4 13

#define MAX_DISTANCE 200

#define LED 13
#define LMOTOR 9
#define RMOTOR 3

NewPing sonar1(TRIGGER_PIN1, ECHO_PIN1, MAX_DISTANCE);
NewPing sonar2(TRIGGER_PIN2, ECHO_PIN2, MAX_DISTANCE);
NewPing sonar3(TRIGGER_PIN3, ECHO_PIN3, MAX_DISTANCE);
NewPing sonar4(TRIGGER_PIN4, ECHO_PIN4, MAX_DISTANCE);

char input;
int conInput;


void setup() {
        Serial.begin(9600);     // opens serial port, sets data rate to 9600 bps
        pinMode(LED, OUTPUT);
}

void loop() {

        // send data only when you receive data:
        if (Serial.available() > 0) {
                // read the incoming byte:
                input = Serial.read(); //single character
                
                Serial.print("I received as a char: ");
                Serial.println(input);

                switch(input){
                  case '0':
                  led_off();
                  break;
                  case '1':
                  led_on();
                  break;
                  case 'f':
                  move_foward();
                  break;
                  case 's':
                  stop_motor();
                  break;
                  case 'u':
                  us_sensor();
                  default:
                  break;
                }
        }
}
void led_on(){
  digitalWrite(LED, HIGH);
  
}
void led_off(){
  digitalWrite(LED, LOW);
}
void move_foward(){
  digitalWrite(LMOTOR, HIGH);
  digitalWrite(RMOTOR, HIGH);
}
void stop_motor(){
  digitalWrite(LMOTOR, LOW);
  digitalWrite(RMOTOR, LOW);
}
void us_sensor(){
  delay(50);
  
  Serial.print("Sensor 1: ");
  Serial.print(sonar1.ping_cm());
  
  Serial.print("Sensor 2: ");
  Serial.print(sonar2.ping_cm());
  
  Serial.print("Sensor 3: ");
  Serial.print(sonar3.ping_cm());
  
  Serial.print("Sensor 4: ");
  Serial.print(sonar4.ping_cm());
  
  delay(50);
  
}
 
