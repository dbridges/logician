/*
 * Logician Firmware
 * USB Logic Analyzer for STM32F4 Discovery
 * Written by Dan Bridges 2013
 * dbridges @ github
 */

#include "discovery.h"
#include "usbd_cdc_core.h"
#include "usbd_usr.h"
#include "usbd_desc.h"
#include "usbd_cdc_vcp.h"

#include "macros.h"
#include "protocol.h"

__ALIGN_BEGIN USB_OTG_CORE_HANDLE  USB_OTG_dev __ALIGN_END;

extern uint8_t protocol_rx_buffer[64];

volatile unsigned int *DWT_CYCCNT  = (volatile unsigned int *)0xE0001004;
volatile unsigned int *DWT_CONTROL = (volatile unsigned int *)0xE0001000;
volatile unsigned int *SCB_DEMCR   = (volatile unsigned int *)0xE000EDFC;

void enable_timing(void)
{
    static int enabled = 0;
 
    if (!enabled)
    {
        *SCB_DEMCR = *SCB_DEMCR | 0x01000000;
        *DWT_CYCCNT = 0; // reset the counter
        *DWT_CONTROL = *DWT_CONTROL | 1 ; // enable the counter
 
        enabled = 1;
    }
}

void timing_delay(unsigned int tick)
{
    unsigned int start, current;

    start = *DWT_CYCCNT;
    do {
        current = *DWT_CYCCNT;
    } while((current - start) < tick);
}

static void usb_cdc_init(void)
{
    USBD_Init(&USB_OTG_dev,
              USB_OTG_FS_CORE_ID,
              &USR_desc,
              &USBD_CDC_cb,
              &USR_cb);
}

uint8_t check_usb()
{
    if (VCP_data_available() >= 64) {
        VCP_get_buffer(protocol_rx_buffer, 64);
        Protocol_ProcessNewPacket();
        return 1;
    }
    return 0;
}

int main(void)
{
    uint8_t data_byte;
    unsigned int start, current;
    uint32_t sample_count = 0;
    session_param_t *params;

    usb_cdc_init();
    VCP_flush_rx();
    enable_timing();

    while (1) {
        if (sample_count > 0) {
            start = *DWT_CYCCNT;
            data_byte = ((uint8_t)INPUT_PORT->IDR) << 4;
            timing_delay(144 - (start - *DWT_CYCNT) - 1);
            data_byte = ((uint8_t)INPUT_PORT->IDR) & 0x0F;
            VCP_put_char(data_byte);
            sample_count--;
            timing_delay(288 - (start - *DWT_CYCNT) - 1);
        } else if (check_usb()) {
            params = Protocol_SessionParams();
            sample_count = params->sample_count;
        } else {
            timing_delay(1440000);  /* Wait 10 ms */
        }
    }

    return 0;
}
