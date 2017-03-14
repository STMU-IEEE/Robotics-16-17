#include <CapacitiveSensor.h>
#include <EnableInterrupt.h>
#include <NewPing.h>
#include <Servo.h>
#include <Wire.h>
#include <I2CEncoder.h>

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
                                        SENSOR 1 ARD 1
                      -------------------------------------------
                     |                                           |
                     |    BUTTON 2    BUTTON 1      ARD 1        |
                     |     (ARD 2)    (ARD 1)                    |
                     |                                           |
                     |                                           |
                     |                                           |
         RIGHT       |                                           |    LEFT
     SENSOR 2,ARD 2  |                                           |    SENSOR 2, ARD 1
          SERVO      |                                           |    SERVO
                     |                                           |
                     |    ARD 2                    RASPBERRY     |
                     |                                           |
                     |                                           |
                     |                                           |
                      -------------------------------------------
                                        FRONT
                                        SENSOR 1 ARD 2



                            
 */





      
//------------------PINs---------------------
#define TRIGGER_PIN1 A2
#define ECHO_PIN1 2

//DO NOT USE PIN 1, IT CAUSES CONSTANT ZEROS
//DO NOT USE PIN 2 as an ECHO, IT WILL ALSO CAUSE CONSTANT ZEROS 
#define TRIGGER_PIN2 4
#define ECHO_PIN2 A3

#define MAX_DISTANCE 200


#define DIR_A 12
#define DIR_B 13

#define BMOTOR 11
#define AMOTOR 3

#define AMOTOR_BRAKE 9
#define BMOTOR_BRAKE 8 

#define ULTRA_FREQUENCY 10

#define CAP_REC 7
#define CAP_SEND 6



//------------------SENSORSs------------------
NewPing sonar1(TRIGGER_PIN1, ECHO_PIN1, MAX_DISTANCE);
NewPing sonar2(TRIGGER_PIN2, ECHO_PIN2, MAX_DISTANCE);
Servo myservo;
I2CEncoder encoder_B;
I2CEncoder encoder_A;
CapacitiveSensor capSense = CapacitiveSensor(CAP_SEND,CAP_REC); // (send_pin, receive_pin);



//------------------VARIABLESs----------------
char input, trash_input;
int servoH_top = 170, servoH_bottom = 0;
long last_time = 0;
int control = 0; 
int stop_button = 10;
int command_status = 1;
int motor_speed[2];
int ultrasonic1 = 0, ultrasonic2 = 0;

