#!/usr/bin/env python3
import config
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
pnconfig.subscribe_key = config.subscribe_key
pnconfig.publish_key = config.publish_key
pnconfig.uuid = config.uuid
pnconfig.ssl = False

pubnub = PubNub(pnconfig)
pubnub.subscribe().channels(pnChannel).execute()

while True:
	gpsd.connect()
	packet = gpsd.get_current()

	if packet.time and packet.lat and packet.lon:
		try:
			envelope = pubnub.publish().channel(pnChannel).message({
			"lat":packet.lat,
			"lng":packet.lon
			}).sync()
			print(packet.time, "timetoken", envelope.result.timetoken, "success", packet.position())
		except PubNubException as e:
			handle_exception(e)
			pass
	else:
		print("No GPS fix")
		continue

	time.sleep(5)
