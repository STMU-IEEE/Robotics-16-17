#include <BMI160.h>
#include <CurieIMU.h>

#include <NewPing.h>
#include <Servo.h>

//--------------ORIENTATION------------------ 
/*
 *                          MAP LAYOUT
          A     B      C     D     E     F     G
          -------------------------------------------
    1    |     |      |     |     |     |     |      |
         |     |      |     |     |     |     |      |
         |-------------------------------------------|                                       
    2    |     |      |     |     |     |     |      |
         |     |      |     |     |     |     |      |
         |-------------------------------------------| 
    3    |     |      |     |     |     |     |      | 
         |     |      |     |     |     |     |      |
         |-------------------------------------------|                                       
    4    |     |      |     |     |     |     |      |
         |     |      |     |     |     |     |      |
         |-------------------------------------------|                                       
    5    |     |      |     |     |     |     |      |
         |     |      |     |     |     |     |      |
         |-------------------------------------------| 
    6    |     |      |     |     |     |     |      |
         |     |      |     |     |     |     |      |
         |-------------------------------------------|                                       
    7    |START|      |     |     |     |     |      |
         |STOP |      |     |     |     |     |      |
          -------------------------------------------


                      DIRECTIONALITY OF THE CODE RESPECTLY TO THE MAP
                      
                            W
                            ^
                            |
                            |
                A     <-----|----->    D
                            |
                            |
                            V
                            S
                
                                    ROBOT LAYOUT LEVEL 1
                                    
                                        FRONT
                                        Sensor 0 Ard 1
                      -------------------------------------------
                     |                                           |
                     |    BUTTON 2    BUTTON 1      ARD 1        |
                     |     (ARD 2)    (ARD 1)                    |
                     |                                           |
                     |                                           |
                     |                                           |
         LEFT        |                                           |    RIGHT
     SENSOR 1,ARD 2  |                                           |    SENSOR 1, ARD 1
          SERVO      |                                           |    SERVO
                     |                                           |
                     |    ARD 2                    RASPBERRY     |
                     |                                           |
                     |                                           |
                     |                                           |
                      -------------------------------------------
                                        BACK
                                        Sensor 0 Ard 2



                            
 */





      
//------------------PINs---------------------
#define TRIGGER_PIN1 0
#define ECHO_PIN1 1

#define TRIGGER_PIN2 2
#define ECHO_PIN2 4

#define MAX_DISTANCE 200


#define DIR_A 12
#define DIR_B 13

#define BMOTOR 11
#define AMOTOR 3

#define AMOTOR_BRAKE 9
#define BMOTOR_BRAKE 8  

#define false 0
#define true 1

//------------------SENSORSs------------------
NewPing sonar1(TRIGGER_PIN1, ECHO_PIN1, MAX_DISTANCE);
NewPing sonar2(TRIGGER_PIN2, ECHO_PIN2, MAX_DISTANCE);
Servo myservo;


//------------------VARIABLESs----------------
char input;
int servoH = 0;
int command_enabled = 1;
long last_time = 0;
int control = 0; 



//------------------CODEs---------------------
void setup() {
        Serial.begin(9600);     // opens serial port, sets data rate to 9600 bps

        myservo.attach(5);
        
  
        
        pinMode(AMOTOR, OUTPUT);
        pinMode(BMOTOR, OUTPUT);
        pinMode(AMOTOR_BRAKE, OUTPUT);
        pinMode(BMOTOR_BRAKE, OUTPUT);
        pinMode(DIR_A, OUTPUT);
        pinMode(DIR_B, OUTPUT);
        
        pinMode(TRIGGER_PIN1, OUTPUT);
        pinMode(ECHO_PIN1, INPUT);
        pinMode(TRIGGER_PIN2, OUTPUT);
        pinMode(ECHO_PIN2, INPUT);

        attachInterrupt(digitalPinToInterrupt(BUTTON), button_pressed, RISING);
               
        Serial.println(AMOTOR);
        Serial.println(BMOTOR);
        Serial.println(AMOTOR_BRAKE);
        Serial.println(BMOTOR_BRAKE);

        //Arduino 101 Stuff
}

void loop() {
  
  //if(digitalRead(BUTTON) == HIGH){
    //button_pressed();
  //}
  
commands();
  
       
  
}


void commands(){
    if (Serial.available() > 0) {
          // read the incoming byte:
          input = Serial.read(); //single character
          
          //Serial.print("I received as a char: ");
          //Serial.println(input);

          switch(input){
            
            case 'w':
              move_foward();
              break;
            case 'r':
              move_reverse();
              break;
            case 'i':
              move_in();
              break;
            case 'o':
              move_out();
              break;
            case 'x':
              stop_motor();
              break;
            case 'u':
              noInterrupts();
              us_sensor();
              interrupts();
              break;
            case 'n':
              servo_info();
              break;
            case 't':
              servo_top();
              break;
            case 'b':
              servo_bottom();
              break;
            case 'p':
              servoH++;
              break;
            case 'n':
              servoH--;
              break;
              
            default:
            break;
          }
    }
  
}

void move_foward(){

    digitalWrite(DIR_A, HIGH);
    digitalWrite(DIR_B, HIGH);

    digitalWrite(AMOTOR_BRAKE, LOW);
    digitalWrite(BMOTOR_BRAKE, LOW);

    digitalWrite(AMOTOR, HIGH);
    digitalWrite(BMOTOR, HIGH);
    
    
  
}
void move_reverse(){
    digitalWrite(DIR_A, LOW);
    digitalWrite(DIR_B, LOW);


    digitalWrite(AMOTOR_BRAKE, LOW);
    digitalWrite(BMOTOR_BRAKE, LOW);


    digitalWrite(AMOTOR, HIGH);
    digitalWrite(BMOTOR, HIGH);
  
}

void move_right(){
    digitalWrite(DIR_A, HIGH);
    digitalWrite(DIR_B, LOW);

    digitalWrite(AMOTOR_BRAKE, LOW);
    digitalWrite(BMOTOR_BRAKE, LOW);

    digitalWrite(AMOTOR, HIGH);
    digitalWrite(BMOTOR, HIGH);
}

void move_left(){
    digitalWrite(DIR_A, LOW);
    digitalWrite(DIR_B, HIGH);

    digitalWrite(AMOTOR_BRAKE, LOW);
    digitalWrite(BMOTOR_BRAKE, LOW);

    digitalWrite(AMOTOR, HIGH);
    digitalWrite(BMOTOR, HIGH);
}

void stop_motor(){
  
  
    digitalWrite(AMOTOR, LOW);
    digitalWrite(BMOTOR, LOW);
    
    digitalWrite(AMOTOR_BRAKE, HIGH);
    digitalWrite(BMOTOR_BRAKE, HIGH);
  
}

void us_sensor(){
  delay(50);
  
  Serial.print("Sensor 1: ");
  Serial.print(sonar1.ping_cm());

  Serial.print("Sensor 2: ");
  Serial.print(sonar2.ping_cm());
  Serial.print("\n");
  
  
  delay(50);
  
}
void servo_info(){
  Serial.println(myservo.read());
}
void servo_bottom(){
  myservo.write(0);
}
void servo_top(){
  myservo.write(servoH);
}

 
