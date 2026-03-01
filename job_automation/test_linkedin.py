import requests
from bs4 import BeautifulSoup
import urllib.parse

def test_linkedin():
    url = f"https://www.linkedin.com/jobs/search?keywords={urllib.parse.quote('machine learning')}&location={urllib.parse.quote('Remote')}&f_TPR=r86400"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = soup.find_all("div", class_="base-search-card__info")
    print(f"Found {len(jobs)} jobs on LinkedIn.")
test_linkedin()
