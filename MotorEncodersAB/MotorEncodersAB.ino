
const byte motorEncoderA = 2; 
const byte motorEncoderB = 3;
int countLeft = 0; countRight = 0;


void setup() {
 attachInterrupt(digitalPinToInterrupt(motorEncoderA), A1 , CHANGE);
 attachInterrupt(digitalPinToInterrupt(motorEncoderB), B1, CHANGE);
 

}

void loop() {
  
}

void A1() {
  if(motorEncoderA == motorEncoderB)
    countLeft--;
  else
    countLeft++;  
}

void B1() {
  if(motorEncoderA == motorEncoderB)
    countLeft++;
  else 
    countLeft--;
}

