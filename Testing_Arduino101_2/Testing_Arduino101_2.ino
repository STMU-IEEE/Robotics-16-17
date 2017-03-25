#include <L3G.h>
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

#define DEBUG_LED 13 //built-in LED on Arduino board

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
CapacitiveSensor cap_sense = CapacitiveSensor(CAP_SEND,CAP_REC); // (send_pin, receive_pin);
L3G gyro;




//------------------VARIABLESs----------------
//Communication Variables
const char confirm_char = '@';
const char term_char = '-';
const char end_char = '&';
const char emergency_char = '%';
const char unknown_arduino_b = '^';
char input, trash_input;
bool command_status = 1;

int left_arduino = 0;
int right_arduino = 1;
int unknown_arduino = -1;
int whoami = unknown_arduino;

//General Sensor Variables
const int stop_button = 10;
int servoH_top = 170, servoH_bottom = 0;
int motor_speed[2];
int ultrasonic1 = 0, ultrasonic2 = 0;

//Gyro Variables
const float SAMPLE_RATE[] = {183.63F, 188.05F};//Marked, Non_marked
const float ADJUSTED_SENSITIVITY[] = {0.008956528F , 0.008956528F}; 

float angle = 0;
float rate = 0;
float prev_rate = 0;

const byte ZYXDA = 0b00001000;
const int sample_num = 1000;
int16_t dc_offset = 0;
int16_t& gyro_robot_z = gyro.g.y; //-Z axis is connected to the gyro's +y rotation
bool gyro_is_calibrated = 0;

//Capactitor Variables
const int data_sample = 40;
long cap_current = 0;
long cap_array_norm[data_sample], cap_array_min[data_sample], cap_array_max[data_sample];
long min_median_cap = 0, max_median_cap = 0, median_cap = 0, ave_cap = 0;
long capacitor_message[4];

//-------------------SETUP----------------
void setup() {
        Wire.begin();
        Serial.begin(9600);     // opens serial port, sets data rate to 9600 bps
        //Serial.println("Welcome to the Arduino Command HQ");  
        myservo.attach(5);
        myservo.write(servoH_top);
        
        //Remember to comment this two declarations before testing anything since they will make the Arduino 
        //become unresponsive
        //encoder_A.init(MOTOR_393_SPEED_ROTATIONS,MOTOR_393_TIME_DELTA);
        //encoder_B.init(MOTOR_393_SPEED_ROTATIONS,MOTOR_393_TIME_DELTA);
        
        enableInterrupt(stop_button, stop_motor_ALL , CHANGE); 

        pinMode(DEBUG_LED, OUTPUT);
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

        //Serial.println("A");
        if(!gyro.init()){
          //report gyro not working
          //Serial.println("Gyro not found");
        }
        //Serial.println("B");
        gyro.enableDefault();
        whoami_assignment();

        delay(100);
        //Serial.println("End of Setup");
}


//-------------------FUNCTIONs----------------
bool RPi_confirm(){
 int end_value = millis() + 20*1000;
  while(Serial.available() < 1){
    if(end_value < millis()){
      return 0;
    }
  }
  if(Serial.read() == confirm_char){
    return 1;
  }
  else
    return 0;
}

void whoami_assignment(){
  
  //Serial.println("Waiting Assignment");
  while(Serial.available() < 1);
  //Serial.println("Recieved Assigment");
  int assignment_given;
  assignment_given = Serial.read();
  
  if(assignment_given == '0'){
    //Serial.println("Left Arduino");
    whoami = left_arduino;
  }
  else if(assignment_given == '1'){
    //Serial.println("Right Arduino");
    whoami = right_arduino;
  }
  else{
    whoami = unknown_arduino;
  }
}

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
  Serial.print(term_char);
  Serial.print(ultrasonic2);
  Serial.print(end_char);
}

