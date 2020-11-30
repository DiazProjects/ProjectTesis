
#!/usr/bin/python

# Google Spreadsheet DHT Sensor Data-logging Example

# Depends on the 'gspread' and 'oauth2client' package being installed.  If you
# have pip installed execute:
#   sudo pip install gspread oauth2client

# Also it's _very important_ on the Raspberry Pi to install the python-openssl
# package because the version of Python is a bit old and can fail with Google's
# new OAuth2 based authentication.  Run the following command to install the
# the package:
#   sudo apt-get update
#   sudo apt-get install python-openssl

# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import json
import sys
import time
import datetime
import Adafruit_DHT
import gspread

import httplib
import urllib
import RPi.GPIO as GPIO
import serial

arduino = serial.Serial("/dev/ttyACM0", 9600)
DHTSensor = Adafruit_DHT.DHT22
key="1LSKKY011RMJE7NJ"
temp=0
hum=0
GPIO_Pin=4
humid_rela=0
tempe_rela=0
time.sleep(2)

contador=0

ki=1.3
kp=30
kd=8
err=0
err_1=0
ref=37.5
Up=0
Ui=0
Ui_1=0
Ud=0
U=0
hora=0
min=0
sec=0
#Pin_bomba = 7
#M2 = 8
#Vent = 5

GPIO.setmode(GPIO.BCM)
#GPIO.setup(Pin_bomba, GPIO.OUT)

from oauth2client.service_account import ServiceAccountCredentials

# Type of sensor, can be Adafruit_DHT.DHT11, Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
#DHT_TYPE = Adafruit_DHT.DHT22

# Example of sensor connected to Raspberry Pi pin 23
#DHT_PIN  = 4
# Example of sensor connected to Beaglebone Black pin P8_11
#DHT_PIN  = 'P8_11'

# Google Docs OAuth credential JSON file.  Note that the process for authenticating
# with Google docs has changed as of ~April 2015.  You _must_ use OAuth2 to log
# in and authenticate with the gspread library.  Unfortunately this process is much
# more complicated than the old process.  You _must_ carefully follow the steps on
# this page to create a new OAuth service in your Google developer console:
#   http://gspread.readthedocs.org/en/latest/oauth2.html
#
# Once you've followed the steps above you should have downloaded a .json file with
# your OAuth2 credentials.  This file has a name like SpreadsheetData-<gibberish>.json.
# Place that file in the same directory as this python script.
#
# Now one last _very important_ step before updating the spreadsheet will work.
# Go to your spreadsheet in Google Spreadsheet and share it to the email address
# inside the 'client_email' setting in the SpreadsheetData-*.json file.  For example
# if the client_email setting inside the .json file has an email address like:
#   149345334675-md0qff5f0kib41meu20f7d1habos3qcu@developer.gserviceaccount.com
# Then use the File -> Share... command in the spreadsheet to share it with read
# and write acess to the email address above.  If you don't do this step then the
# updates to the sheet will fail!
GDOCS_OAUTH_JSON       = 'spreadsheetdata@spreadsheetdata-252805.iam.gserviceaccount.com'

# Google Docs spreadsheet name.
GDOCS_SPREADSHEET_NAME = 'DHT Humidity Logs'

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS      = 10


