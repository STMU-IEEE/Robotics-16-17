/*
To measure the sample rate of the sensor:
1. Discard sample
2. Poll sensor until next sample is ready.
   Discard again because this might be immediately after clearing the 1st sample.
3. Wait until next sample; this will be long enough that once the next sample is ready,
   the time can be taken.
4. Take time after next sample; initialize count to 1.
5. Keep counting samples for 1 minute.
6. Every minute the Arduino will print number of samples per minute.
   Divide this by 60 to obtain samples per second.

   Results:
   unmarked sensor: 11283 Sa/min = 188.05 Sa/s
   marked sensor: 11018 Sa/min = 183.63 Sa/s
*/

#include <Wire.h>
#include <L3G.h>

const byte ZYXDA = 1 << 3;

L3G gyro;

void setup() {
  Serial.begin(9600);
  Wire.begin();

  if (!gyro.init())
  {
    Serial.println("Failed to autodetect gyro type!");
    while (1);
  }

  gyro.enableDefault();
}

void loop() {
  //Discard sample
  gyro.read()
  //Wait until next new sample
  while(!gyro_data_ready());
  //Discard sample
  gyro.read()
  //The Arduino has definitely "caught up" and can wait until next new sample
  while(!gyro_data_ready());
  //Get time immediately after 1st sample is ready
  long start_time = millis();
  gyro.read();
  int read_count = 1;
  //Count number of samples for 1 minute (60000ms)
  while(millis() < start_time + 60000){
    while(!gyro_data_ready());
    gyro.read();
    read_count++;
  }
  Serial.println(read_count);
}

bool gyro_data_ready(){
    return (gyro.readReg(L3G::STATUS) & ZYXDA) == ZYXDA;
}

