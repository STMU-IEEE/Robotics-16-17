void gyro_cali(){
	int32_t dc_offset_sum = 0;
	
	for(int i = 0; i < sample_num; i++){
		while(!gyro_data_ready());
		gyro.read();
		dc_offset_sum += gyro_robot_z;
	}
	dc_offset = dc_offset_sum / sample_num;
	Serial.print(dc_offset);
	Serial.print(end_char);
}

bool gyro_data_ready(){
	return (gyro.readReg(L3G::STATUS) & ZYXDA) == ZYXDA;
}

void gyro_update_angle(){
	gyro.read();
	rate = (float)(gyro_robot_z - dc_offset) * ADJUSTED_SENSITIVITY;
	angle += (((prev_rate + rate) / SAMPLE_RATE) / 2);
	prev_rate = rate;
}

void gyro_report_angle(){
	Serial.print(angle);
	Serial.print(end_char);
}
