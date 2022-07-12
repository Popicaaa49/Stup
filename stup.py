#!/usr/bin/env python
#import smbus
import MySQLdb
import bme280

import RPi.GPIO as GPIO
import time
import os
import Adafruit_DHT

import datetime
import httplib, urllib
import serial
import schedule
import requests

now = datetime.datetime.now()

#GPIO.cleanup()
#GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN)
GPIO.setup(17, GPIO.IN) #senzor umiditate sol
GPIO.setup(27, GPIO.IN)
#GPIO.setup(servoPIN, GPIO.OUT)

def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot5216605235:AAHeOf9JsaRC73SwSeQiYmGlExEqChiJ-b0/sendMessage?chat_id=5151421790&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


def weight():
  DAT =26
  CLK=13
  GPIO.setup(CLK, GPIO.OUT)
  num=0
  i=0
  num=0
  GPIO.setup(DAT, GPIO.OUT)
  GPIO.output(DAT,1)
  GPIO.output(CLK,0)
  GPIO.setup(DAT, GPIO.IN)

  while GPIO.input(DAT) == 1:
      i=0
  for i in range(24):
        GPIO.output(CLK,1)
        num=num<<1

        GPIO.output(CLK,0)

        if GPIO.input(DAT) == 0:
            num=num+1

  GPIO.output(CLK,1)
  num=num^0x800000
  GPIO.output(CLK,0)
  wei=0
  wei=((num)/1406)
  return abs(round(((wei-5871)-95)/1000,2))

ser=serial.Serial("/dev/ttyAMA0", 9600, timeout=1)  #change ACM number as found from ls /dev/tty/ACM*
ser.close()
try:
    ser.open()
    ser.flush()
except:
    print("Port deschis")
ser.flush()


GPIO.setup(11, GPIO.OUT)        # Set pins' mode is output
GPIO.setup(12, GPIO.OUT)

#pwm = GPIO.PWM(servoPIN, 50)

#def SetAngle(angle):
#    duty = angle / 18 + 2
#    GPIO.output(servoPIN, True)
#    pwm.ChangeDutyCycle(duty)
#    time.sleep(1)
#    GPIO.output(servoPIN, False)
#    pwm.ChangeDutyCycle(0)

#GPIO.output(21, GPIO.LOW);
#while start < 60:
#    if(start%2==0):
#        GPIO.output(21, GPIO.HIGH);
#    else:
#        GPIO.output(21, GPIO.LOW);
#    start+=1
#    time.sleep(0.5)


mydb = MySQLdb.connect(
    host="localhost",
    user="stup",
    passwd="hex12300",
    database="stup"
)
#GPIO.output(20, GPIO.HIGH)

print(mydb)

def destroy():
    GPIO.cleanup()


cur = mydb.cursor("")