def login_open_sheet(oauth_key_file, spreadsheet):
    """Connect to Google Docs spreadsheet and return the first worksheet."""
    try:
        scope =  ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('SpreadsheetData-d6783811f3fa.json', scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open(spreadsheet).sheet1
        return worksheet
    except Exception as ex:
        print('Unable to login and get spreadsheet.  Check OAuth credentials, spreadsheet name, and make sure spreadsheet is shared to the client_email address in the OAuth .json file!')
        print('Google sheet login failed with error:', ex)
        sys.exit(1)


print('Logging sensor measurements to {0} every {1} seconds.'.format(GDOCS_SPREADSHEET_NAME, FREQUENCY_SECONDS))
print('Press Ctrl-C to quit.')
worksheet = None
while True:
    RR = datetime.datetime.now()
    hora = RR.hour
    min = RR.minute
    sec = RR.second
    humid, temper = Adafruit_DHT.read(DHTSensor, GPIO_Pin)
    if humid is not None and temper is not None:
        humid_rela = humid
        tempe_rela = temper
        #time.sleep(2)
        #continue
    temp = tempe_rela
    hum = humid_rela
    temp = float("{0:.2f}".format(temp))
    hum = float("{0:.2f}".format(hum))
    contador = contador + 1
    err = ref - temp
    Up = kp * err
    Ui = (ki * err) + Ui_1
    if(Ui > 128):
        Ui = 128
    if(Ui < -128):
        Ui = -128
    Ud = kd * (err - err_1)
    U = Up + Ud + Ui
    Ui_1 = Ui
    ac=int(U)

    if(U > 128):
        U = 128
    if(U < -128):
        U = -128
    if(U > 0):
        U = 128 - U
    if(U < 0):
        U = U - 64

    print(temp, err, U)
    U = abs(U)
    numero1 = U
    numero2 = int(numero1)
    numero = str(numero2)

    if(contador == 1):
        arduino.write(numero)
    if(contador == 2):
        h = str('2') + str('27.1')
        arduino.write(h)
        contador = 0
        print h

    err_1 = err

    params = urllib.urlencode({'field1': temp, 'key': key})
    headers = {"Content-typZZe": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    params2 = urllib.urlencode({'field2': hum, 'key': key})
    headers2 = {"Content-typZZe": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection("api.thingspeak.com:80")
    conn2 = httplib.HTTPConnection("api.thingspeak.com:80")

    # Login if necessary.
    if worksheet is None:
        worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME)

    # Attempt to get sensor reading.
    #humidity, tempera = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)

    # Skip to the next reading if a valid measurement couldn't be taken.
    # This might happen if the CPU is under a lot of load and the sensor
    # can't be reliably read (timing is critical to read the sensor).
    #if humidity is None or temp is None:
    #    time.sleep(2)
    #    continue

    print('Temperature: {0:0.1f} C'.format(temp))
    print('Humidity:    {0:0.1f} %'.format(hum))
    print('Action Control: {0:0.1f}'.format(ac))

    # Append the data in the spreadsheet, including a timestamp
    try:
        worksheet.append_row((datetime.datetime.now().isoformat(), temp, hum, ac))
        conn.request("POST", "/update", params, headers)
        conn2.request("POST", "/update", params2, headers2)
        response = conn.getresponse()
        response2 = conn2.getresponse()
        print response.status, response.reason
        data = response.read()
        data2 = response2.read()
        conn.close()
        conn2.close()
    except:
        # Error appending data, most likely because credentials are stale.
        # Null out the worksheet so a login is performed at the top of the loop.
        print('Append error, logging in again')
        worksheet = None
        time.sleep(FREQUENCY_SECONDS)
        continue

    # Wait 30 seconds before continuing
    #print('Wrote a row to {0}'.format(GDOCS_SPREADSHEET_NAME))
    #time.sleep(FREQUENCY_SECONDS)

    temp = int(temp*10)
    hum = int(hum*10)
    print(temp, hum)
    print('envio 1')
    arduino.write(str('a'))
    holaa = arduino.readline()
    print holaa
    print('enviar AC')
    arduino.write(numero)
    holaa = arduino.readline()
    print holaa
    time.sleep(1)
    print('envio 2')
    arduino.write(str('b'))
    holaa = arduino.readline()
    print holaa
    numero = str(hum)
    print('enviar Humedad')
    arduino.write(numero)
    holaa = arduino.readline()
    print holaa
    print('envio 3')
    arduino.write(str('c'))
    holaa = arduino.readline()
    print holaa
    numero = str(temp)
    print('enviar Temperatura')
    arduino.write(numero)
    holaa = arduino.readline()
    print holaa

    print('Wrote a row to {0}'.format(GDOCS_SPREADSHEET_NAME))
    time.sleep(FREQUENCY_SECONDS)

arduino.close()
