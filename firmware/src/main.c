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

#include "systime.h"
#include "macros.h"
#include "scheduler.h"
#include "protocol.h"

__ALIGN_BEGIN USB_OTG_CORE_HANDLE  USB_OTG_dev __ALIGN_END;

extern uint8_t protocol_rx_buffer[64];
static Task *acquire_task;
static uint32_t sample_len;

static void usb_cdc_init(void)
{
    USBD_Init(&USB_OTG_dev,
              USB_OTG_FS_CORE_ID,
              &USR_desc,
              &USBD_CDC_cb,
              &USR_cb);
}

/* Task Callbacks */
void check_usb(Task *task)
{
    session_parm_t params;

    if (VCP_data_available() >= 64) {
        VCP_get_buffer(protocol_rx_buffer, 64);
        Protocol_ProcessNewPacket();
        params = *Protocol_SessionParams();
        sample_len = params.acquisition_length/params.sample_period;
    }
}

int main(void)
{
    usb_cdc_init();
    SysTime_Init();

    VCP_flush_rx();

    Scheduler_AddTask(systime(), 1000, &check_usb, TRUE);
    
    while (1) {
        Scheduler_Run(systime());
    }

    return 0;
}
