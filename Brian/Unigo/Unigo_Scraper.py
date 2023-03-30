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
                "Bernadette" : "It's pretty chill ngl"
                "Bob" : "Hot California"
            }
        }
    }
    "Next school : etc...
}
'''


class UnigoScraper:

    stats = {}

    def __init__(self, schoolName):
        self.schoolName = schoolName
        self.schoolWebName = self.schoolName.replace(" ", "-").lower()
        self.html = self.__scraper()
        self.__getStats()

    def __str__(self):
        return str(UnigoScraper.stats)

    def makeJson(self):
        json_str = json.dumps(UnigoScraper.stats)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        json_file_path = os.path.join(dir_path, 'all_colleges_unigo.json')

        with open(json_file_path, "a") as outfile:
            outfile.write(json_str)

    def __scraper(self):
        driver = webdriver.Chrome()
        driver.maximize_window()

        url = f"https://www.unigo.com/colleges/{str(self.schoolWebName)}"
        driver.get(url)

        # clicks show more button 5 times
        for _ in range(5):
            try:
                show_more_button = driver.find_element(
                    by=By.XPATH, value="//*[text()='Load More Reviews']")
                show_more_button.click()
                time.sleep(2)
            except:
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
        UnigoScraper.stats[self.schoolName] = {}
        UnigoScraper.stats[self.schoolName]["School About"] = self.aboutSchool(
            self.html)
        UnigoScraper.stats[self.schoolName]["School Overall Score"] = int(self.getOverallScore(
            self.html))
        self.seperateReviews(self.html)
        UnigoScraper.stats[self.schoolName]["Individual Opinions"] = {}

    def __getCommentStats(self):
        self.getIndividualOpinion(self.html)
        UnigoScraper.stats[self.schoolName]["FAQ"] = {}

    def __getFAQStats(self):
        FAQ_url = [f"https://www.unigo.com/colleges/{self.schoolWebName}/describe-a-typical-weekend",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/describe-how-your-school-looks-to-someone-whos-never-seen-it",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/describe-the-best-and-worst-parts-of-the-social-scene-on-campus",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/describe-the-dorms",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/describe-the-students-at-your-school",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/describe-your-favorite-campus-traditions",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/heres-your-chance-say-anything-about-your-college",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/is-the-stereotype-of-students-at-your-school-accurate",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/tell-us-about-the-food-and-dining-options",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/tell-us-about-the-sports-scene-on-campus",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/tell-us-about-your-professors",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/what-are-the-academics-like-at-your-school",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/what-are-the-most-popular-classes-offered",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/what-are-the-most-popular-student-activities-groups",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/what-are-your-classes-like",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/what-do-students-complain-about-most",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/what-is-the-stereotype-of-students-at-your-school",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/what-is-your-overall-opinion-of-this-school",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/what-should-every-freshman-at-your-school-know-before-they-start",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/whats-the-dating-scene-like",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/whats-the-greek-scene-like",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/whats-unique-about-your-campus",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/when-you-step-off-campus-what-do-you-see",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/where-is-the-best-place-to-get-work-done-on-campus",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/why-did-you-decide-to-go-to-this-school",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/what-is-the-stereotype-of-students-at-your-school-is-this-stereotype-accurate",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/whats-the-one-thing-you-wish-someone-had-told-you-about-freshman-year",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/whats-the-hardest-thing-about-freshman-year",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/i-dont-drink-will-it-be-hard-for-me-to-go-to-parties",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/how-often-should-i-phone-home-is-once-a-day-too-much",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/what-do-you-consider-the-worst-thing-about-your-school-why",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/what-kind-of-person-should-attend-this-school",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/what-kind-of-person-should-not-attend-this-school",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/what-do-you-brag-about-most-when-you-tell-your-friends-about-your-school",
                   f"https://www.unigo.com/colleges/{self.schoolWebName}/whats-the-most-frustrating-thing-about-your-school"]

        for url in FAQ_url:
            try:
                # TODO: FIX ME!
                print(url)
                response = requests.get(url)
                soup = BeautifulSoup(response.content, "html.parser")

                UnigoScraper.stats[self.schoolName]["FAQ"] = {}
                question = self.getFAQQuestion(soup)
                UnigoScraper.stats[self.schoolName]["FAQ"][question] = {}
                name, comment = self.getFAQNameAndComment(soup)
                UnigoScraper.stats[self.schoolName]["FAQ"][question][name] = comment
            except:
                continue

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
        question = header_div.find("h2")
        return question.text

    def getFAQNameAndComment(self, soup):
        reviews = soup.find_all(
            'div', class_='overall-college-user-review-container')
        names = []
        comments = []

        for review in reviews:
            names.append(review.find('strong').text)
            comments.append(review.find('p').text)

        return names, comments


def main():
    school = UnigoScraper("University of California-Los Angeles")

    school.makeJson()


if __name__ == "__main__":
    main()
