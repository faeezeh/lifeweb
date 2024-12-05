from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from django.http import HttpResponse, JsonResponse


def fetch_apps():
    
    url = "https://cafebazaar.ir/lists/ml-mental-health-exercises"

    response = requests.get(url)
    
    print("Response Status Code:", response.status_code)
    if response.status_code != 200:
        print("Failed to fetch the page.")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print(soup.prettify())  
    
    apps = []
    
    for app_card in soup.select(".carousel__inner-content"):  
        name_element = app_card.select_one(".SimpleAppItem__title.fs-14")
        
        if name_element:
            name = name_element.text.strip()
            print("App Name Found:", name)  
            apps.append({"name": name})
        else:
            print("App Name Not Found in this Card.")
    
    return apps

def generate_excel(request):

    url_apps = "https://cafebazaar.ir/lists/ml-mental-health-exercises"
    url_app_detail = "https://cafebazaar.ir/app/com.diaco.khodam"
    response = requests.get(url_apps)
    

    
    # with open("appDetail.html", "w", encoding="utf-8") as file:
    #     file.write(response.text)
    
    soup = BeautifulSoup(response.text,"html.parser")
    
    apps = []

    # for app in soup.select(".LayoutRoot__content.container padding"):  
    #     app_name = app.select_one(".SimpleAppItem__title.fs-14")
    #     apps.append(app_name)

#fetch name in main page
    # for app in soup.select(".SimpleAppItem__title.fs-14"):
    #     app_name = app.text.strip()
    #     apps.append({"name": app_name})   
    # 

    # elements = soup.select(".GroupedRow__body")
    # response_data = [element.text.strip() for element in elements]
    # return JsonResponse({"results": response_data})

    # apps = []
    # for app_card in soup.select(".Box__body.GroupedRow__body"):
    #     name_tag = app_card.select_one(".SimpleAppItem__title.fs-14")
    #     link_tag = app_card.select_one(".SimpleAppItem.SimpleAppItem--single")

    #     if name_tag and link_tag :
    #         name = name_tag.text.strip()
    #         link = "https://cafebazaar.ir" + link_tag
    #         apps.append({"name": name, "link": link})


    app_cards = soup.select(".SimpleAppItem.SimpleAppItem--single")
    
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
    apps_sheet.append(["Name", "Link"])  
    
    
    for app in apps:
        apps_sheet.append([app['name'], app['link']])
    
   
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="cafebazaar_data.xlsx"'
    workbook.save(response)
    return response

def template_view(request):
    return render(request, 'mentalHealth/export.html')
