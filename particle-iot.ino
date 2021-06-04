#include <HttpClient.h>

// This #include statement was automatically added by the Particle IDE.
#include <Adafruit_PWMServoDriver.h>

#include "application.h"
#include "HttpClient.h"

unsigned int nextTime = 0;    // Next time to contactthe server
HttpClient http;

// Headers currently need to be set at init, usefulfor API keys etc.
http_header_t headers[] = { 
    //  { "Content-Type", "application/json" },
    //  { "Accept" , "application/json" },
    { "Accept" , "*/*"},
    { NULL, NULL } // NOTE: Always terminate headerswill NULL};
};

http_request_t request;
http_response_t response;
String line = "";;

const int TouchPin=D2;
int touched = 0;
int closed = 0;
int open = 179;
long tl_timer;
SYSTEM_THREAD(ENABLED);

Servo myservo;

void setup() {
    Serial.begin(9600);
    myservo.attach(D3);
    delay(1000);
}

void loop() {
     if (nextTime > millis()) {
        return;
    }
    Serial.println("Application>\tStart of Loop.");
    // hostname is ip address of flask server
	request.hostname = "";
    request.port = 5000;
    request.path = "/mask";
    // request.path = "/stats?date=2021-06-01";
    int sensorValue = digitalRead(TouchPin);
    Serial.println(sensorValue);
    if(sensorValue == 1)
    {
        Serial.println("touched");
        touched = 1;
        
        http.get(request, response, headers);
        // delay(3000);
        Serial.print("Application>\tResponse status: ");
        Serial.println(response.status);
        // if(response.body != "-1") {
        //   while(1);  
        // }
        Serial.print("Application>\tHTTP Response Body:");
        Serial.println(response.body);
        if(response.body == "Wearing Mask") {
            tl_timer = millis();
            while((millis() - tl_timer) < 5000) {
                myservo.write(open);
            }
            touched = 0;
            myservo.write(closed);
        }
        nextTime = millis() + 10000;
    }
    delay(200);

    
}
