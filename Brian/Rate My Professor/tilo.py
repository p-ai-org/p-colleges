import requests
from bs4 import BeautifulSoup
import re
from selenium.webdriver.common.by import By
import time
import math
from selenium import webdriver
import json


class SchoolScraper:
	"""
	Creates an object that stores scraped data from websites related to schools.
	"""
	def __init__(self, url_list):
		"""
		Creates an object that scrapes data from URLs that it is fed and can store the data. 
		"""
		self.exceptions = []
		self.results = []
		self.browser = self.start_webdriver()

		for prof in url_list:
			try:
				html = self.load_page(self.browser,prof)
				self.results.append(self.scrape_page(html))
				time.sleep(5)
			except Exception as e:
				self.exceptions.append(prof)
				print("an exception occurred: ", prof)
				print(e)

	def start_webdriver(self):
		"""
		Creates a new Selenium instance and opens chrome.
		return: (browser) A browser.
		"""
		option = webdriver.ChromeOptions()
		chrome_prefs = {}
		option.experimental_options["prefs"] = chrome_prefs
		chrome_prefs["profile.default_content_settings"] = {"images": 2}
		chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
		DRIVER_PATH = 'C:\Users\brian\Desktop\p-colleges\p-colleges\Brian\chromedriver.exe'
		return webdriver.Chrome(executable_path=DRIVER_PATH,chrome_options=option)

	def load_page(self, browser, url):
		"""
		Loads a page given a particular url.
		browser: (browser) A browser.
		url: (str) A url.
		return: (html) A page html.
		"""
		def get_review_count(html):
			soup = BeautifulSoup(html, "html.parser")
			x = soup.find("div",{"class": "RatingValue__NumRatings-qw8sqy-0 jMkisx"})
			return int(x.find("a").text.split("\xa0")[0])
		
		def load_more_ratings():
			print("new attempt")
			print(browser.find_element(By.XPATH, '//button[text()="Load More Ratings"]'))
			browser.find_element(By.XPATH, '//button[text()="Load More Ratings"]').click()
		

		browser.get('https://www.ratemyprofessors.com'+url)
		html = browser.page_source
		for x in range( math.ceil(get_review_count(html)/10)-2):
			time.sleep(6)
			load_more_ratings()
		#about to return page source printed
		time.sleep(6)
		return browser.page_source

	def scrape_page(self, html):
		"""
		Scrapes a page from an html page for review data.
		html: (html) An html page.
		return: (list) A list of reviews that are of type dictionary.
		"""
	
		soup = BeautifulSoup(html, "html.parser")
		
		def get_Prof(soup):
			return {"professor": soup.find("div",re.compile("NameTitle__Name")).text}
		
		def get_Department(soup):
			return {"department": soup.find("div",re.compile("NameTitle__Title")).find("b").text}
		
		def scrape_review(li):
		
			def get_MetaItems(li):
				result = {}
				for mi in li.find_all("div",re.compile('MetaItem__StyledMetaItem')):
					ar = mi.text.split(": ")
					result[ar[0]] = ar[1]
				return result

			def get_CardNumRatings(li):
				result = {}
				ar = li.find_all("div",re.compile('CardNumRating__CardNumRatingNumber'))
				result["Quality"] = ar[0].text
				result["Difficulty"] = ar[1].text
				return result

			def get_Comments(li):
				return {"Comment": li.find("div",re.compile("Comments__StyledComments")).text}

			def get_Class(li):
				return {"course_id": li.find("div",re.compile("RatingHeader__StyledClass")).text}

			return {**get_Class(li),
					**get_CardNumRatings(li),
					**get_MetaItems(li),
					**get_Comments(li)}
		
		raw_reviews = soup.find("ul", {"id": "ratingsList"}).find_all("div", re.compile("Rating__StyledRating"))

		processed_reviews = []
		for rr in raw_reviews:
			review = scrape_review(rr)
			
			review.update({
				**get_Prof(soup),
				**get_Department(soup)
				})
		   
			processed_reviews.append(review)
			
		return processed_reviews

if __name__ == '__main__':
	with open("prof_links/pitzer.txt","r") as file:
		links = json.loads(file.read().replace("\'",'"'))

	sc = SchoolScraper(links)
