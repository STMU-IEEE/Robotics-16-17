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
  Serial.print(DELIMITER_CHAR);
  Serial.print(ultrasonic2);
  Serial.print(CRLF);
}
