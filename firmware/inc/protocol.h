#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <stdint.h>

#define PROTOCOL_BUFFER_LENGTH  64

typedef struct {
    uint16_t sample_period;      /* 200 - 20000 uS */
    uint32_t acquisition_length; /* In systime counts */
} session_parm_t;

session_parm_t *Protocol_SessionParams(void);
uint8_t         Protocol_ProcessNewPacket(void);
uint8_t         Protocol_SendU16(uint16_t byte);
uint8_t         Protocol_SendI16(int16_t byte);


#endif
