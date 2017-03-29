void servo_info(){
  Serial.print(myservo.read());
  Serial.print(TERM_CHAR);
  Serial.print(servoH_top);
  Serial.print(TERM_CHAR);
  Serial.print(servoH_bottom);
  Serial.print(END_CHAR);
}
void servo_bottom(){
  myservo.write(servoH_bottom);
}
void servo_top(){
  myservo.write(servoH_top);
}
void servo_change(){
    while(Serial.available () < 2){
      gyro_update_angle();//wait for the motor speed info
    }
    servoH_top = Serial.parseInt();//motor A speed
    servoH_bottom = Serial.parseInt();//motor B speed
}
