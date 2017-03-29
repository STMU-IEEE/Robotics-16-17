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

//the brake traces were cut! these aren't connected!
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
const char CONFIRM_CHAR = '@';
const char TERM_CHAR = ' ';
const char END_CHAR = '\n';
const char EMERGENCY_CHAR = '%';
const char UNKNOWN_ARDUINO_CHAR = '^';
char input, trash_input;

//declare this as volatile since it is updated by an ISR
volatile bool command_status = 0;

const int LEFT_ARDUINO = 0;
const int RIGHT_ARDUINO = 1;
const int UNKNOWN_ARDUINO = -1;
int whoami = UNKNOWN_ARDUINO;

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
const int GYRO_CAL_SAMPLE_NUM = 1000;
int16_t dc_offset = 0;
int16_t& gyro_robot_z = gyro.g.y; //-Z axis is connected to the gyro's +y rotation
bool gyro_is_calibrated = 0;
bool gyro_status = 0;

//Capactitor Variables
const int CAP_SAMPLE_NUM = 40;
long cap_current = 0;
long cap_array_norm[CAP_SAMPLE_NUM], cap_array_min[CAP_SAMPLE_NUM], cap_array_max[CAP_SAMPLE_NUM];
long min_median_cap = 0, max_median_cap = 0, median_cap = 0, ave_cap = 0;
const int CAP_MESSAGE_SIZE = 4;
long capacitor_message[CAP_MESSAGE_SIZE];

//-------------------SETUP----------------
void setup() {
        Wire.begin();
        Serial.begin(57600);     // opens serial port, sets data rate to 57600 bps
        //Serial.println("Welcome to the Arduino Command HQ");  
        myservo.attach(5);
        myservo.write(servoH_top);
        
        //Remember to comment this two declarations before testing anything since they will make the Arduino 
        //become unresponsive
        encoder_A.init(MOTOR_393_SPEED_ROTATIONS,MOTOR_393_TIME_DELTA);
        encoder_B.init(MOTOR_393_SPEED_ROTATIONS,MOTOR_393_TIME_DELTA);
        
        enableInterrupt(stop_button, stop_motor_ALL , CHANGE); 

        pinMode(DEBUG_LED, OUTPUT);
        pinMode(AMOTOR, OUTPUT);
        pinMode(BMOTOR, OUTPUT);
        //the brake traces were cut! these aren't connected!
        pinMode(AMOTOR_BRAKE, OUTPUT);
        pinMode(BMOTOR_BRAKE, OUTPUT);
        pinMode(DIR_A, OUTPUT);
        pinMode(DIR_B, OUTPUT);

        
        pinMode(TRIGGER_PIN1, OUTPUT);
        pinMode(ECHO_PIN1, INPUT);
        pinMode(TRIGGER_PIN2, OUTPUT);
        pinMode(ECHO_PIN2, INPUT);       

        gyro_status = gyro.init();
          //report gyro not working
          //Serial.println("Gyro found");
        

        //Don't speak when not spoken to
        //Serial.println(gyro_status);
        
        gyro.enableDefault();
        //set_whoami();

        //Serial.println("End of Setup");
}


//-------------------FUNCTIONs----------------
bool RPi_confirm(){
  int end_value = millis() + 20*1000;
 
  while(Serial.available() < 1){
    gyro_update_angle();
    if(end_value < millis()){
      return 0;
    }
  }
  if(Serial.read() == CONFIRM_CHAR){
    return 1;
  }
  else
    return 0;
}

void print_long_array(long ary[], int ary_size){
  for(int a = 0; a < ary_size; a++){
    Serial.print(capacitor_message[a]);
    if(a < ary_size - 1){
      Serial.print(TERM_CHAR);
    }
    else{
      Serial.print(END_CHAR);
    }
  }
  if(!RPi_confirm()){
    Serial.print(EMERGENCY_CHAR);
  }
  return;
}

//Please only call this from corresponding command case '['
void set_whoami(){
  
  //Serial.println("Waiting Assignment");
  while(Serial.available() < 1);
  //Serial.println("Received Assigment");
  int assignment_given;
  assignment_given = Serial.read();
  
  if(assignment_given == '0'){
    //Serial.println("Left Arduino");
    whoami = LEFT_ARDUINO;
  }
  else if(assignment_given == '1'){
    //Serial.println("Right Arduino");
    whoami = RIGHT_ARDUINO;
  }
  else{
    whoami = UNKNOWN_ARDUINO;
  }
}

void get_whoami(){
  Serial.println(whoami);
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

//------------------LOOPs---------------------


void loop() {  
  //Serial.println("Loop");
  
  if(gyro_is_calibrated == 1){
     gyro_update_angle();  
  }
  command();
  //us_sensor();
}


