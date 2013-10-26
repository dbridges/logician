#include "protocol.h"
#include "usbd_cdc_vcp.h"
#include "systime.h"

uint8_t protocol_rx_buffer[PROTOCOL_BUFFER_LENGTH];

static  session_parm_t session_parm;

uint8_t    Protocol_ProcessNewPacket(void)
{
    uint8_t *rx_ptr;

    rx_ptr = &protocol_rx_buffer[1];
    
    switch (protocol_rx_buffer[0]) {
        case 1:
            session_parm.sample_period = (*(uint16_t*)rx_ptr) * SYSTIME_COUNTS_PER_MS;
            rx_ptr += 2;
            session_parm.acquisition_length = (*(uint16_t*)rx_ptr) * 
                100 * SYSTIME_COUNTS_PER_MS; 
            break;
        default:
            return 0;
    }
    return 1;
}

session_parm_t *Protocol_SessionParams(void)
{
    return &session_parm;
}

uint8_t Protocol_SendU16(uint16_t val)
{
    VCP_put_char((uint8_t)(val & 0x00FF));
    VCP_put_char((uint8_t)(val >> 8));
    return 2;
}

uint8_t Protocol_SendI16(int16_t val)
{
    VCP_put_char((int8_t)(val & 0x00FF));
    VCP_put_char((int8_t)(val >> 8));
    return 2;
}
