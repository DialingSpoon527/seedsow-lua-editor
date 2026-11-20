#include "pico/stdlib.h"
#include "tusb.h"
#include "bsp/board.h"
#include "usb/usb_output_driver.h"
#include "usb/switch/switch_pro_driver.h"
#include "platform/pico/bootsel_button_sample.h"
extern "C" {
#include "engine.h"
}
/* Configurator patches this reserved flash object, never instructions. */
__attribute__((used)) const volatile uint8_t standalone_config[8192]={
 'S','2','P','I','C','O','2','W','C','O','N','F','I','G','0','1'};
static uint32_t word(const volatile uint8_t *p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint8_t packet[8168];
int main(){
 board_init();usb_output_driver_init(AdapterUsbMode::kSwitch);tusb_init();
 uint32_t size=word(standalone_config+16),crc=word(standalone_config+20);
 bool valid=size<=sizeof(packet)&&size>0;
 if(valid){for(unsigned i=0;i<size;i++)packet[i]=standalone_config[24+i];valid=packet_crc(packet,size)==crc&&packet_valid(packet,size);}
 Sender sender{};bool held=false,locked=false,uploaded=false,released=false;
 uint64_t began=0,last_poll=0,last_report=0;
 for(;;){
  tud_task();uint64_t now=to_ms_since_boot(get_absolute_time());
  bool ready=tud_mounted()&&usb_output_driver_is_ready(0);
  if(!ready&&sender.active){sender_cancel(&sender);locked=true;}
  if(sender.active&&last_report&&now-last_report>2000){sender_cancel(&sender);locked=true;}
  if(now-last_poll>=25){last_poll=now;int sample=bootsel_button_sample();
   if(sample==1&&!held){held=true;began=now;if(sender.active){sender_cancel(&sender);locked=true;}}
   if(sample==0){
    if(held){uint64_t duration=now-began;held=false;
     if(ready&&!locked&&released&&now>5000&&duration>=100){
      unsigned mode=sender_mode_for_hold(duration);
      if(mode!=3||(!uploaded&&valid)){if(sender_start(&sender,mode,packet,size)){last_report=now;if(mode==3)uploaded=true;}}
     }
    }released=true;
   }
  }
  ControllerState state=controller_neutral_state();
  state.button_east=sender.mask&4;state.button_south=sender.mask&2;
  state.button_north=sender.mask&8;state.button_west=sender.mask&1;
  state.button_left_shoulder=sender.mask&16;state.button_right_shoulder=sender.mask&32;
  usb_output_driver_set_input(0,state,SWITCH_PRO_DIGITAL_TRIGGER_THRESHOLD,SWITCH_PRO_DIGITAL_TRIGGER_THRESHOLD);
  if(usb_output_driver_task(0)){last_report=now;sender_report_sent(&sender,now);}
 }
}
