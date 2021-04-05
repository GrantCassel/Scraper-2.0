# Program Created By: GC
# Description: Scrapes the Newegg.com website and collects the relevant data and dumps it into a CSV file to be cleaned
# Created Date: 4/1/2021
# Version: 1.1

#  --Ideas--

# TODO Create my own file of categories and their corresponding URLs
# TODO Save the unique ID in the URL and not the URL itself
# TODO Make it possible to load a list of URLS to scrape instead of scraping everything
# TODO Get the unique number of each item in order and save it
# TODO Save the category to each item
# TODO Change from date to timestamp (Can go from timestamp to date or time but can not go the other way around)

# TODO Make cleaning the data into its own python script (Automatically call it here) yet keep a version of the dirty data in a CSV

# Changelog

# 1.1
# Changed variable names to more resemble what they actually are
# Fixed getting the total page count for a given URL
# Data now gets dumped after every URL
# Added multiple pageSoups so it doesn't pull the same page every time

#1.2
# Lists are now automatically created by the classNames key and are auto inputed into the dataframe
# In order to add a new field to scrape you now just need to add a new key,value to classNames

# TODO Somehow dynamically find page numbers (Or set a cap and delete the duplicates since they usually put the "best" items first)
# TODO Load classNames from files within a folder to dynamically scrape through websites

from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
from random import randint
from time import sleep
import datetime
import time
import re
import pandas as pd

# Debug-Mode
debug = True

# The URL to the main page we are scanning
pageString = 'https://www.newegg.com/p/pl?LeftPriceRange=0+100000&PageSize=96&Order=3'

# A dictionary of the associated name and class name
# Class names are inputed using || instead of "" and are later changed
classNames = {
	# Not all have the same # of Lines. It errors it out if it doesn't have the correct number of lines(AKA Doesn't have a model number)
	"ModelNumber" : """"item-features").findAll('li')[100 if len(item.find(class_="item-features").findAll('li')) == 3 else 4].text""",
	"ItemName" : """"item-img").img['title']""",
	"ItemBrand" : """"item-brand").img['title']""",
	"ItemURL" : """"item-img")['href']""",
	"ItemPriceBefore" : """"price-was-data").text""",
	"ItemPriceAfter" : """"price-current").text""",
	"ItemPercentSaved" : """"price-save-percent").text""",
	"ItemShippingPrice" : """"price-ship").text""",
	"ItemPromoDiscount" : """"item-promo").text""",
	"ItemNumberOfReviews" : """"item-rating-num").text"""
}

# Keeps track of time
startTime = time.time()

# Grab the beginning HTML page
uClient = uReq(pageString)
page_html = uClient.read()
uClient.close()

# Page info
pageSoup = soup(page_html, "html.parser")

# All of the URLs we need to scrape
pagesToScrape = []

# All of the filter boxes on the current page
categories = pageSoup.find(class_="filter-box-body").findAll(class_="filter-box-list")

# Loop through all the filter boxes and save the pages
for category in categories:
	# Save the URLs into the pagesToScrape
	pagesToScrape.append(category.a.get('href'))
	print(category.a.get('href'))

# The total number of URLS we have scraped
urlsCompleted = 0

# Loop through all the pages
for url in pagesToScrape:

	# The list which holds all the data
	# Very important to spell correctly. They are named the same as the className keys

	# POSSIBLE TODO

	# Auto exec the variables by the classNames key in order to make you only have to add the class kery

	for key in classNames:
		exec("global " + key + "; " + key + " = []")


	# The total amount of pages searched for the url
	pagesSearched = 1

	# Get the total number of pages
	client = uReq(url)
	html = client.read()
	client.close()

	pageSoup = soup(html, "html.parser")

	totalPages = pageSoup.find(class_="list-tool-pagination-text").find('strong').text
	totalPages = totalPages[2:]

	totalPages = str(3)

	# We search for pages - 3 since it includes the non first page, and the dead last page
	while(str(pagesSearched) != totalPages):

		# Sleep for a random amount of time between pulls in order to not get blocked
		# TODO Look for ways around this so I can reduce the time it takes to complete the scrape
		sleep(randint(1,2))

		# Increase the PageCount
		pagesSearched += 1

		# Output current page number
		if debug:
			print("Loaded page # " + str(pagesSearched) + "/" + totalPages)

		# Determine which URL to use
		if(pagesSearched > 0):
			uClient = uReq(url + "&Page=" + str(pagesSearched))
			print(url + "&Page=" + str(pagesSearched))
		else:
			uClient = uReq(url)

		# Grab the new page
		pagehtml = uClient.read()
		pageSoup = soup(pagehtml, "html.parser")
		uClient.close()

		# Find all the items
		items = pageSoup.find("div", {"class":"item-cells-wrap border-cells items-grid-view four-cells expulsion-one-cell"})

		# Loop through all the items
		for item in items:
			for classKey in classNames:
				try:
					globals()[classKey].append(eval("item.find(class_=" + str(classNames[classKey])))
				except:
					# Why append NULL? Makes more data to clean (Just test before removing it completely though)
					globals()[classKey].append("NULL")

	# Console print the progress
	urlsCompleted += 1

	classVariables = {}

	# Get a list of all variables
	for key in classNames.keys():
		print(classNames[key])
		classVariables[key] = globals()[str(key)]

	# Import it into a DataFrame
	scrapedData = pd.DataFrame.from_dict(classVariables)

	# TODO Clean the data
	# Add into debug mode to save a copy of the dirty data
	# Make sure to import the new file and call the function which cleans the data
	# Then save the data

	print(scrapedData.head())

	scrapedData.drop_duplicates()

	# Timestamp every column
	scrapedData['Date'] = str(datetime.datetime.now().strftime("%d %B %Y"))

	# Export the dataframe into a CSV file
	scrapedData.to_csv("Newegg Scrape " + str(datetime.datetime.now().strftime("%d %B %Y")) + ".csv", mode='a')

	if debug:
		print("Completed URL  #" + str(urlsCompleted) + "/" + str(len(pagesToScrape)))

# Print out the elapsed time
print("Script ran successfully after: " + str(float(startTime) - float(time.time())))