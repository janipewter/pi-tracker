#!/usr/bin/env python3
import gpsd
import serial
import time
import string
import pynmea2
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.exceptions import PubNubException
import pdb

pnChannel = "drifter-tracker";

pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-b5450a2c-3f3b-491d-9d29-260ec735fcc5"
pnconfig.publish_key = "pub-c-0f990405-f7e5-4c8b-b828-a31bea7db2b0"
pnconfig.uuid = "ad02cdee-f89f-4453-b3f8-25529bddcc24"
pnconfig.ssl = False

pubnub = PubNub(pnconfig)
pubnub.subscribe().channels(pnChannel).execute()

while True:
	gpsd.connect()
	try:
		packet = gpsd.get_current()
	except gpsd.NoFixError as e:
		print("No GPS fix:", e)
		continue

	print(packet.position())
	try:
		envelope = pubnub.publish().channel(pnChannel).message({
		"lat":packet.position()[0],
		"lng":packet.position()[1]
		}).sync()
		print("publish timetoken: %d" % envelope.result.timetoken)
	except PubNubException as e:
		handle_exception(e)

	time.sleep(2)
