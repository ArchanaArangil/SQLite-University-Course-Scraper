import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import sqlite3

driver = webdriver.Chrome()
conn = sqlite3.connect('colleges-and-courses.db')
cursor = conn.cursor()

def main():
    page = 0
    try:
        # Navigate to the initial page
        url = 'https://www.phdportal.com/rankings/1/world-university-rankings-times-higher-education.html'
        driver.get(url)

        while True:
            # Wait for the page to load and locate the data elements
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button')))

            # Get the page source after the dynamic content has loaded
            page_source = driver.page_source
            page += 1

            time.sleep(5)  
            seeCollege(page_source, page) 

            # Parse the page source with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')

            data_elements = soup.select('button')
            for item in data_elements:
                print(item.text)

            # Find the "Next" button
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, 'button.NextPage.TextNav')
                next_button.click()

                # Wait for the new page to load
                WebDriverWait(driver, 10).until(EC.staleness_of(next_button))
                time.sleep(2) 
            except:
                print("No more pages or unable to find the 'Next' button.")
                break
    finally:
        driver.quit()

def seeCollege(src, page): #Get links to the separate pages of the universities on 
    doc = BeautifulSoup(src, 'html.parser')
    s = doc.find('tbody', class_='ZebraStyle')
    rows = s.find_all(lambda tag: tag.name=='tr' and tag.get('data-id')==str(page))
    for row in rows:
        td = row.find('td')
        if td:
            a = td.find('a')
            if a:
                href = a.get('href')
                print(f"href: {href}")
                scrapeUniv(href)

def scrapeUniv(url): # Get a list of all for each university and add to the database
    try:
        courses = []
        content = fetchData(url)
        soup = BeautifulSoup(content, 'html.parser')
        title = soup.find('div', {'class': 'OrganisationTitle'}).text
        divs = soup.findAll('div', {'class': 'FoldContent Hidden'})

        for course in divs:
            a = course.findAll('a')
            for p in a:
                courses.append(p.get('title'))
        addToDatabase(title, courses)
    except:
        print("Exception occurred, skipping university")

def fetchData(url): # Open page for the given url
    tempDriver = webdriver.Chrome()
    tempDriver.get(url)
    return tempDriver.page_source

def addToDatabase(title, courses):
    if(len(courses) > 0):
        # Check if university has been added to the 'colleges' database yet
        cursor.execute('''
                SELECT id FROM colleges WHERE college_name = ?
                    ''',(title,))
        result = cursor.fetchone()
        
        # Add university if it doesn't already exist
        if result is None:
            cursor.execute('''
                    INSERT INTO colleges (college_name)
                    VALUES (?)
                    ''', (title,))
            conn.commit()

        # Get university ID
        cursor.execute('''
                SELECT id FROM colleges WHERE college_name = ?
                    ''', (title,))
        result = cursor.fetchone()
        college_id = int(result[0])

        # Add each course into the 'courses' database
        for course in courses:
            cursor.execute('''
                INSERT INTO courses (course_name, degree_type, college_id)
                VALUES (?, ?, ?)
                ''', (course, 'phd', college_id))
            conn.commit()


main()
conn.close()