void bubble_sort(long a[], int sizeofarray){
  //smallest ---- highest
  long holder = 0;
    for(int i = 0; i < sizeofarray - i; i++){
      for(int j = 0; j < sizeofarray - (i+1); j++){
        if(a[j] > a[j+1]){
          holder = a[j];
          a[j] = a[j+1];
          a[j+1] = holder;
        }
      }
    }
}

long findMedian(long a[], int size){

  long returned_value = 0;
  size = size-1;
  
  float size_div = 0;
  size_div = float(size)/2;

  if(size_div != round(size/2)){

    returned_value = (a[round(size/2)] + a[round(size/2)+1])/2;
  }
  else
    returned_value = a[round(size/2)];
  
  return returned_value;
  
}

void cap_value(){
  
  
  for (int i = 0; i < data_sample; i++){
    cap_array_norm[i] = cap_sense.capacitiveSensorRaw(30);
  }

  for(int l = 0; l < data_sample; l++){
    ave_cap += cap_array_norm[l];
  }
  ave_cap /= data_sample;
  

  bubble_sort(cap_array_norm, data_sample);
  
  median_cap = findMedian(cap_array_norm, data_sample);

  for(int e = 0; e < round(data_sample/2) ; e++){
    cap_array_min[e] = cap_array_norm[e];
  }
  
  min_median_cap = findMedian(cap_array_min, (data_sample / 2) );
  
  for(int w = round(data_sample/2); w < data_sample; w++){
    cap_array_max[w-round(data_sample/2)] = cap_array_norm[w]; 
  }

  max_median_cap = findMedian(cap_array_max, data_sample/2 );

  capacitor_message[0] = abs(max_median_cap);
  capacitor_message[1] = abs(median_cap);
  capacitor_message[2] = abs(min_median_cap);
  capacitor_message[3] = abs(ave_cap);


  for(int a = 0; a < 4; a++){
    Serial.print(capacitor_message[a]);
    if(a < 3){
      Serial.print(term_char);
    }
    else{
      Serial.print(end_char);
      break;
    }
    if(!RPi_confirm()){
      Serial.print(emergency_char);
      break;
    }
  }
  
}
void cap_test(){
  for(int i = 0; i < 100; i++){
    Serial.println(cap_sense.capacitiveSensorRaw(30));
  }
}
void cap_hard_reset(){
  digitalWrite(CAP_SEND, LOW);
  delay(500);
}

void servo_info(){
  Serial.print(myservo.read());
  Serial.print(term_char);
  Serial.print(servoH_top);
  Serial.print(term_char);
  Serial.print(servoH_bottom);
  Serial.print(end_char);
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

void encoder_reset(){
  encoder_A.zero();
  encoder_B.zero();
}
void encoder_report(){
  Serial.print(abs(round(encoder_A.getRawPosition())));
  Serial.print(term_char);
  Serial.print(abs(round(encoder_B.getRawPosition())));
  Serial.print(term_char);
}

//------------------LOOPs---------------------


void loop() {  
  //Serial.println("Loop");
  
  if(gyro_is_calibrated == 1){
     gyro_update_angle();  
  }
  command();
  //us_sensor();
}

//-------------------COMMANDSs----------------

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
              Serial.print("Cap");
              if(command_status == 1){
                cap_value();
              }
              break;
            case 'H':
              if(command_status == 1){
                cap_hard_reset();
              }
              break;
            case '+':
              if(command_status == 1){
                cap_test();
              }
	            break;
            case '=':
               Serial.println("Gyro_Cali");
               if(command_status == 1){
                gyro_cali();
               }
               break;
            case '?':
               if(command_status == 1){
                gyro_report_angle();
               }
               break;
             case '(':
                if(command_status == 1){
                  whoami_assignment(); 
                }
                break;
              case '.':
                if(command_status == 1){
                  gyro_test_value();
                }
                break;
              case ',':
                if(command_status == 1){
                  gyro_reset_angle();
                }
                break;
	       break;
            default:
             // Serial.println("NULL");
               break;
          }
      }
}


 
