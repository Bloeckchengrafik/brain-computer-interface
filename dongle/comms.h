#pragma once

#include <esp_now.h>

#define position 0 // 0: Dongle, 1: Onboard
#define WIFI_CHANNEL 0

extern uint8_t peerAddress[6];
extern esp_now_peer_info_t peerInfo;
extern bool ack;

class CommunicationData {
    public:
      float values[8];
      float pos[3];
      bool trigger;
};

void onDataSent( const uint8_t* macAddr, esp_now_send_status_t state);
void onDataRecv( const uint8_t* macAddr, const uint8_t *incomingData, int len);

class Controller {
    public:
        CommunicationData ack;
        CommunicationData payload;

        void init( void );
        void update( void );
};
