#!/usr/bin/env python3
import config
import gpsd
import serial
import time
import string
import pynmea2
import argparse
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

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--frequency", required=False, type=int, default=5, choices=range(1,601), metavar="[1-600]",
                    help="number of seconds between logs (default is 5)")
args = parser.parse_args()


def main():
	print("Running with", vars(args)["frequency"], "second sleep between position sends")
	while True:
		gpsd.connect()
		packet = gpsd.get_current()

		if packet.time and packet.lat and packet.lon:
			while True:
				try:
					envelope = pubnub.publish().channel(pnChannel).message({
					"lat":packet.lat,
					"lng":packet.lon
					}).sync()
					print(packet.time, "timetoken", envelope.result.timetoken, "success", packet.position())
					time.sleep(float(vars(args)["frequency"])) # sleep for set frequency
				except PubNubException as e:
					PubNubException.handle_exception(e)
					print("Exception in the pubnub send, hopefully we will retry in 1 second")
					time.sleep(1)
					continue
				else:
					print("Breaking from internal loop")
					break
		else:
			print("No GPS fix")
			time.sleep(1)
			continue

		


if __name__ == "__main__":
	main()
