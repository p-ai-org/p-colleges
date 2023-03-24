import requests
from bs4 import BeautifulSoup
import re
import json


class RMPScraperByID:

    def __init__(self, schoolID):
        self.schoolID = schoolID
        self.html = self.__scraper()
        self.stats = {}
        self.__getStats()

    def __str__(self):
        return str(self.stats)
    
    def makeJson(self):
        json_str = json.dumps(self.stats)
        name = ""
        for college in self.stats.keys():
            name = str(college)
        with open(f"{name}.json", "w") as outfile:
            outfile.write(json_str)



    def __scraper(self):
        url = f"https://www.ratemyprofessors.com/school?sid={str(self.schoolID)}"

        response = requests.get(url)
        html = response.text

        soup = BeautifulSoup(html, "html.parser")
        return soup

    def __getStats(self):
        self.__getSchoolStats()

    def __getSchoolStats(self):
        school_name = self.html.find("div", {
                                     "class": "HeaderDescription__StyledTitleName-sc-1lt205f-1 eNxccF"}).text.strip()
        self.stats[school_name] = {}

        self.stats[school_name]["School_Overall"] = self.html.find(
            "div", {"class": "OverallRating__Number-y66epv-3 dXoyqn"}).text.strip()
        self.stats[school_name]["School_Reputation"] = self.html.find(
            "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, text="Reputation").find_next_sibling().text.strip()
        self.stats[school_name]["School_Location"] = self.html.find(
            "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, text="Location").find_next_sibling().text.strip()
        self.stats[school_name]["School_Facilities"] = self.html.find(
            "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, text="Facilities").find_next_sibling().text.strip()
        self.stats[school_name]["School_Food"] = self.html.find(
            "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, text="Food").find_next_sibling().text.strip()
        self.stats[school_name]["School_Happiness"] = self.html.find(
            "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, text="Happiness").find_next_sibling().text.strip()
        self.stats[school_name]["School_Opportunities"] = self.html.find(
            "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, text="Opportunities").find_next_sibling().text.strip()
        self.stats[school_name]["School_Clubs"] = self.html.find(
            "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, text="Clubs").find_next_sibling().text.strip()
        self.stats[school_name]["School_Safety"] = self.html.find(
            "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, text="Safety").find_next_sibling().text.strip()
        self.stats[school_name]["School_Social"] = self.html.find(
            "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, text="Social").find_next_sibling().text.strip()
        self.stats[school_name]["School_Internet"] = self.html.find(
            "div", {"class": "CategoryGrade__CategoryTitle-sc-17vzv7e-1 XKroK"}, text="Internet").find_next_sibling().text.strip()


def main():
    USC = RMPScraperByID("1381")
    USC.makeJson()


if __name__ == "__main__":
    main()
