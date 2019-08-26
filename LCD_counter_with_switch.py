//Robot_Arm.ino

#include <Servo.h>
#include <Wire.h>
#include <LCD.h>
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x3F,2,1,0,4,5,6,7);

const int arrLen = 20;

Servo clawServo, lowerServo, upperServo, baseServo;
int claw, lower, upper, base;

int clawPot  = 3;
int lowerPot = 2;
int upperPot = 1;
int basePot  = 0;
int vars     = 0;

int clawPin    = 6;
int lowerPin   = 10;
int upperPin   = 5;
int basePin    = 11;
int controlPin = 13;
int ledPin     = 12;

int clawArr[arrLen];
int lowerArr[arrLen];
int upperArr[arrLen];
int baseArr[arrLen];

String dataStr;
int dataArr[4];
int splitIndex = 0;
int controlState;

int servoChange = 1;
int initializeNum = 1;
int delta;

void setup() {
	lcd.begin (16,2); // for 16 x 2 LCD module
	lcd.setBacklightPin(3,POSITIVE);
	lcd.setBacklight(HIGH);
	clawServo.attach(clawPin);
	lowerServo.attach(lowerPin);
	upperServo.attach(upperPin);
	baseServo.attach(basePin);
	pinMode(controlPin, INPUT);
	pinMode(ledPin, OUTPUT);
	Serial.begin(9600);
}

void loop() {
	
	if(initializeNum == 1) {
		initialize(clawServo, 100);
	}
	else if(initializeNum == 2) {
		initialize(lowerServo, 30);
	}
	else if(initializeNum == 3) {
		initialize(upperServo, 30);
	}
	else if(initializeNum == 4) {
		initialize(baseServo, 90);
	} else {
  controlState = digitalRead(controlPin);
  if(controlState) {
  	digitalWrite(ledPin, HIGH);
  	if (Serial.available()) {
  		char ch = Serial.read();
  		dataStr += String(ch);
  		if(ch == ',') {
  			dataArr[splitIndex] = dataStr.toInt();
  			splitIndex ++;
  			dataStr = "";
  		}
  		if(ch == '|') {
  			splitIndex = 0;
  			dataStr = "";
  			if(dataArr[3] >= 0 && dataArr[3] <= 180)
  				claw  = dataArr[3];
  			if(dataArr[1] >= 0 && dataArr[1] <= 180)
  				lower = dataArr[1];
  			if(dataArr[2] >= 0 && dataArr[2] <= 180)
  				upper = dataArr[2];
  			if(dataArr[0] >= 0 && dataArr[0] <= 180)
  				base  = dataArr[0];
  			lcd.setCursor(0,0);
  			lcd.print(claw);
  			lcd.print(" ");
  			lcd.setCursor(0,1);
  			lcd.print(lower);
  			lcd.print(" ");
  			lcd.setCursor(12,0);
  			lcd.print(upper);
  			lcd.print(" ");
  			lcd.setCursor(12,1);
  			lcd.print(base);
  			lcd.print(" ");
  			clawServo.write(claw);
  			lowerServo.write(lower);
  			upperServo.write(upper);
  			baseServo.write(base);
  		}
	}
  }
  else {
  	digitalWrite(ledPin, LOW);
  	claw  = map(analogRead(clawPot),0,1023,0,150);
	lower = map(analogRead(lowerPot),0,1023,0,60);
	upper = map(analogRead(upperPot),0,1023,0,60);
	base  = map(analogRead(basePot),0,1023,0,180);
	smooth(claw, lower, upper, base);
  }
  delay(5);
}
/*
	//clawServo.write(120);
  	lowerServo.write(95);
  	//upperServo.write(95);
  	//baseServo.write(95);
  	delay(2000);
  	//clawServo.write(130);
  	lowerServo.write(115);
  	//upperServo.write(115);
  	//baseServo.write(115);
  	delay(2000);
  	*/
}

void smooth(int claw, int lower, int upper, int base) {
	if(vars < arrLen) {
		clawArr[vars]  = claw;
		lowerArr[vars] = lower;
		upperArr[vars] = upper;
		baseArr[vars]  = base;
		vars++;
	}
	else {
		for(int i=0; i<arrLen-1; i++) {
			clawArr[i]  = clawArr[i+1];
			lowerArr[i] = lowerArr[i+1];
			upperArr[i] = upperArr[i+1];
			baseArr[i]  = baseArr[i+1];
		}
		clawArr[arrLen-1]  = claw;
		lowerArr[arrLen-1] = lower;
		upperArr[arrLen-1] = upper;
		baseArr[arrLen-1]  = base;
	}
	clawServo.write(avgArr(clawArr));
  	lowerServo.write(avgArr(lowerArr));
  	upperServo.write(avgArr(upperArr));
  	baseServo.write(avgArr(baseArr));
  	Serial.print(avgArr(clawArr));
	Serial.print("\t");
	Serial.print(avgArr(lowerArr));
	Serial.print("\t");
	Serial.print(avgArr(upperArr));
	Serial.print("\t");
	Serial.println(avgArr(baseArr));
	
	//printArr(clawArr);
}

void printArr(int arr[]) {
	for(int i=0; i<arrLen-1; i++) {
		Serial.print(arr[i]);
		Serial.print(" ");
	}
	Serial.println(arr[arrLen]);	
}

int avgArr(int arr[]) {
	int total = 0;
	for(int i=0; i<arrLen; i++) {
 		total += arr[i];
 	}
 	//Serial.println(total/arrLen);
	return(total/arrLen); 
}

void initialize(Servo &theServo, int initPos) {
	delta = initPos - theServo.read();
	while(abs(delta) > 0) {
		if(delta<0)
			servoChange = -1;
		else
			servoChange = 1;
		theServo.write(theServo.read()+servoChange);
		delta = initPos - theServo.read();
		Serial.println(delta);
		delay(50);
	}
	Serial.print("done moving ");
	Serial.println(initializeNum);
	initializeNum++;
}