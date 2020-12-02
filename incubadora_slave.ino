#include  <TimerOne.h>          // Avaiable from http://www.arduino.cc/playground/Code/Timer1
#include <Wire.h> 
#include <LiquidCrystal_I2C.h>

volatile int i=0;               
volatile boolean zero_cross=0;  
int AC_pin=11;                
int dim=80;                   
int inc=1;                      
int freqStep=75;              
int band=0;
int NumRx1=0;
int NumRx2=0;
int NumRx3=0;
float Res1=0.0;
float Res2=0.0;
float Temp=0.0;
float Hume=0.0;
float Numero=0.0;
String str="";
int M=7;
digitalWrite(AC_pin, LOW)

LiquidCrystal_I2C lcd(0x27, 2, 1, 0, 4, 5, 6, 7, 3, POSITIVE);   

void setup() {
  lcd.begin(16, 2);
  lcd.print(" Incubadora");
  pinMode(M,OUTPUT);
  Serial.begin(9600);  // Begin setup
  pinMode(AC_pin, OUTPUT);                          // Set the Triac pin as output
  pinMode(13, OUTPUT);                              // Set the Triac pin as output
  attachInterrupt(0, zero_cross_detect, RISING);    // Attach an Interupt to Pin 2 (interupt 0) for Zero Cross Detection
  Timer1.initialize(freqStep);                      // Initialize TimerOne library for the freq we need
  Timer1.attachInterrupt(dim_check, freqStep);
}
void zero_cross_detect() {
  zero_cross = true;               // set the boolean to true to tell our dimming function that a zero cross has occured
  i=0;
  digitalWrite(AC_pin, LOW);       // turn off TRIAC (and AC)
}                                 
// Turn on the TRIAC at the appropriate time
void dim_check() {
  if(zero_cross == true) {
    if(i>=dim) {
      digitalWrite(AC_pin, HIGH); // turn on light
      i=0;                        // reset time step counter
      zero_cross = false;         //reset zero cross detection
    } 
    else {
      i++; // increment time step counter                     
    }                                
  }                                  
}                                   
void loop() {                        
  if(Serial.available()){
    char  mssg = Serial.read(); //Leemos el serial
    if (mssg=='a'){
      Serial.println("ok");{
        while(1){
          if(Serial.available()){
            str=Serial.readStringUntil('\n'); 
            NumRx1=str.toInt();
            Serial.println("ok");
            break;
          }
        }
      }
    }
    if (mssg=='b'){
      Serial.println("ok");{
        while(1){
          if(Serial.available()){
            str=Serial.readStringUntil('\n'); 
            NumRx2=str.toInt();
            //if(NumRx1==112){digitalWrite(13,LOW);}
            lcd.setCursor(0, 1);
            lcd.print("H:");
            lcd.setCursor(2, 1);
            float n4=NumRx2/10.0;
            lcd.print(n4);
            Serial.println("ok");
            break;
          }        
        }
      }
    }
    if (mssg=='c'){
      Serial.println("ok");{
        while(1){
          if(Serial.available()){
            str=Serial.readStringUntil('\n'); 
            NumRx3=str.toInt();
            //if(NumRx1==112){digitalWrite(13,LOW);
            lcd.setCursor(8, 1);
            lcd.print("T:");
            lcd.setCursor(10, 1);
            float n3=NumRx3/10.0;
            lcd.print(n3);
            Serial.println("ok");
            break;
          }        
        }
      }
    }
  }
  dim=NumRx1;
}
