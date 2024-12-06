import datetime
import requests
import time

from django.shortcuts import render
from django.http import HttpResponse

from bs4 import BeautifulSoup
from openpyxl import Workbook

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def generate_excel(request):

    url_apps = "https://cafebazaar.ir/lists/ml-mental-health-exercises"
    response = requests.get(url_apps)
    
    soup = BeautifulSoup(response.text,"html.parser")
    start_time = datetime.datetime.now()
    print(start_time)
    apps = []

    for app_card in soup.select(".SimpleAppItem.SimpleAppItem--single"):
        name_tag = app_card.select_one(".SimpleAppItem__title.fs-14")
        link_tag = app_card.get("href")

        if name_tag and link_tag :
            name = name_tag.text.strip()
            link = "https://cafebazaar.ir" + link_tag
            apps.append({"name": name, "link": link})

    workbook = Workbook()
    apps_sheet = workbook.active
    apps_sheet.title = "Apps"
    apps_sheet.append(["Name", "Description", "Installs", "Size", "Last Updated", "Image Links"])  
    
    
    for app in apps:
        app_name = app["name"]
        app_link = app["link"]
        app_details = fetch_app_details(app_link)

        apps_sheet.append([
        app_name,
                app_details.get("description", ""),
                app_details.get("installs", ""),
                app_details.get("size", ""),
                app_details.get("last_updated", ""),
                ", ".join(app_details.get("image_links", []))
        ])

    comments_sheet = workbook.create_sheet(title="Comments")
    comments_sheet.append(["User ID", "Customer Name", "Comment Content", "Rate", "Date"])   

    for app in apps:
        app_link = app["link"]
        app_comments = fetch_app_comments(app_link)

        for comment in app_comments:
            comments_sheet.append([
                comment.get("user_id", ""),
                comment.get("display_name", ""),
                comment.get("comment", ""),
                comment.get("rating", ""),
                comment.get("date", ""),
            ])
   
    end_time = datetime.datetime.now()
    execution_time = end_time - start_time
    print(f"time execution : {execution_time}")

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="cafebazaar_data.xlsx"'
    workbook.save(response)
    return response

def fetch_app_details(app_link):
    response = requests.get(app_link)
    soup = BeautifulSoup(response.text, "html.parser")    

    app_name = soup.select_one(".AppName.fs-16").text.strip()

    # description = app_card.select_one(".AppDescription__content.fs-14").text.strip()
    description_parts = soup.select(".AppDescription__content.fs-14")
    description = " ".join(part.text.strip() for part in description_parts)
    installs, size, last_updated = "null", "null", "null"

    info_cubes = soup.select(".InfoCube")
    for cube in info_cubes:
        title = cube.select_one(".InfoCube__title.fs-12").text.strip() if cube.select_one(".InfoCube__title.fs-12") else ""
        content = cube.select_one(".InfoCube__content.fs-14").text.strip() if cube.select_one(".InfoCube__content.fs-14") else ""
            
        if "نصب" in title:
            installs = content
        elif "حجم" in title:
            size = content
        elif "آخرین بروزرسانی" in title:
            last_updated = content

    image_tags = soup.select(".sg__cell picture img")
    image_links = [img.get("src") for img in image_tags if img.get("src")]

    return {
            "app_name": app_name,
            "description": description,
            "installs": installs,
            "size": size,
            "last_updated": last_updated,
            "image_links": image_links
        }

def fetch_app_comments(app_link):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  
    driver = webdriver.Chrome(options=options)
    driver.get(app_link)
    
    reviews = []
    while True:
        
        try:
            more_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".newbtn.AppCommentsList__loadmore"))
            )
            more_button.click()
            time.sleep(2)  
        except:
            break

    soup = BeautifulSoup(driver.page_source, "html.parser")
    review_elements = soup.select(".AppCommentsList.padding")  # انتخاب نظرات
    elements = soup.find_all("div", class_="AppComment AppCommentsList__item")
    for element in elements:
        user_id = element.get("id", "unkown")
        display_name = element.select_one(".AppComment__username").text.strip()
        comment = element.select_one(".AppComment__body.fs-14").text.strip()
        # rating = element.select_one(".rating__fill")
        
        rating = element.select_one(".rating__fill").get("style", "unkown").replace("width:", "").replace(";", "").strip()
        # date = element.find_all("div")[-1].get("style", "unkown").replace("width:", "").replace(";", "").strip()
        date = element.find_all("div")[-2].text.strip()
        # date = element.find_next(".rating__fill").text.strip()
        
        reviews.append({
            "user_id": user_id,
            "display_name": display_name,
            "comment": comment,
            "rating": rating,
            "date": date,
        })

    driver.quit() 

    return reviews


def template_view(request):
    return render(request, 'mentalHealth/export.html')
