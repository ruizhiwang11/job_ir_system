import requests
import colorama
import time
import csv
import os
import argparse
import json
from bs4 import BeautifulSoup as soup
import pandas as pd

class JobGetter:
    def __init__(self, job_name, location):
        self.job_name = job_name
        self.location = location
        self.max_page_search = 5
        self.job_links = []
        self.job_data = {}


    def get_job_link_by_location(self):
        try:

            for i in range(0, self.max_page_search):
                req = requests.get(
                    f'https://www.jobstreet.com.sg/en/job-search/{self.job_name}-jobs-in-{self.location}/{i}'
                )
                req.raise_for_status()
                # create Soup
                page_soup = soup(req.text, 'html.parser')
                reqs = page_soup.findAll("a", {"class": "_18qlyvc12 _9tnmfh1 _18qlyvc2 sx2jih0 sx2jihe zcydq824"})
                
                for re in reqs:
                    if "token" not in re["href"]:
                        continue
                    self.job_links.append("https://www.jobstreet.com.sg"+re["href"])

        except requests.HTTPError as err:
            print(colorama.Fore.RED,
                  f'[!!] Something went wrong! {err}', colorama.Style.RESET_ALL)

    def parse_job_data(self):
        
        for id ,link in enumerate(self.job_links):
            req = requests.get(
                link
            )
            req.raise_for_status()

            # create Soup
            page_soup = soup(req.text, 'html.parser')
            job_title = page_soup.find("h1", {"class": "sx2jih0 _18qlyvc0 _18qlyvch _1d0g9qk4 _18qlyvcp _18qlyvc13"})

            div_tag = page_soup.findAll("div", {"class": "sx2jih0 zcydq84i"})[0]
            company_name = div_tag.find_next("span", {"class": "sx2jih0 zcydq82q _18qlyvc0 _18qlyvc13 _18qlyvc2 _1d0g9qk4 _18qlyvcb"})

            description_tag = page_soup.find("div", {"class": "sx2jih0 _2KCML_0 ZFCb8_0"})
            texts = description_tag.findAll(text=True)
            index1 = 0
            index2 = 0
            for i, text in enumerate(texts):
                if text == "Job Description":
                    index1 = int(i)
                if text == "Additional Information":
                    index2 = int(i)
                    break
            usable_texts = texts[index1+1:index2]
            move = dict.fromkeys((ord(c) for c in u"()-·\xa0\n\t\u2022"))
            for i, text in enumerate(usable_texts):
                tmp = text.translate(move)
                usable_texts[i] = tmp
            
            usable_texts[:] = [x for x in usable_texts if len(x) > 5]
            usable_texts[:] = [x for x in usable_texts if "EA" not in x]
            usable_texts[:] = [x for x in usable_texts if "RA" not in x]
            usable_texts[:] = [x for x in usable_texts if "[" not in x and "]" not in x]
            usable_texts[:] = [x for x in usable_texts if not (")" in x and "(" not in x)]
            usable_texts[:] = [x for x in usable_texts if not ("Reg" in x or "License" in x)]
            time.sleep(1)        
            dic_data = {
                "job title": job_title.string,
                "company": company_name.string,
                "category": self.job_name,
                "location": self.location,
                "description": usable_texts
            }
            self.job_data[id] = dic_data

    def generate_json(self):
        self.get_job_link_by_location()
        self.parse_job_data()
        with open(f"./{self.job_name}-{self.location}.json", "w") as f:
            f.write(json.dumps(self.job_data)) 

getter = JobGetter("software engineer", "central")
getter.generate_json()