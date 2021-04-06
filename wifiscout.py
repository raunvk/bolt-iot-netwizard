import requests    		# to make HTTP requests
import json        		# library for handling JSON data
import time			# time library

from boltiot import Bolt    	# importing Bolt from boltiot module
import conf                 	# config file

import scapy.all as sc    	# import scapy library

try:
	file = open('wifiscout.txt', 'r')
	print (' ')
	print (file.read())
	file.close()
except IOError:
	print ('\nBanner File not found!')

mybolt = Bolt(conf.bolt_api_key, conf.device_id)

iprange = input("Enter your Wireless network IP range :\n")

prevcount = 0

status = ""

while True :

	currentcount = 0

	print("\n\n-------------------------------------")

	# Function to Scan the IP
	def scan(ip):

		arp_request = sc.ARP(pdst = ip)
		broadcast = sc.Ether(dst = "ff:ff:ff:ff:ff:ff")
		x = broadcast/arp_request
		answered_list = sc.srp(x, timeout=1, verbose=False)[0]
		targets_list = []

		for element in answered_list:
			targets_dict = {"ip":element[1].psrc, "mac":element[1].hwsrc}
			targets_list.append(targets_dict)
		return targets_list

	# Function to Print the Output Result
	def result(results_list):

		print("IP\t\tMAC Address\n-------------------------------------")

		for target in results_list:
			print(target["ip"] + "\t" + target["mac"])

		global currentcount
		currentcount = len(results_list)
		print("\nNo. of active Device(s) connected to your Wifi Network : ", currentcount, "\n")

		global prevcount
		global status

		if currentcount > prevcount :
			diff = currentcount - prevcount
			status = str(diff) + " new Device(s) were added in last 60 seconds\n"
			print(status)
			for i in range(0,2):
				mybolt.digitalWrite('0', 'HIGH')
				time.sleep(0.05)
				mybolt.digitalWrite('0', 'LOW')

		elif currentcount < prevcount :
			diff = prevcount - currentcount
			status = str(diff) + " new Device(s) were removed in last 60 seconds\n"
			print(status)
			for i in range(0,1):
                                mybolt.digitalWrite('0', 'HIGH')
                                time.sleep(0.05)
                                mybolt.digitalWrite('0', 'LOW')

		else :
			status = "No new Device(s) were added or removed in last 60 seconds\n"
			print(status)

		prevcount = currentcount

	scan_target = iprange
	scan_result = scan(scan_target)
	result(scan_result)

	# Function to send output to Telegram
	def telegram_message(message):

		url = "https://api.telegram.org/" + conf.telegram_bot_id + "/sendMessage"
		data = {"chat_id": conf.telegram_chat_id, "text": message}

		try:
			response = requests.request("POST", url, params=data)
			print("\nThis is the Telegram URL : ")
			print(url)
			print("\nThis is the Telegram response : ")
			print(response.text)
			telegram_data = json.loads(response.text)
			return telegram_data["ok"]

		except Exception as e:
			print("\nAn error occurred in sending the alert message via Telegram")
			print(e)
			return False

	message = "Details of the devices connected to your Wifi Network:\n\n" + str(scan_result) + "\n\nNo. of active Devices connected to your Wifi Network : " + str(currentcount) + "\n\n" + status

	telegram_status = telegram_message(message)
	print("\nThis is the Telegram status :\n", telegram_status, "\n")
	time.sleep(60)
