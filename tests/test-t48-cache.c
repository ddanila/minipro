/* Regression: pull-down reconfiguration releases driven pins. */
#include "../src/t48.c"
static int outputs;
int msg_send(void *handle,uint8_t *b,size_t n) {
 (void)handle;(void)n;if(b[0]==T48_SET_OUT)outputs++;return 0;
}
int main(void) {
 minipro_handle_t h={0};uint8_t d[56],s[56];
 memset(d,MP_PIN_DIRECTION_IN,sizeof d);memset(s,0,sizeof s);
 d[0]=MP_PIN_DIRECTION_OUT;s[0]=1;
 assert(t48_reset_state(&h)==0);
 assert(t48_set_zif_direction(&h,d)==0);assert(t48_set_zif_state(&h,s)==0);
 assert(outputs==1);
 assert(t48_set_zif_state(&h,s)==0);assert(outputs==1);
 assert(t48_set_zif_direction(&h,d)==0);assert(t48_set_zif_state(&h,s)==0);
 assert(outputs==2);puts("T48 pull-down output restore: PASS");return 0;
}
