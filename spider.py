# https://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python
# https://stackoverflow.com/questions/5137497/find-current-directory-and-files-directory
# https://stackoverflow.com/questions/273192/how-to-check-if-a-directory-exists-and-create-it-if-necessary
# https://stackoverflow.com/questions/12519074/scrape-websites-with-infinite-scrolling

from tqdm import tqdm
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import sys
import unittest, time, re

def getFileData(url=None):
    return requests.get(url, stream=True)

def saveFileData(url=None, destination=None):
    fileName = getFileName(url)
    response = getFileData(url)
    if destination and fileName:
        fileName = destination + fileName
    with open(fileName, "wb") as handle:
        for data in tqdm(response.iter_content()):
            handle.write(data)
    return response

def getFileName(url=None):
    return url.split("/")[len(url.split("/"))-1]

def getFilePath(url=None):
    return url.split("/").remove(getFileName(url))

def getPageSource(url=None):
    returns = ""
    rawData = getFileData(url)
    rawData.encoding = 'utf-8'
    for data in tqdm(rawData.iter_content()):
        returns += str(data)
    return returns

def getLocalPageSource(url=None):
    page = readTextFile(url)
    return page

def writeTextFile(name="test.txt", lines=None):
    file = open(name,"w") 
    for line in lines:
        file.write(line) 
    file.close() 

def readTextFile(name="text.txt"):
    file = open(name, "r") 
    return file.read() 

def makeDir(url=None):
    if not os.path.exists(url):
        os.makedirs(url)
    return url + os.sep

def cwdFile(url=None):
    return os.path.join(os.getcwd(), url)

def makeCwdDir(url=None):
    url = cwdFile(url)
    return makeDir(url)

# https://sites.google.com/a/chromium.org/chromedriver/home
def scrollScraper(url=None, linkText="Load more"):
    driver = webdriver.Chrome()
    driver.implicitly_wait(30)
    delay = 3
    driver.get(url)
    driver.find_element_by_link_text(linkText).click()
    for i in range(1,100):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #time.sleep(4)
    time.sleep(4)
    html_source = driver.page_source
    data = html_source.encode('utf-8')
    return str(data)

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

def getVideos(url=None, scroll=False):
    offline = True
    if (url.startswith("http")):
        offline = False

    pageCodes = []
    pageUrls = []
    fileUrls = []

    # step 1
    page = None
    if (offline==True):
        page = getLocalPageSource(url).split(",")
    else:
        if (scroll==False):
        	page = getPageSource(url).split(",")
        else:
        	page = scrollScraper(url).split(",")

    for line in page:
        if line.startswith(" \"code\""):
            line = line.split(":")
            pageCode = line[1]
            if (offline==False and scroll==False):
                pageCode = pageCode.replace("b\'", "").replace("\'", "")
            pageCode = pageCode.replace("\"", "").replace(" ", "")
            pageCodes.append(pageCode)

    for pageCode in pageCodes:
        pageUrl = "https://www.instagram.com/p/" + pageCode
        pageUrls.append(pageUrl)

    # step 2
    for pageUrl in pageUrls:
        page = getPageSource(pageUrl).replace("b\'", "").replace("\'", "")
        page = page.split("<meta")
        for line in page:
            if line.startswith(" property=\"og:video\" content=\""):
                line = line.split("=")
                fileUrl = line[2].replace("\"", "").split(" ")[0]
                print(fileUrl)
                fileUrls.append(fileUrl)

    print("*** Found " + str(len(fileUrls)) + " files to download. ***")

    # step 3
    for fileUrl in fileUrls:
        saveFileData(fileUrl, destination=makeCwdDir("downloads"))

#getVideos("https://www.instagram.com/explore/tags/dumbabstraction/")
#getVideos(cwdFile("src.html"))
getVideos("https://www.instagram.com/explore/tags/dumbabstraction/")
