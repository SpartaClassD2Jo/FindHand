from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.onepf4f.mongodb.net/?retryWrites=true&w=majority', 27017)
db = client.dbsparta


for i in range(1, 10):
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    url = f"https://www.animal.go.kr/front/awtis/protection/protectionList.do?menuNo=1000000060&page={i}"

    driver.get(url)  # 드라이버에 해당 url의 웹페이지를 띄웁니다.
    sleep(5)  # 페이지가 로딩되는 동안 5초 간 기다립니다.

    req = driver.page_source  # html 정보를 가져옵니다.
    driver.quit()  # 정보를 가져왔으므로 드라이버는 꺼줍니다.

    # soup = BeautifulSoup(data.text, 'html.parser')
    soup = BeautifulSoup(req, 'html.parser')  # 가져온 정보를 beautifulsoup으로 파싱해줍니다.

    # searchList > div.boardList > ul:nth-child(2) > li.first
    # searchList > div.boardList > ul:nth-child(2) > li:nth-child(2)
    animalList = soup.select("#searchList > div.boardList > ul:nth-child(2) > li")
    print(len(animalList))

    for animal in animalList:

        # searchList > div.boardList > ul:nth-child(2) > li.first > div.photo > div > a > img
        # img 태그에서 src를 .get("src")로 가져옴
        img = "https://www.animal.go.kr" + animal.select_one("div.photo > div > a > img").get("src")

        # searchList > div.boardList > ul:nth-child(2) > li.first > div.txt > dl:nth-child(1) > dd
        notice_num = animal.select_one(" div.txt > dl > dd").text

        area_len = len(notice_num) - 11
        area = notice_num[:area_len]

        # searchList > div.boardList > ul:nth-child(2) > li.first > div.txt > dl:nth-child(3) > dd
        kind = animal.select_one("dl:nth-child(3) > dd").text

        # searchList > div.boardList > ul:nth-child(2) > li.first > div.txt > dl:nth-child(4) > dd
        sex = animal.select_one("dl:nth-child(4) > dd").text

        print(img, notice_num, area, kind, sex)
        doc = {
            "img": img,
            "notice_num": notice_num,
            "area": area,
            "kind": kind,
            "sex": sex,
           }
        db.animals.insert_one(doc)

