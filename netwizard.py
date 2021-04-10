import requests			# to make HTTP requests
import json			# library for handling JSON data
import time			# time library
import math, statistics		# maths library to compute Z-score
from boltiot import Bolt	# importing Bolt from boltiot module
import speedtest		# speedtest library to check Network speed
import conf			# config file
import scapy.all as sc    	# import scapy library

try:
    file = open('netwizard.txt', 'r')
    print (' ')
    print (file.read())
    file.close()
except IOError:
    print ('\nBanner File not found!')

mybolt = Bolt(conf.bolt_api_key, conf.device_id)

ping_history=[]

iprange = input("Enter your Wireless network IP range :\n")

prevcount = 0

status = ""

currentcount = 0


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

	print("\nConnected Devices :")
	print("\n-------------------------------------")
	print("IP\t\tMAC Address\n-------------------------------------")

	for target in results_list:
		print(target["ip"] + "\t" + target["mac"])

	global currentcount
	currentcount = len(results_list)
	print("\nNo. of active Device(s) in your Wifi : ", currentcount, "\n")

	global prevcount
	global status

	if currentcount > prevcount :
		diff = currentcount - prevcount
		status = str(diff) + " new Device(s) were added in last 60 seconds\n"
		print(status)
		

	elif currentcount < prevcount :
		diff = prevcount - currentcount
		status = str(diff) + " new Device(s) were removed in last 60 seconds\n"
		print(status)
		
	else :
		status = "No new Device(s) were added or removed in last 60 seconds\n"
		print(status)

	for i in range(0, currentcount):
		mybolt.digitalWrite('0', 'HIGH')
		time.sleep(0.05)
		mybolt.digitalWrite('0', 'LOW')

	prevcount = currentcount


# Function to compute Upper and Lower Bounds by Z-Score Analysis
def compute_bounds(ping_history,frame_size,factor):
	if len(ping_history) < frame_size:
		return None
	if len(ping_history) > frame_size:
		del ping_history[0:len(ping_history)-frame_size]

	Mn=statistics.mean(ping_history)
	Variance=0
	for data in ping_history:
		Variance += math.pow((data-Mn),2)

	Zn = factor*math.sqrt(Variance/frame_size)
	High_bound = ping_history[frame_size-1]+Zn
	Low_bound = ping_history[frame_size-1]-Zn
	return [High_bound,Low_bound]


# Function to test Network Speed
def test():
	try:
		s = speedtest.Speedtest()
		s.get_servers()
		s.get_best_server()
		s.download()
		s.upload()
		res = s.results.dict()
		return res["download"], res["upload"], res["ping"]

	except Exception as e:
		print("\nInternet connection was lost :(")
		print("\nPlease connect to your Internet and try again !\n")


# Function to send output to Telegram
def telegram_message(message):

	url = "https://api.telegram.org/" + conf.telegram_bot_id + "/sendMessage"
	data = {"chat_id": conf.telegram_chat_id, "text": message}

	try:
		response = requests.request("POST", url, params=data)
		#print("\nThis is the Telegram URL : ")
		#print(url)
		#print("\nThis is the Telegram response : ")
		#print(response.text)
		telegram_data = json.loads(response.text)
		return telegram_data["ok"]

	except Exception as e:
		print("\nAn error occurred in sending the alert message via Telegram")
		print(e)
		return False


while True :

	scan_target = iprange
	scan_result = scan(scan_target)
	result(scan_result)

	message = "Connected Devices :\n\n" + str(scan_result) + "\n\nNo. of active Devices in your Wifi : " + str(currentcount) + "\n\n" + status

	telegram_status = telegram_message(message)
	print("This is the Telegram status : ", telegram_status, "\n")

	d, u, p = test()
	print('\nNetwork Information :\n')
	print('Download : {:.2f} Kb/s\n'.format(d / 1024))
	print('Upload : {:.2f} Kb/s\n'.format(u / 1024))
	print('Ping : {:.2f} \n'.format(p))
	ping_value = int(p)

	bound = compute_bounds(ping_history,conf.frame_size,conf.mul_factor)
	if not bound:
		required_data_count = conf.frame_size-len(ping_history)
		print("Not enough data to compute Z-score. Need ",required_data_count," more data point(s) !")
		ping_history.append(ping_value)
		continue

	try:
		if ping_value > bound[0] :
			print ("Ping increased suddenly. Sending an alert via Telegram....")
			message = "Your Ping has increased suddenly." + "\nCurrent Ping value is : " + str(ping_value)
			message += "\nConsider disconnecting some Devices from your Network or switch to a better Network !"
			telegram_status = telegram_message(message)
			print ("\nThis is the Telegram status : ", telegram_status, "\n")
			for i in range(0,9):
				mybolt.digitalWrite('1', 'HIGH')
				time.sleep(0.05)
				mybolt.digitalWrite('1', 'LOW')

		ping_history.append(ping_value)

	except Exception as e:
		print ("Error : ",e)
	time.sleep(10)
