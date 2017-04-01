void cap_value(){
  
  
  for (int i = 0; i < CAP_SAMPLE_NUM; i++){
    cap_array_norm[i] = cap_sense.capacitiveSensorRaw(30);
  }

  for(int l = 0; l < CAP_SAMPLE_NUM; l++){
    ave_cap += cap_array_norm[l];
  }
  ave_cap /= CAP_SAMPLE_NUM;
  

  bubble_sort(cap_array_norm, CAP_SAMPLE_NUM);
  
  median_cap = findMedian(cap_array_norm, CAP_SAMPLE_NUM);

  for(int e = 0; e < round(CAP_SAMPLE_NUM/2) ; e++){
    cap_array_min[e] = cap_array_norm[e];
  }
  
  min_median_cap = findMedian(cap_array_min, (CAP_SAMPLE_NUM / 2) );
  
  for(int w = round(CAP_SAMPLE_NUM/2); w < CAP_SAMPLE_NUM; w++){
    cap_array_max[w-round(CAP_SAMPLE_NUM/2)] = cap_array_norm[w]; 
  }

  max_median_cap = findMedian(cap_array_max, CAP_SAMPLE_NUM/2 );

  capacitor_message[0] = abs(max_median_cap);
  capacitor_message[1] = abs(median_cap);
  capacitor_message[2] = abs(min_median_cap);
  capacitor_message[3] = abs(ave_cap);

  print_long_array(capacitor_message, CAP_MESSAGE_SIZE);

  
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

