#-------------------------------------------------------------------------------------------------------------------
# Created by: Jacob Milner
# Assignment: TGIS 501A - Lab 7
# Purpose: Create a shapefile from Twitter REST API results, see if anyone is still talking about the Seattle Sonics
# Output: SonicsTweets.shp
#-------------------------------------------------------------------------------------------------------------------

# PART ONE - GET TWEETS AND SAVE IN A TEXT FILE

from TwitterSearch import *
from geopy import geocoders
import io

# Process: Create geocoding function using Google V3 geocoding service
def geo(location):
	geocoder = geocoders.GoogleV3()
	loc = geocoder.geocode(location)
	return loc.latitude, loc.longitude

try:
	# Process: Create a TwitterSearchOrder object, define search terms
	TSO = TwitterSearchOrder()
	keywords = ['Seattle', 'Sonics']
	print 'Search: ' + str(keywords)
	TSO.set_keywords(keywords)
	TSO.set_include_entities(False) # Do not return all entity information

	# Process: Create a search object, provide access token
	TS = TwitterSearch(
		consumer_key = 'cRzN3CXcvqne8J1mlNYZuNXok'
		consumer_secret = 'cGr7D4QRF8Y0fMNrvNp3dyPHpGnhYbaYrfNWA0qviVmgcy0z6z'
		access_token = '2864985021-wGFEFP5bHBzZBQMSyQFJh0bnZv7jc0GYHlJYgl2'
		access_token_secret = 'UytdgfgnflbvVLasljHcA2h0FUdX1fHJwmQyVfX92lWGA'
	)

	results = "TwitterSearchData.txt" # Create a new text file to store tweet data

	with io.open(results, 'w', encoding='utf8') as f:
		i = 1
		for tweet in TS.search_tweets_iterable(TSO): # loop through the search object
			if tweet['place'] is not None: # do not return tweets without a location
				(lat, lng) = geo(tweet['place']['full_name']) # sets lat, long variables from geocoded location
				f.write(str(lat) + '\t' + str(lng) + '\t' + tweet['user']['screen_name'] + '\t') # write records as a tab-delimited text file (lat, long, screen name, tweet)
				f.write(tweet['text'].replace('\n', ' ') + '\n') # strip new lines from text
				i = i + 1
		print str(i-1) + ' rows written'

except TwitterSearchException as e:
	print(e)


# PART TWO - CREATE POINT SHAPEFILE FROM TEXT FILE
#-------------------------------------------------------------------------------------------------------
# NOTE: Please comment out all code in Part One after generating text file to avoid exceeding API limit
#-------------------------------------------------------------------------------------------------------

import arcpy
from arcpy import env
import csv

# Process: Set local variables
folder = "C:/Users/Jacob/Desktop/Lab7/"
env.workspace = folder
env.overwiteOutput = True

# Process: Create new empty point shapefile
TSfc = arcpy.CreateFeatureClass_management(folder, 'SonicsTweets.shp', 'POINT', '', 'DISABLED', 'DISABLED', '')

# Process: Add attribute fields to point shapefile
arcpy.AddField_management(TSfc, 'ID', 'LONG')
arcpy.AddField_management(TSfc, 'SHAPE@XY', 'DOUBLE')
arcpy.AddField_management(TSfc, 'scrname', 'TEXT', '', '', 15)
arcpy.AddField_management(TSfc, 'tweetmsg', 'TEXT', '', '', 255)

# Using text file from Part One, insert attribute table records
with open(results, 'rb') as f:
	reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE) # reads tab-delimited data
	with arcpy.da.InsertCursor(TSfc, ['ID', 'SHAPE@XY', 'scrname', 'tweetmsg']) as cursor:
		i = 1
		for row in reader:
			newpoint = (float(row[1]), float(row[0]))
			cursor.insertRow((i, newpoint, row[2], row[3]))
			print i, newpoint, row[2]
			i = i + 1
	del cursor