//-------------------FUNCTIONs----------------
void stop_motor_ALL(){
  
    command_status = 0;
    digitalWrite(DIR_A, LOW);
    digitalWrite(DIR_B, LOW);
  
    digitalWrite(AMOTOR, LOW);
    digitalWrite(BMOTOR, LOW);
    
    digitalWrite(AMOTOR_BRAKE, HIGH);
    digitalWrite(BMOTOR_BRAKE, HIGH);

    while(Serial.available() > 0){
      trash_input = Serial.read();
    }
  
}
/*
void move_forward(){

    digitalWrite(DIR_A, HIGH);
    digitalWrite(DIR_B, HIGH);

    digitalWrite(AMOTOR_BRAKE, LOW);
    digitalWrite(BMOTOR_BRAKE, LOW);

    digitalWrite(AMOTOR, HIGH);
    digitalWrite(BMOTOR, HIGH);
}
*/
void variable_forward(){
    while(Serial.available () < 2);//wait for the motor speed info
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
/*
void move_reverse(){
    digitalWrite(DIR_A, LOW);
    digitalWrite(DIR_B, LOW);


    digitalWrite(AMOTOR_BRAKE, LOW);
    digitalWrite(BMOTOR_BRAKE, LOW);


    digitalWrite(AMOTOR, HIGH);
    digitalWrite(BMOTOR, HIGH);
}
*/
void variable_reverse(){
    while(Serial.available () < 2);//wait for the motor speed info
    motor_speed[0] = Serial.parseInt();//motor A speed
    motor_speed[1] = Serial.parseInt();//motor B speed

    if(motor_speed[0] > 255){
      motor_speed[0] = 255;
    }
    if(motor_speed[1] > 255){
      motor_speed[1] = 255;
    }
    
    digitalWrite(DIR_A, LOW);
    digitalWrite(DIR_B, LOW);

    digitalWrite(AMOTOR_BRAKE, LOW);
    digitalWrite(BMOTOR_BRAKE, LOW);

    analogWrite(AMOTOR, motor_speed[0]);
    analogWrite(BMOTOR, motor_speed[1]);
}
/*
void move_in(){
    digitalWrite(DIR_A, HIGH);
    digitalWrite(DIR_B, LOW);


    digitalWrite(AMOTOR_BRAKE, LOW);
    digitalWrite(BMOTOR_BRAKE, LOW);

    digitalWrite(AMOTOR, HIGH);
    digitalWrite(BMOTOR, HIGH);
}
*/
void variable_in(){
    while(Serial.available () < 2);//wait for the motor speed info
    motor_speed[0] = Serial.parseInt();//motor A speed
    motor_speed[1] = Serial.parseInt();//motor B speed

    if(motor_speed[0] > 255){
      motor_speed[0] = 255;
    }
    if(motor_speed[1] > 255){
      motor_speed[1] = 255;
    }
    
    digitalWrite(DIR_A, HIGH);
    digitalWrite(DIR_B, LOW);

    digitalWrite(AMOTOR_BRAKE, LOW);
    digitalWrite(BMOTOR_BRAKE, LOW);

    analogWrite(AMOTOR, motor_speed[0]);
    analogWrite(BMOTOR, motor_speed[1]);
}
/*
void move_out(){
    digitalWrite(DIR_A, LOW);
    digitalWrite(DIR_B, HIGH);


    digitalWrite(AMOTOR_BRAKE, LOW);
    digitalWrite(BMOTOR_BRAKE, LOW);

    digitalWrite(AMOTOR, HIGH);
    digitalWrite(BMOTOR, HIGH);
}
*/
void variable_out(){
    while(Serial.available () < 2);//wait for the motor speed info
    motor_speed[0] = Serial.parseInt();//motor A speed
    motor_speed[1] = Serial.parseInt();//motor B speed

    if(motor_speed[0] > 255){
      motor_speed[0] = 255;
    }
    if(motor_speed[1] > 255){
      motor_speed[1] = 255;
    }
    
    digitalWrite(DIR_A, LOW);
    digitalWrite(DIR_B, HIGH);

    digitalWrite(AMOTOR_BRAKE, LOW);
    digitalWrite(BMOTOR_BRAKE, LOW);

    analogWrite(AMOTOR, motor_speed[0]);
    analogWrite(BMOTOR, motor_speed[1]);
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
  int i = 0, total1 = 0, total2 = 0,ave_us1 = 0, ave_us2 = 0;
  for(i = 0; i < ULTRA_FREQUENCY; i++){
    total1 += sonar1.ping_cm();
    total2 += sonar2.ping_cm();
  }
  ave_us1 = total1 / ULTRA_FREQUENCY;
  ave_us2 = total2 / ULTRA_FREQUENCY;
  
  ultrasonic1 = ave_us1;
  ultrasonic2 = ave_us2;

  Serial.print(ultrasonic1);
  Serial.print('-');
  Serial.print(ultrasonic2);
  Serial.print("&");
}

void get_cap_value() {
  int i;
  long cap = capSense.capacitiveSensorRaw(30);
  long capAvg;

  for (i = 0, capAvg = 0; i < 100; i++) {
    capAvg += cap;
  }
  Serial.print(capAvg/100);
  Serial.print('-');
  //return capAvg/100;
}

void servo_info(){
  Serial.print(myservo.read());
  Serial.print('-');
  Serial.print(servoH_top);
  Serial.print('-');
  Serial.print(servoH_bottom);
  Serial.print('&');
}
void servo_bottom(){
  myservo.write(servoH_bottom);
}
void servo_top(){
  myservo.write(servoH_top);
}
void servo_change(){
    while(Serial.available () < 2);//wait for the motor speed info
    servoH_top = Serial.parseInt();//motor A speed
    servoH_bottom = Serial.parseInt();//motor B speed
}
/*
void test(){
  int A = 0;
  int B = 0;
  while(Serial.available () < 2);//wait for the motor speed info
  A = Serial.parseInt();//motor A speed
  B = Serial.parseInt();//motor B speed
  Serial.print("\n");
  Serial.print(A);
  Serial.print("\n");
  Serial.print(B);
  Serial.print("\n");
}
*/
void encoder_reset(){
  encoder_A.zero();
  encoder_B.zero();
}
void encoder_report(){
  Serial.print(abs(round(encoder_A.getPosition())));
  Serial.print('-');
  Serial.print(abs(round(encoder_B.getPosition())));
  Serial.print('&');
}

//------------------CODEs---------------------
void setup() {
        Wire.begin();
        Serial.begin(9600);     // opens serial port, sets data rate to 9600 bps
        //Serial.println("Welcome to the Arduino Command HQ");  
        myservo.attach(5);
        myservo.write(servoH_top);
        
        //encoder_A.init(MOTOR_393_SPEED_ROTATIONS,MOTOR_393_TIME_DELTA);
        //encoder_B.init(MOTOR_393_SPEED_ROTATIONS,MOTOR_393_TIME_DELTA);
        
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
         
        /*
        Serial.println(AMOTOR);
        Serial.println(BMOTOR);
        Serial.println(AMOTOR_BRAKE);
        Serial.println(BMOTOR_BRAKE);
        */
        delay(100);
        //Serial.println("End of Setup");
}

void loop() {  
  //Serial.println("Loop"); 
  command();
  //us_sensor();
}


void command(){
      if (Serial.available() > 0) {
          // read the incoming byte:
          input = Serial.read(); //single character
          //Serial.print("Receieved: "); 
          //Serial.println(input);
          

          switch(input){
            case 'w':
              if(command_status == 1){
                //move_forward();
                variable_forward();
                //Serial.print("Forward");
              }
              break;
              
            case 'r':
              if(command_status == 1){
                //move_reverse();
                variable_reverse();
                //Serial.print("Backward");
              }
              break;

            case 'o':
              if(command_status == 1){
                //move_out();
                variable_out();
              }
              break;          

            case 'i':
              if(command_status == 1){
                //move_in();
                variable_in();
              } 
              break;
              
            case 'x':
              if(command_status == 1){
                stop_motor();
              }
              break;
              
            case 'u':
              if(command_status == 1){
                //noInterrupts();
                us_sensor();
                //us_sensor();
                //interrupts();
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
              
            case 'c':
              if(command_status == 1){
                servo_change();    
              }
              break;
              
            case 'R':
              command_status = 1;
              break;
              
            case 'k':
              if(command_status == 1){
                encoder_reset();
                //Serial.print("reset");
              }
              break;
              
            case 'm':
              if(command_status == 1){
                encoder_report();
                //Serial.print("report");
              }
              break;
             
            case 'C':
              //Serial.print("Received: C");
              if(command_status == 1){
                get_cap_value();
                //Serial.print("Cap");
              }
              break;
             
            
            default:
             // Serial.println("NULL");
            break;
          }
      }
}


 
