from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from django.http import HttpResponse

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
    apps_data = fetch_apps()
    
    workbook = Workbook()
    apps_sheet = workbook.active
    apps_sheet.append(["Name"]) 

  
    for app in apps_data:
        apps_sheet.append([app["name"]])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="cafebazaar_data.xlsx"'
    workbook.save(response)
    return response

def template_view(request):
    return render(request, 'mentalHealth/export.html')