vreme = GPIO.input(4)
#valChannel0 = adc.read_adc(0)
#print(valChannel0)
k = 0
sol = GPIO.input(17)
aer = GPIO.input(27)
#temp,p,hum = bme280.readBME280All(addr=0x76)
p = 977
hum, temp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 16)
#humint, tempint = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 20)
while True:
    #print(getResult1())
    #stare vreme
    humint = hum
    tempint = temp
    if(ser.in_waiting > 0):
        ser.flushInput()
        vant = ser.readline().rstrip()
        print(vant)
        ser.write(str(temp).encode('utf-8'))
    dbvreme = ""
    if(vreme == 1): #1 = nu ploua, 0 = ploua
        print("Nu ploua.")
        dbvreme = "UPDATE `Vreme` SET `Stare`=1 WHERE `ID` = 0"
        stvreme = "nu ploua"
    else:
        print("Ploua")
        dbvreme = "UPDATE `Vreme` SET `Stare`=0 WHERE `ID` = 0"
        stvreme = "ploua"
    vreme = GPIO.input(4) #reiau citirea
    cur = mydb.cursor()
    cur.execute(dbvreme)
    mydb.commit()

    print("Temperatura interioara: " + str(tempint))
    print("Umiditate interioara: " + str(humint))

    dbhint = "UPDATE `Humint` SET `Valoare` = " + str(humint) +" WHERE `ID` = 0"
    cur = mydb.cursor()
    cur.execute(dbhint)
    mydb.commit()

    dbtint = "UPDATE `tempint` SET `Valoare` = " + str(tempint) +" WHERE `ID` = 0"
    cur = mydb.cursor()
    cur.execute(dbtint)
    mydb.commit()
    #humint, tempint = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 20)
    print("Temperatura exterioara: " + str(temp))
    print("Umiditatea exterioara: " + str(hum))
    hum, temp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 16)
    dbsol = ""
    if(sol == 1):
        print("Solul este uscat.")
        dbsol = "UPDATE `Sol` SET `Stare`=1 WHERE `ID` = 0"
        stsol = "uscat"
    else:
        print("Solul este umed.")
        dbsol = "UPDATE `Sol` SET `Stare`=0 WHERE `ID` = 0"
        stsol = "umed"
    #sol = GPIO.input(17)
    cur = mydb.cursor()
    cur.execute(dbsol)
    mydb.commit()
    dbaer = ""
    if(aer == 1):
        print("Aerul este curat.")
        dbaer = "UPDATE `Aer` SET `Stare`=1 WHERE `ID` = 0"
        calaer = "curat"
    else:
        print("Aerul contine impuritati (CO2, Alcool, Nitrogen, etc).")
        dbaer = "UPDATE `Aer` SET `Stare`=0 WHERE `ID` = 0"
        calaer = "contine impuritati"
    aer = GPIO.input(27)
    cur.execute(dbaer)
    mydb.commit()

    greutate = weight()
    dbgreutate = "UPDATE `Greutate` SET `suma`=" + str(greutate) + " WHERE `ID` = 0"
    print("Greutate: " + str(greutate))
    cur=mydb.cursor()
    cur.execute(dbgreutate)
    mydb.commit()

    dbtempint = "UPDATE `tempext` SET `Valoare`=" + str(temp) + " WHERE `ID` = 0"
    print("Temperatura interioara: " + str(temp))
    cur=mydb.cursor()
    cur.execute(dbtempint)
    mydb.commit()

    dbp = "UPDATE `Presiune` SET `Valoare`=" + str(p) + " WHERE `ID` = 0"
    print("Presiune: " + str(p) + " hPa")
    cur=mydb.cursor()
    cur.execute(dbp)
    mydb.commit()

    dbh = "UPDATE `Humext` SET `Valoare`=" + str(hum) + " WHERE `ID` = 0"
    print("Umiditatea interioara: " + str(hum) + " %")
    cur=mydb.cursor()
    cur.execute(dbh)
    mydb.commit()
    #temp2,p,hum2 = bme280.readBME280All()
    timp = datetime.datetime.now()
    print(str(timp))
    if(k==360):
        k=0
        iddb = "SELECT `ID` FROM `logs` ORDER BY `ID` DESC"
        cur=mydb.cursor()
        cur.execute(iddb)
        val = cur.fetchone()
        if(val is None):
            val2 = 0
        else:
            val2= int(val[0]) + 1
        vant = 0
        db = "INSERT INTO `logs`(`ID`, `Data`, `Tempint`, `Tempext`, `Vreme`, `Sol`, `Aer`, `Presiune`, `Humint`, `Humext`, `Vantviteza`, `Greutate`) VALUES (" + str(val2) + ",  '" + str(timp) + "', " + str(temp) + ", " + str(temp) + ", " + str(vreme) + ", " + str(sol) + ", " + str(aer) + ", " + str(p) +", " + str(hum) + ", 0, " + str(vant) + "," + greutate + ")"
        
        cur=mydb.cursor()
        cur.execute(db)
        mydb.commit()
        #conn = httplib.HTTPSConnection("api.pushover.net:443")
        #conn.request("POST", "/1/messages.json",
        #  urllib.urlencode({
        #    "token": "aow1i2ubivjfj9ou7kzrdcm32veaez",
        #    "user": "uuknty5h5oz84ir55uc8vajp5m51px",
        #    "title": "Stup - " + str(timp) + "",
        #    "message": "Vreme: " + stvreme + "\nUmiditate sol: " + stsol + "\nCalitate aer: " + calaer + "\nGreutate stup:" + str(greutate) +"kg\nTemperatura exterioara: " + str(temp) + " C\nTemperatura interioara: 0 C\nUmiditate exterioara: " + str(hum) + "%\nUmiditate interioara: 0%\nViteza vant: 0m/s\nPresiunea atmosferica: " + str(p) + " hPa",
        #  }), { "Content-type": "application/x-www-form-urlencoded" })
        #conn.getresponse()
    k+=1
    #print(GPIO.input(21))
    telegram_bot_sendtext("Vreme: " + stvreme + "\nUmiditate sol: " + stsol + "\nCalitate aer: " + calaer + "\nGreutate stup:" + str(greutate) +"kg\nTemperatura exterioara: " + str(temp) + " C\nTemperatura interioara: 0 C\nUmiditate exterioara: " + str(hum) + "%\nUmiditate interioara: 0%\nViteza vant: 0m/s\nPresiunea atmosferica: " + str(p) + " hPa")
    time.sleep(0.2)
