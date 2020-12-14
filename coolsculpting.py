import pandas as pd
import csv
import time
import os.path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options

class Provider:
	def __init__(self, name, address, phone, website, email):
		self.name = name
		self.address = address
		self.phone = phone
		self.website = website
		self.email = email

	def __hash__(self):
		return hash((self.name, self.address))

	def __eq__(self, other):
		return (self.name, self.address) == (other.name, other.address)

	def __ne__(self, other):
		# Not strictly necessary, but to avoid having both x==y and x!=y
		# True at the same time
		return not(self == other)

def scrape_page(browser, result_dic):
	providers = browser.find_elements_by_css_selector(".provider-card")
	for provider in providers:
		name = provider.find_element_by_css_selector(".provider-card__content__display-name").text
		address = provider.find_element_by_css_selector(".provider-card__content__address .address").text
		try:
			phone = provider.find_element_by_css_selector(".provider-card__content__address .phone").text
		except:
			phone = ""
		contact_links = provider.find_elements_by_css_selector(".contact_links")
		website = ""
		email = ""
		for contact in contact_links:
			try:
				website = contact.find_element_by_link_text("Website").get_attribute("href")
				email = contact.find_element_by_link_text("Email").get_attribute("href")
			except:
				pass

		print(name)
		listing = Provider(name, address, phone, website, email)
		if listing not in result_dic:
			result_dic[listing] = 0


def scrape(url, zipcode, result_dic):
	chrome_options = Options()
	# chrome_options.add_argument("--headless")
	
	browser = webdriver.Chrome(options=chrome_options)

	user_agent = "Chrome/87.0.4280.88"
	headers = {'User-Agent': user_agent}

	browser.implicitly_wait(10)
	browser.get(url)

	expandButton = browser.find_element_by_xpath('//div[@id="range_sort_drawer"]/button')
	browser.execute_script("arguments[0].click();", expandButton)

	slider = browser.find_element_by_xpath('//input[@name="searchRadius"]')
	# move = ActionChains(browser)
	# move.click_and_hold(en).move_by_offset(10, 0).release().perform()
	# move.drag_and_drop_by_offset(en, 20, 0).perform()

	for i in range(45):
		slider.send_keys(Keys.RIGHT)


	inputElement = browser.find_element_by_id("fadSearchInput")
	inputElement.send_keys(zipcode)

	submitButton = browser.find_element_by_id("searchButton")
	browser.execute_script("arguments[0].click();", submitButton)

	scrape_page(browser, result_dic)
	print(result_dic)

	flag = True
	while flag:
		try:
			nextButton = browser.find_element_by_css_selector(".button_container .next")
			browser.execute_script("arguments[0].click();", nextButton)

			# time.sleep(2)
			scrape_page(browser, result_dic)
			print(result_dic)
		except:
			flag = False

	browser.close()
	# return new_result_dic



if __name__ == '__main__':
	url = "https://find.coolsculpting.com/find-a-center/"
	result = {}
	fieldnames = ['Name', 'Address', 'Phone', 'Website', 'Email']

	dtype_dic = {'ZIP': int, 'ZIP_TEXT': str}
	df = pd.read_csv("ZIP_TRACT_092020.csv", dtype = dtype_dic)
	for index, row in df.iterrows():
		scrape(url, row["ZIP_TEXT"], result)
		for key in result.keys():
			if not os.path.isfile('coolsculpting.csv'):
				with open('coolsculpting.csv', 'w', newline='') as csvfile:
					writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
					writer.writeheader()
					writer.writerow({'Name': key.name,
						'Address': key.address,
						'Phone': key.phone,
						'Website': key.website,
						'Email': key.email
					})

			else:
				with open('coolsculpting.csv', 'a', newline='') as csvfile2:
					writer2 = csv.DictWriter(csvfile2, fieldnames=fieldnames)
					writer2.writerow({'Name': key.name,
						'Address': key.address,
						'Phone': key.phone,
						'Website': key.website,
						'Email': key.email
					})

