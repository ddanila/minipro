/* Exercise the real parser without opening a USB device. */
#define main minipro_cli_main
#include "../src/main.c"
#undef main
#include <assert.h>
int main(void) {
 device_t d={0};cmdopts_t opts={0};minipro_handle_t h={0};h.device=&d;h.cmdopts=&opts;
 char *args[]={"minipro","-o","pulse=50000",NULL};
 assert(parse_options(&h,3,args)==0);assert(d.pulse_delay==50000);
 char *longargs[]={"minipro","--pulse","50000",NULL};
 d.pulse_delay=0;assert(parse_options(&h,3,longargs)==0);assert(d.pulse_delay==50000);
 char *bad[]={"minipro","-o","pulse=65536",NULL};
 assert(parse_options(&h,3,bad)!=0);puts("Pulse short/long option and range: PASS");return 0;
}
