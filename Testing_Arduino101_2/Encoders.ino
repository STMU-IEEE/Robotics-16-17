void encoder_reset(){
  encoder_A.zero();
  encoder_B.zero();
}
void encoder_report(){
  //Don't call functions inside abs()--use a variable instead
  long a = encoder_A.getRawPosition();
  Serial.print(abs(a));
  Serial.print(DELIMITER_CHAR);
  long b = encoder_B.getRawPosition();
  Serial.print(abs(b));
  Serial.print(CRLF);
}

