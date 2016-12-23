#include <EnableInterrupt.h>
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
                                    
                                        BACK
                                        Sensor 0 Ard 1
                      -------------------------------------------
                     |                                           |
                     |    BUTTON 2    BUTTON 1      ARD 1        |
                     |     (ARD 2)    (ARD 1)                    |
                     |                                           |
                     |                                           |
                     |                                           |
         RIGHT       |                                           |    LEFT
     SENSOR 1,ARD 2  |                                           |    SENSOR 1, ARD 1
          SERVO      |                                           |    SERVO
                     |                                           |
                     |    ARD 2                    RASPBERRY     |
                     |                                           |
                     |                                           |
                     |                                           |
                      -------------------------------------------
                                        FRONT
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


//------------------SENSORSs------------------
NewPing sonar1(TRIGGER_PIN1, ECHO_PIN1, MAX_DISTANCE);
NewPing sonar2(TRIGGER_PIN2, ECHO_PIN2, MAX_DISTANCE);
Servo myservo;



//------------------VARIABLESs----------------
char input;
int servoH = 0;
long last_time = 0;
int control = 0; 
int stop_button = 10;
int command_status = 1;
int motor_speed[2];


//-------------------FUNCTIONs----------------
void stop_motor_ALL(){
  
    command_status = 0;
    digitalWrite(DIR_A, LOW);
    digitalWrite(DIR_B, LOW);
  
    digitalWrite(AMOTOR, LOW);
    digitalWrite(BMOTOR, LOW);
    
    digitalWrite(AMOTOR_BRAKE, HIGH);
    digitalWrite(BMOTOR_BRAKE, HIGH);
  
}
void move_forward(){

    digitalWrite(DIR_A, HIGH);
    digitalWrite(DIR_B, HIGH);

    digitalWrite(AMOTOR_BRAKE, LOW);
    digitalWrite(BMOTOR_BRAKE, LOW);

    digitalWrite(AMOTOR, HIGH);
    digitalWrite(BMOTOR, HIGH);
}
void variable_forward(){
    while(Serial.available () > 2);//wait for the motor speed info
    motor_speed[0] = Serial.parseInt();//motor A speed
    motor_speed[1] = Serial.parseInt();//motor B speed

    if(motor_speed[0] > 255){
      motor_speed[0] = 255;
    }
    if(motor_speed[1] > 255){
      motor_speed[1] = 255;
    }
    
    digitalWrite(DIR_A, HIGH);
    digitalWrite(DIR_B, HIGH);

    digitalWrite(AMOTOR_BRAKE, LOW);
    digitalWrite(BMOTOR_BRAKE, LOW);

    analogWrite(AMOTOR, motor_speed[0]);
    analogWrite(BMOTOR, motor_speed[1]);
  
}
void move_reverse(){
    digitalWrite(DIR_A, LOW);
    digitalWrite(DIR_B, LOW);


    digitalWrite(AMOTOR_BRAKE, LOW);
    digitalWrite(BMOTOR_BRAKE, LOW);


    digitalWrite(AMOTOR, HIGH);
    digitalWrite(BMOTOR, HIGH);
  
}


void move_in(){
    digitalWrite(DIR_A, HIGH);
    digitalWrite(DIR_B, LOW);


    digitalWrite(AMOTOR_BRAKE, LOW);
    digitalWrite(BMOTOR_BRAKE, LOW);

    digitalWrite(AMOTOR, HIGH);
    digitalWrite(BMOTOR, HIGH);
}

void move_out(){
    digitalWrite(DIR_A, LOW);
    digitalWrite(DIR_B, HIGH);


    digitalWrite(AMOTOR_BRAKE, LOW);
    digitalWrite(BMOTOR_BRAKE, LOW);

    digitalWrite(AMOTOR, HIGH);
    digitalWrite(BMOTOR, HIGH);
}

void stop_motor(){
    digitalWrite(DIR_A, LOW);
    digitalWrite(DIR_B, LOW);
  
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

//------------------CODEs---------------------
void setup() {
        Serial.begin(9600);     // opens serial port, sets data rate to 9600 bps

        myservo.attach(5);
        
        enableInterrupt(stop_button, stop_motor_ALL , CHANGE);
        
  
        
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
               
        Serial.println(AMOTOR);
        Serial.println(BMOTOR);
        Serial.println(AMOTOR_BRAKE);
        Serial.println(BMOTOR_BRAKE);
}

void loop() {      
  command();
}


void command(){

      if (Serial.available() > 0) {
          // read the incoming byte:
          input = Serial.read(); //single character

          

          switch(input){
            
            case 'w':

              if(command_status == 1){
                //move_forward();
                variable_forward();
              }
              break;
              
            case 'r':
              if(command_status == 1){
                move_reverse();
              }
              break;

            case 'o':
              if(command_status == 1){
                move_out();
              }
              break;          

            case 'i':
              if(command_status == 1){
                move_in();
              } 
              break;
              
            case 'x':
              if(command_status == 1){
                stop_motor();
              }
              break;
              
            case 'u':
              if(command_status == 1){
                noInterrupts();
                us_sensor();
                interrupts();
              }
              break;
              
            case 'n':
              if(command_status == 1){
                servo_info();
              }
              break;
              
            case 't':
              if(command_status == 1){
                servo_top();
              }
              break;
              
            case 'b':
              if(command_status == 1){
                servo_bottom();
              }
              break;
              
            case 'p':
              if(command_status == 1){
                servoH++;  
              }
              break;
              
            case 'e':
              if(command_status == 1){
                servoH--;  
              }
              break;            
            case '9':
              command_status = 1;
              break;
            default:
            break;
          }
      }
    
  
}


 
