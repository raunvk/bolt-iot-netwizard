# boltiot-netwizard

**Description** : Network Anomaly Detector

**Hardware Requirement** : Wireless Network Adapter, Bolt IoT Device, Mini Buzzer, Connecting Wires

**Requisite** : Make sure you have Python3 installed in your System 

**How to Run (Linux)** :

1. Use the Wireless Network Adapter to connect to your WiFi

2. Setup the Bolt IoT Device circuit connection :

      a) Connect +ve leg of the Mini Buzzer to pin '0' of the Bolt Iot Device using Connecting Wires

      b) Connect -ve leg of the Mini Buzzer to pin 'GND' of the Bolt Iot Device using Connecting Wires

3. Install requirements.txt to install necessary packages [**$ python3 -m pip install -r requirements.txt**] 

4. Edit conf.py and add your own credentials [**$ nano conf.py**]

5. Run wifiscout.py to monitor active devices on your WiFi Network and send Telegram alerts [**$ sudo python3 wifiscout.py**]

6. Run pingmaster.py to detect anomalies in your Internet Ping by Z-Score analysis and sends Telegram alerts [**$ sudo python3 pingmaster.py**]


**Circuit Connection** :

![](circuit.png) 
 
