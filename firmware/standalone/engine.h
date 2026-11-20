#pragma once
#include <stdint.h>
#include <stddef.h>
typedef struct {
 const uint8_t *packet; size_t length, step;
 uint64_t deadline; uint16_t mask;
 unsigned mode; int active, delivered, finished;
} Sender;
/* mask uses switch-pico UART button bits: Y B A X L R. */
int sender_start(Sender *s, unsigned mode, const uint8_t *packet, size_t length);
void sender_cancel(Sender *s);
void sender_report_sent(Sender *s, uint64_t now_ms);
uint32_t packet_adler(const uint8_t *p, size_t n);
uint32_t packet_crc(const uint8_t *p, size_t n);
int packet_valid(const uint8_t *p, size_t n);
unsigned sender_mode_for_hold(uint64_t milliseconds);
