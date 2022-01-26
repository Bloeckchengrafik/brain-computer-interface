#include "comms.h"
#include <WiFi.h>
#include <esp_now.h>
#include <HardwareSerial.h>

uint8_t peerAddress[6] = {0x00, 0x9d, 0xc2, 0xc2, 0xef, 0x60};
esp_now_peer_info_t peerInfo;
bool ack;

void onDataSent( const uint8_t* macAddr, esp_now_send_status_t state) {
  if ( state == ESP_NOW_SEND_SUCCESS ) {
    Serial.println("#Sent Packet successfully");
  } else {
    Serial.print("!Error while sending packet: ");
    Serial.println(state);
  }
}

void onDataRecv( const uint8_t* macAddr, const uint8_t *incomingData, int len) {
  Serial.println("#Recv");
  if ( position == 1) {
    ack = true;
    Serial.print("#Ack now ");
    Serial.println(ack);
    uint8_t lPeerAddress[6] = {0x00, 0x9d, 0xc2, 0xc2, 0xef, 0x60};

    for (int i = 0; i < 6; i++) {
      lPeerAddress[i] = *macAddr;
      macAddr++;

      Serial.printf("%02x:", lPeerAddress[i] & 0xff);
    }
    
    memcpy(peerInfo.peer_addr, lPeerAddress, 6);
    esp_now_add_peer(&peerInfo);
    return;
  }

  CommunicationData buffer;
  memcpy(&buffer, incomingData, sizeof(buffer));

  if ( position == 0 ) {
    Serial.printf(
      "*%f#%f#%f#%f#%f#%f#%f#%f(%f-%f-%f)-%s\n",
      buffer.values[0],
      buffer.values[1],
      buffer.values[2],
      buffer.values[3],
      buffer.values[4],
      buffer.values[5],
      buffer.values[6],
      buffer.values[7],
      buffer.pos[0],
      buffer.pos[1],
      buffer.pos[2],
      buffer.trigger ? "Y" : "N"
    );
  }
}

void Controller::init( void ) {
  WiFi.mode(WIFI_MODE_STA);

  if (esp_now_init() != ESP_OK) {
    Serial.println("!Error in EspNow Initialization Process");
  }

  esp_now_register_send_cb(onDataSent);
  esp_now_register_recv_cb(onDataRecv);
  
  peerInfo.channel = WIFI_CHANNEL;
  peerInfo.encrypt = false;
  
  Serial.print("#macAdress: ");
  Serial.println(WiFi.macAddress());
  
  if ( position ){
    /* Onboard */
  } else {
    /* Dongle */
    while ( !Serial );

    Serial.print("#Recv MAC ");
    
    for (int i = 0; i < 6; i++) {
      while ( Serial.available() <= 1 );

      uint8_t readByte = Serial.read();
      
      Serial.printf("%02x", readByte & 0xff);

      if ( i != 5 ) {
        Serial.print(":");
      }
      
      peerAddress[i] = readByte;
    }


    Serial.println("");
    
    memcpy(peerInfo.peer_addr, peerAddress, 6);
    esp_now_add_peer(&peerInfo);

    esp_now_send(peerAddress, (uint8_t *) &ackPayload, sizeof(ackPayload));
  }
}

void Controller::update( void ) {
  if( ack == true ) {
    Serial.print("#Sending... ");
    esp_err_t error = esp_now_send(peerAddress, (uint8_t *) &payload, sizeof(payload));
    Serial.println(error);
  }
}
