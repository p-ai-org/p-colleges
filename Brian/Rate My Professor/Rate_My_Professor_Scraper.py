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

# 6049
# 6048: no rating


class RMPScraperByID:

    stats = {}

    def __init__(self, schoolID):
        self.schoolID = schoolID
        self.html = self.__scraper()
        self.schoolName = ""
        self.__getStats()

    def __str__(self):
        return str(RMPScraperByID.stats)

    def makeJson(self):
        json_str = json.dumps(RMPScraperByID.stats)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        json_file_path = os.path.join(dir_path, 'all_colleges.json')

        with open(json_file_path, "a") as outfile:
            outfile.write(json_str)

    def __scraper(self):
        driver = webdriver.Chrome()
        driver.maximize_window()

        url = f"https://www.ratemyprofessors.com/school?sid={str(self.schoolID)}"

        driver.get(url)

        # time.sleep(2)
        # EC.element_to_be_clickable((By.XPATH, '''/html/body/div[5]/div/div/button'''))

        for _ in range(3):
            print("NEW ATTEMPT")
            try:
                # show_more_button = WebDriverWait(driver, 10).until(
                #     EC.element_to_be_clickable((By.XPATH, '''//a[@class='Buttons__Button-sc-19xdot-1 PaginationButton__StyledPaginationButton-txi1dr-1 gjQZal']'''))
                # )
                # show_more_button.click()
                loadMoreButton = driver.find_element_by_xpath("//button[contains(@aria-label,'Show More')]")
                time.sleep(1)
                loadMoreButton.click()

                time.sleep(2)
            except:
                print("YOU MESSED UP")
                break

        html = driver.page_source

        soup = BeautifulSoup(html, "html.parser")
        driver.quit()

        return soup

    def __getStats(self):
        self.__getSchoolStats()
        self.__getCommentStats()

    def __getSchoolStats(self):
        self.schoolName = self.html.find("div", {
            "class": "HeaderDescription__StyledTitleName-sc-1lt205f-1 eNxccF"}).text.strip()
        RMPScraperByID.stats[self.schoolName] = {}

        try:
            RMPScraperByID.stats[self.schoolName]["School_Overall"] = float(self.html.find(
                "div", {"class": "OverallRating__Number-y66epv-3 dXoyqn"}).text.strip())
            RMPScraperByID.stats[self.schoolName]["School_Reputation"] = float(self.html.find(
                "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, text="Reputation").find_next_sibling().text.strip())
            RMPScraperByID.stats[self.schoolName]["School_Location"] = float(self.html.find(
                "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, text="Location").find_next_sibling().text.strip())
            RMPScraperByID.stats[self.schoolName]["School_Facilities"] = float(self.html.find(
                "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, text="Facilities").find_next_sibling().text.strip())
            RMPScraperByID.stats[self.schoolName]["School_Food"] = float(self.html.find(
                "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, text="Food").find_next_sibling().text.strip())
            RMPScraperByID.stats[self.schoolName]["School_Happiness"] = float(self.html.find(
                "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, text="Happiness").find_next_sibling().text.strip())
            RMPScraperByID.stats[self.schoolName]["School_Opportunities"] = float(self.html.find(
                "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, text="Opportunities").find_next_sibling().text.strip())
            RMPScraperByID.stats[self.schoolName]["School_Clubs"] = float(self.html.find(
                "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, text="Clubs").find_next_sibling().text.strip())
            RMPScraperByID.stats[self.schoolName]["School_Safety"] = float(self.html.find(
                "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, text="Safety").find_next_sibling().text.strip())
            RMPScraperByID.stats[self.schoolName]["School_Social"] = float(self.html.find(
                "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, text="Social").find_next_sibling().text.strip())
            RMPScraperByID.stats[self.schoolName]["School_Internet"] = float(self.html.find(
                "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, text="Internet").find_next_sibling().text.strip())

            RMPScraperByID.stats[self.schoolName]["Comments"] = {}
        except:
            print("no reviews")

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


def main():
    school1 = RMPScraperByID("1075")
    school1.makeJson()


if __name__ == "__main__":
    main()
