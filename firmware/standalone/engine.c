#include "engine.h"
#include <string.h>
static uint32_t le32(const uint8_t *p) {return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
uint32_t packet_adler(const uint8_t *p,size_t n){uint32_t a=1,b=0;for(size_t i=0;i<n;i++){a=(a+p[i])%65521;b=(b+a)%65521;}return (b<<16)|a;}
uint32_t packet_crc(const uint8_t *p,size_t n){uint32_t c=~0u;for(size_t i=0;i<n;i++){c^=p[i];for(int j=0;j<8;j++)c=(c>>1)^(0xedb88320u & (0u-(c&1)));}return ~c;}
int packet_valid(const uint8_t *p,size_t n){
 if(!p||n<20||memcmp(p,"SSE2\1",5))return 0;
 size_t len=le32(p+5),name=p[13];
 if(name<7||name>72||len>8000||14+name+len!=n||p[14]!='P'||p[18]!='_')return 0;
 for(int i=15;i<18;i++)if(p[i]<'0'||p[i]>'9')return 0;
 unsigned slot=(p[15]-'0')*100+(p[16]-'0')*10+p[17]-'0';
 if(slot<4||slot>120)return 0;
 return packet_adler(p+14+name,len)==le32(p+9);
}
static unsigned duration(Sender *s){
 if(s->mode==1){static const unsigned ms[]={800,300,200,500};return ms[s->step];}
 if(s->mode==2){if(s->step==0||s->step==13)return 2000;return s->step%2?1200:1000;}
 if(s->step==0)return 1000;
 if(s->step>4*s->length)return 500;
 return s->step%2?100:200;
}
static void output(Sender *s){
 s->mask=0;
 if(s->mode==1){if(s->step==0)s->mask=48;else if(s->step==2)s->mask=4;return;}
 if(s->mode==2){static const uint16_t buttons[]={4,2,8,1,16,32};if(s->step>=1&&s->step<=11&&s->step%2)s->mask=buttons[(s->step-1)/2];return;}
 if(s->step==0||s->step>4*s->length)return;
 size_t symbol=(s->step-1)/2;uint8_t byte=s->packet[symbol/2],nibble=symbol%2?byte&15:byte>>4;
 static const uint16_t faces[]={4,2,8,1};for(int i=0;i<4;i++)if(nibble&(1<<i))s->mask|=faces[i];
 unsigned edge=(unsigned)(symbol%2)^(s->step%2?0:1);if(edge)s->mask|=32;
}
int sender_start(Sender *s,unsigned mode,const uint8_t *p,size_t n){
 if(s->active||mode<1||mode>3||(mode==3&&!packet_valid(p,n)))return 0;
 memset(s,0,sizeof(*s));s->mode=mode;s->packet=p;s->length=n;s->active=1;output(s);return 1;
}
void sender_cancel(Sender *s){s->active=0;s->mask=0;s->finished=1;}
void sender_report_sent(Sender *s,uint64_t now){
 if(!s->active)return;
 if(!s->delivered){s->delivered=1;s->deadline=now+duration(s);return;}
 if(now<s->deadline)return;
 if(now>s->deadline+2000){sender_cancel(s);return;}
 size_t last=s->mode==1?3:s->mode==2?13:4*s->length+1;
 if(s->step==last){sender_cancel(s);return;}
 s->step++;s->delivered=0;output(s);
}
unsigned sender_mode_for_hold(uint64_t ms){return ms<100?0:ms<1000?1:ms<3500?2:3;}
