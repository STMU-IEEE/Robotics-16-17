void gyro_cali(){
  digitalWrite(DEBUG_LED, HIGH); //debugging
	int32_t dc_offset_sum = 0;
	
	for(int i = 0; i < GYRO_CAL_SAMPLE_NUM; i++){
		while(!gyro_data_ready());
		gyro.read();
		dc_offset_sum += gyro_robot_z;
	}
	dc_offset = dc_offset_sum / GYRO_CAL_SAMPLE_NUM;
 
  gyro_is_calibrated = 1;
  
	Serial.print(dc_offset);
	Serial.print(END_CHAR);
  digitalWrite(DEBUG_LED, LOW);
}

bool gyro_data_ready(){
	return (gyro.readReg(L3G::STATUS) & ZYXDA) == ZYXDA;
}

void gyro_update_angle(){
  if(whoami == UNKNOWN_ARDUINO){
    Serial.println(UNKNOWN_ARDUINO_CHAR);
  }
  else if(gyro_data_ready()){
    gyro.read();
    rate = (float)(gyro_robot_z - dc_offset) * ADJUSTED_SENSITIVITY[whoami];
    angle += (((prev_rate + rate) / SAMPLE_RATE[whoami]) / 2);
    prev_rate = rate;  
  }
}

void gyro_report_angle(){
  //Serial.print("\n");
	Serial.print(angle);
	Serial.print(END_CHAR);
}

void gyro_reset_angle(){
  angle = 0;
}

void gyro_test_value(){
  while(true){
    gyro_update_angle();
    gyro_report_angle();
  }
}
void gyro_status_report(){
  Serial.println(gyro_status);
}

