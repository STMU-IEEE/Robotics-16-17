//-------------------COMMANDSs----------------

void command(){
  if (Serial.available() > 0) {
    // read the incoming byte:
    input = Serial.read(); //single character
    if(command_status != 1) {
      if(input == 'R')
      {
        command_status = 1;
        //gyro_status_report();//get rid of this! do this when told!
        //set_whoami();//get rid of this! do this when told!
        Serial.println(1);
      }
    }
    else //i.e. if(command_status == 1)
    { 
      switch(input){
        case 'w':
          variable_forward();
          break;
        case 'r':
          variable_reverse();
          break;
        case 'o':
          variable_out();
          break;
        case 'i':
          variable_in();
          break;
        case 'x':
          stop_motor();
          break;
        case 'u':
          us_sensor();
          break;
        case 'n':
          servo_info();
          break;
        case 't':
          servo_top();
          break;
        case 'b':
          servo_bottom();
          break;
        case 'c':
          servo_change();    
          break;
        case 'k':
          encoder_reset();
          break;
        case 'm':
          encoder_report();
          break;
        case 'C':
          cap_value();
          break;
        case 'H':
          cap_hard_reset();
          break;
        case '+':
          cap_test();
          break;
        case '=':
          gyro_cali();
          break;
        case '?':
          gyro_report_angle();
          break;
        case '[':
          get_whoami();
          break;
        case ']':
          set_whoami(); 
          break;
        case '.':
          gyro_test_value();
          break;
        case ',':
          gyro_reset_angle();
          break;
        case '_':
          gyro_status_report();
          break;
        default:
          break;
      }
    }
  }
}
