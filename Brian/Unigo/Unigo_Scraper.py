import requests
from bs4 import BeautifulSoup
import re
import json
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

'''
EXAMPLE
{
    "University of California-Los Angeles" : {
        "About" : "Founded in 1919, University of California-Los Angeles.",
        "School Overall Score" : 4.5,
        "School On-campus housing" : 3.4,
        "School Off-campus housing" : 3.0,
        "School Campus food" : 3.6,
        "School Campus facilities" : 4.4,
        "Individual Opinions" : {
            "Anna" : {
                "Rating" : 4
                "Comment" : "UCLA is a great place"
            }
        }
        "FAQ" : {
            "Describe a typical weekend" : {
                "Bernadette" : "It's pretty chill"
                "Bob" : "Hot California"
            }
        }
    }
    "Next school : etc...
}
'''


class UnigoScraper:

    stats = {}

    def __init__(self, schoolName, scrapeOneSchool=False):
        self.schoolName = schoolName
        self.scrapeOneSchool = scrapeOneSchool
        if self.scrapeOneSchool:
            UnigoScraper.stats = {}
        self.schoolWebName = self.schoolName.replace(" ", "-").lower()
        self.html = self.__scraper()
        self.__getStats()

    def __str__(self):
        return str(UnigoScraper.stats)

    def makeJson(self):

        dir_path = os.path.dirname(os.path.realpath(__file__))
        if self.scrapeOneSchool:
            json_file_path = os.path.join(dir_path, f'{self.schoolName}.json')
        else:
            json_file_path = os.path.join(dir_path, 'all_colleges_Unigo.json')

        # json_str = json.dumps(RMPScraperByID.stats[self.schoolName])
        with open(json_file_path, 'r') as f:
            data = json.load(f)

        data[self.schoolName] = UnigoScraper.stats[self.schoolName]


        with open(json_file_path, "w") as f:
            json.dump(data, f)

    def __scraper(self):
        driver = webdriver.Chrome()
        driver.maximize_window()

        url = f"https://www.unigo.com/colleges/{str(self.schoolWebName)}"
        driver.get(url)

        # clicks show more button 5 times
        for _ in range(3):
            try:
                time.sleep(3)
                show_more_button = driver.find_element(
                    by=By.XPATH, value="//*[text()='Load More Reviews']")
                driver.execute_script("arguments[0].click();", show_more_button)
                # show_more_button.click()
            except Exception as e:
                print("No load more", e)
                break

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        driver.quit()
        return soup

    def __getStats(self):
        self.__getSchoolStats()
        self.__getCommentStats()
        self.__getFAQStats()

    def __getSchoolStats(self):
        try:
            UnigoScraper.stats[self.schoolName] = {}
            UnigoScraper.stats[self.schoolName]["School About"] = self.aboutSchool(
                self.html)
            UnigoScraper.stats[self.schoolName]["School Overall Score"] = int(self.getOverallScore(
                self.html))
            self.seperateReviews(self.html)
            UnigoScraper.stats[self.schoolName]["Individual Opinions"] = {}
        except:
            return

    def __getCommentStats(self):
        try:
            self.getIndividualOpinion(self.html)
            UnigoScraper.stats[self.schoolName]["FAQ"] = {}
        except:
            return

    def __getFAQStats(self):
        try:
            FAQ_url = []

            # read_all_link = self.html.find(
            #     "a", text=lambda text: "Read all" in text, href=True)

            for link in self.html.find_all('a'):
                if 'Read all' in link.text:

                    read_all_link = link.get('href')
                    break

            link = "https://www.unigo.com" + read_all_link
            response = requests.get(link)
            soup = BeautifulSoup(response.content, "html.parser")

            select_tag = soup.find("select", {"id": "schoolQuestionSelect"})
            if select_tag:
                option_tags = select_tag.find_all("option")
                for option in option_tags:
                    value = option["value"]
                    FAQ_url.append("https://www.unigo.com" + value)

            for url in FAQ_url:
                try:
                    response = requests.get(url)
                    soup = BeautifulSoup(response.content, "html.parser")

                    question = self.getFAQQuestion(soup)
                    self.getFAQNameAndComment(soup, question)
                    time.sleep(4)
                    # UnigoScraper.stats[self.schoolName]["FAQ"][question][name] = comment
                except:
                    continue
        except:
            return

    def aboutSchool(self, soup):
        aboutSchoolStr = ""
        college_info_container = soup.find(
            'div', {'class': 'college-general-information-container'})
        h2_tags = college_info_container.find_all('h2')
        info_paragraphs = []

        if len(h2_tags) >= 2:
            first_h2_tag = h2_tags[0]
            second_h2_tag = h2_tags[1]

            for sibling in first_h2_tag.next_siblings:
                if sibling == second_h2_tag:
                    break
                elif sibling.name == 'p':
                    info_paragraphs.append(sibling.get_text())

        for p in info_paragraphs:
            aboutSchoolStr += p

        return aboutSchoolStr

    def getOverallScore(self, soup):
        star_rating = soup.find('div', {'class': 'col-sm-2 star-rating'})
        percentage = star_rating.find('div', {'class': 'front-stars'})['style']
        percentage = percentage.replace('width:', '').replace('%', '').strip()
        return round(float(percentage) / 20, 2)  # out of 5

    def get_second_number(self, lst):
        second_num = None
        for i in range(len(lst)):
            try:
                num = float(lst[i])
                if i != 0:
                    second_num = num
                    break
            except:
                pass
        return second_num

    def seperateReviews(self, soup):
        reviews_anchor_tag = soup.find(
            'a', {'class': 'anchor-link', 'id': 'Reviews'})
        if reviews_anchor_tag:
            h4_tags = reviews_anchor_tag.find_all_next('h4')
            for h4 in h4_tags:
                h4_text = h4.get_text().strip()
                if h4_text.startswith('How would you rate'):
                    h4_text = h4_text[len('How would you rate'):].strip()
                    h4_text = h4_text[:-1].strip().capitalize()
                    p_tag = h4.find_next_sibling('p')
                    if p_tag:
                        p_text = p_tag.get_text().strip()
                        individualReview = self.get_second_number(
                            p_text.split())
                        # print(f"{h4_text}: {individualReview}")
                        UnigoScraper.stats[self.schoolName][f"School {h4_text}"] = int(
                            individualReview)

    def getIndividualOpinion(self, soup):
        reviews_list = soup.find("div", class_="reviews-list")

        for name in reviews_list.find_all("strong"):
            div_tag = name.find_next_sibling("div")

            rating = div_tag["data-review-count"]  # out of five
            p_tag = name.find_next_sibling("p")
            UnigoScraper.stats[self.schoolName]["Individual Opinions"][name.text] = {
            }
            UnigoScraper.stats[self.schoolName]["Individual Opinions"][name.text]["Rating"] = int(
                rating)
            UnigoScraper.stats[self.schoolName]["Individual Opinions"][name.text]["Comment"] = p_tag.text

    def getFAQQuestion(self, soup):
        header_div = soup.find(
            "div", class_="college-review-question-header-container")
        question = header_div.find("h2").text
        UnigoScraper.stats[self.schoolName]["FAQ"][question] = {}
        return question

    def getFAQNameAndComment(self, soup, question):
        reviews = soup.find_all(
            'div', class_='overall-college-user-review-container')

        for review in reviews:
            name = review.find('strong').text
            comment = review.find('p').text

            UnigoScraper.stats[self.schoolName]["FAQ"][question][name] = comment


def main():
    dir_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(dir_path, "all_colleges_Unigo.json")

    if not os.path.isfile(file_path):

        data = {}
        with open(file_path, "w") as f:
            json.dump(data, f)

    # RUN THIS (MULTIPLE COLLEGES)
    
    filename = "/Users/hmcuser/Desktop/p-colleges/Brian/Unigo/FilteredCampus.csv"
    counter = 1

    with open(filename, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            try:
                print("School", counter, ''.join(row))
                counter += 1

                if counter > 529:
                    school = UnigoScraper(''.join(row))
                    school.makeJson()
                # if counter == 5:
                #     break
                    time.sleep(5)
            except Exception as e:
                print("Some sort of error: ", e)
                time.sleep(30)
                continue

    


    # OR THIS (ONE COLLEGE)
    # school = UnigoScraper("University of Southern California")
    # school.makeJson()


if __name__ == "__main__":
    main()
