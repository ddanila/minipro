/* ASan catches the historical 40-entry buffers passed to 56-entry T48 APIs. */
#include "../src/prom.c"
#include <assert.h>
static volatile unsigned observed;
int minipro_set_zif_direction(minipro_handle_t *h,uint8_t*p){(void)h;observed+=p[55];return 0;}
int minipro_set_zif_state(minipro_handle_t*h,uint8_t*p){(void)h;observed+=p[55];return 0;}
int minipro_set_pin_drivers(minipro_handle_t*h,pin_driver_t*p){(void)h;observed+=p[55].vpp;return 0;}
int minipro_set_voltages(minipro_handle_t*h,uint8_t a,uint8_t b){(void)h;(void)a;(void)b;return 0;}
int minipro_get_zif_state(minipro_handle_t*h,uint8_t*p){(void)h;memset(p,0,56);return 0;}
int minipro_reset_state(minipro_handle_t*h){(void)h;return 0;}
int main(void){
 device_t d={0};minipro_handle_t h={0};uint8_t data[2];h.device=&d;d.package_details.pin_count=16;
 assert(prom_init(&h)==0);assert(prom_read(&h,0,data,sizeof(data))==0);
 assert(prom_terminate(&h)==0);puts("PROM 56-entry pin vectors: PASS");return 0;
}
