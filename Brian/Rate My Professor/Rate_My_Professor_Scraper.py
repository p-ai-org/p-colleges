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

class RMPScraperByID:

    stats = {}

    def __init__(self, schoolID, scrapeOneSchool=False):
        self.schoolID = schoolID
        self.scrapeOneSchool = scrapeOneSchool
        if scrapeOneSchool:
            RMPScraperByID.stats = {}
        self.html = self.__scraper()
        self.schoolName = ""
        self.__getStats()

    def __str__(self):
        return str(RMPScraperByID.stats)

    def makeJson(self):

        dir_path = os.path.dirname(os.path.realpath(__file__))
        if self.scrapeOneSchool:
            json_file_path = os.path.join(dir_path, f'{self.schoolName}.json')
        else:
            json_file_path = os.path.join(dir_path, 'all_colleges_RMP.json')

        # json_str = json.dumps(RMPScraperByID.stats[self.schoolName])
        with open(json_file_path, 'r') as f:
            data = json.load(f)

        data[self.schoolName] = RMPScraperByID.stats[self.schoolName]


        with open(json_file_path, "w") as f:
            json.dump(data, f)

    def __scraper(self):
        driver = webdriver.Chrome()
        driver.maximize_window()

        url = f"https://www.ratemyprofessors.com/school?sid={str(self.schoolID)}"

        driver.get(url)

        # time.sleep(5)
        # # closes the "close" button
        # close_button = driver.find_element(
        #     by=By.XPATH, value="//button[@class='Buttons__Button-sc-19xdot-1 CCPAModal__StyledCloseButton-sc-10x9kq-2 gvGrz']")
        # close_button.click()

        # clicks show more button 3 times
        for _ in range(3):
            try:
                time.sleep(4)
                show_more_button = driver.find_element(
                    by=By.XPATH, value='//button[@class="Buttons__Button-sc-19xdot-1 PaginationButton__StyledPaginationButton-txi1dr-1 gjQZal"]')
                show_more_button.click()
            except:
                break

        html = driver.page_source

        soup = BeautifulSoup(html, "html.parser")
        driver.quit()

        return soup

    def __getStats(self):
        self.__getSchoolStats()
        self.__getCommentStats()

    def __getSchoolStats(self):
        try:
            self.schoolName = self.html.find("div", {
                "class": "HeaderDescription__StyledTitleName-sc-1lt205f-1 eNxccF"}).text.strip()
        except:
            print("no school at all")
            return

        RMPScraperByID.stats[self.schoolName] = {}

        try:
            RMPScraperByID.stats[self.schoolName]["School_Overall"] = float(self.html.find(
                "div", {"class": "OverallRating__Number-y66epv-3 dXoyqn"}).text.strip())
            RMPScraperByID.stats[self.schoolName]["School_Reputation"] = float(self.html.find(
                "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, string="Reputation").find_next_sibling().text.strip())
            RMPScraperByID.stats[self.schoolName]["School_Location"] = float(self.html.find(
                "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, string="Location").find_next_sibling().text.strip())
            RMPScraperByID.stats[self.schoolName]["School_Facilities"] = float(self.html.find(
                "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, string="Facilities").find_next_sibling().text.strip())
            RMPScraperByID.stats[self.schoolName]["School_Food"] = float(self.html.find(
                "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, string="Food").find_next_sibling().text.strip())
            RMPScraperByID.stats[self.schoolName]["School_Happiness"] = float(self.html.find(
                "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, string="Happiness").find_next_sibling().text.strip())
            RMPScraperByID.stats[self.schoolName]["School_Opportunities"] = float(self.html.find(
                "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, string="Opportunities").find_next_sibling().text.strip())
            RMPScraperByID.stats[self.schoolName]["School_Clubs"] = float(self.html.find(
                "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, string="Clubs").find_next_sibling().text.strip())
            RMPScraperByID.stats[self.schoolName]["School_Safety"] = float(self.html.find(
                "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, string="Safety").find_next_sibling().text.strip())
            RMPScraperByID.stats[self.schoolName]["School_Social"] = float(self.html.find(
                "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, string="Social").find_next_sibling().text.strip())
            RMPScraperByID.stats[self.schoolName]["School_Internet"] = float(self.html.find(
                "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, string="Internet").find_next_sibling().text.strip())

            RMPScraperByID.stats[self.schoolName]["Comments"] = {}
        except:
            print("no reviews")
            return

    def __extract_comment(self, text):
        pattern = r'SchoolRating__RatingComment[^>]*>([^<]*)'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            return None

    def __extract_awesomeScore(self, text):
        pattern = r'awesomeScore[^>]*>([^<]*)'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            pattern = r'averageScore[^>]*>([^<]*)'
            match = re.search(pattern, text)
            if match:
                return match.group(1)
            else:
                pattern = r'awfulScore[^>]*>([^<]*)'
                match = re.search(pattern, text)
                if match:
                    return match.group(1)
                else:
                    return None

    def __extract_review_date(self, text):
        pattern = r'TimeStamp__StyledTimeStamp-sc-9q2r30-0 bXQmMr SchoolRating__StyledTimeStamp-sb9dsm-7 bkDMlg[^>]*>([^<]*)'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            return None

    def __count_approved_substrings(self, input_string):
        approved_strings = ["DisplaySlider__DisplaySliderBox-sc-6etfq5-3 gjzHHH", "DisplaySlider__DisplaySliderBox-sc-6etfq5-3 jcnvup",
                            "DisplaySlider__DisplaySliderBox-sc-6etfq5-3 kPgDgT", "DisplaySlider__DisplaySliderBox-sc-6etfq5-3 bXxFBs",
                            "DisplaySlider__DisplaySliderBox-sc-6etfq5-3 ggogdh", "DisplaySlider__DisplaySliderBox-sc-6etfq5-3 ffSfbF",
                            "DisplaySlider__DisplaySliderBox-sc-6etfq5-3 idrjOK"]
        count = 0
        for approved_string in approved_strings:
            count += input_string.count(approved_string)
        return count

    def __extract_review_metric_and_score(self, text):
        scores = []
        metrics = ["Comment_Reputation", "Comment_Location", "Comment_Opportunities", "Comment_Facilities",
                   "Comment_Internet", "Comment_Food", "Comment_Clubs", "Comment_Social", "Comment_Happiness", "Comment_Safety"]
        slider_divs = text.find_all(
            "div", {"class": "DisplaySlider__SliderBoxContainer-sc-6etfq5-2 LReVN"})

        for slider_div in slider_divs:
            scores.append(
                int(self.__count_approved_substrings(str(slider_div))))

        return metrics, scores

    def __getCommentStats(self):
        try:
            ratings = self.html.find_all(
                'div', class_='SchoolRating__SchoolRatingContainer-sb9dsm-0 inMLDw')
            for rating in ratings:
                comment = self.__extract_comment(str(rating))
                RMPScraperByID.stats[self.schoolName]["Comments"][comment] = {}

                review_date = self.__extract_review_date(str(rating))
                RMPScraperByID.stats[self.schoolName]["Comments"][comment]["Comment_Date"] = review_date

                overall_score = self.__extract_awesomeScore(str(rating))
                RMPScraperByID.stats[self.schoolName]["Comments"][comment]["Comment_Overall"] = float(
                    overall_score)

                metrics, scores = self.__extract_review_metric_and_score(rating)

                for metric, score in zip(metrics, scores):
                    RMPScraperByID.stats[self.schoolName]["Comments"][comment][metric] = score
        except:
            return


def main():
    # scraping ALL schools and putting it into one JSON file (called all_Colleges_RMP.json)
    # I capped the number of schools to 3 (because otherwise it will take forever)
    for i in range(2358 , 6050):
        print("College number", i)
        try:
            school = RMPScraperByID(i)
            school.makeJson()
            time.sleep(10)
        except:
            print("whoops")
            time.sleep(120)
            

    # scraping ONE SPECIFIC school and putting it into its own JSON file
    # UCLA = RMPScraperByID(1075, scrapeOneSchool=True)
    # UCLA.makeJson()


if __name__ == "__main__":
    main()
