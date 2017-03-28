void gyro_cali(){
  digitalWrite(DEBUG_LED, HIGH); //debugging
	int32_t dc_offset_sum = 0;
	
	for(int i = 0; i < sample_num; i++){
		while(!gyro_data_ready());
		gyro.read();
		dc_offset_sum += gyro_robot_z;
	}
	dc_offset = dc_offset_sum / sample_num;
 
  gyro_is_calibrated = 1;
  
	Serial.print(dc_offset);
	Serial.print(end_char);
  digitalWrite(DEBUG_LED, LOW);
}

bool gyro_data_ready(){
	return (gyro.readReg(L3G::STATUS) & ZYXDA) == ZYXDA;
}

void gyro_update_angle(){
  if(whoami == unknown_arduino){
    Serial.println(unknown_arduino_b);
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
	Serial.print(end_char);
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
  Serial.print(gyro_status);
}

