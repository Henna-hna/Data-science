### Code to webscrape phytochemicals from IMPPAT database: ###

import requests
from bs4 import BeautifulSoup
import csv

def scrape_phytochemical_table(plant_names):
    phytochemical_data = []

    for plant_name in plant_names:
        url = f"https://cb.imsc.res.in/imppat/phytochemical/{plant_name}"
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            #this table is the first table on the page, therefore: 
            table = soup.find('table')
            if table:
                table_data = []
                rows = table.find_all('tr')
                for row in rows:
                    row_data = []
                    columns = row.find_all(['th', 'td'])
                    for column in columns:
                        row_data.append(column.get_text(strip=True))
                    table_data.append(row_data)
                phytochemical_data.extend(table_data)  # Extending the list with data for each plant:
            else:
                print(f"No table found for {plant_name}")
        else:
            print(f"Failed to fetch data for {plant_name}. Status code: {response.status_code}")

    return phytochemical_data

# creating unction to read plant names from CSV file:
def read_plant_names_from_csv(csv_file_path):
    plant_names = []
    with open(csv_file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            plant_names.extend(row)
    return plant_names

#Give the path to CSV file containing plant names
csv_file_path = '/content/worksheet - Phytochemicals.csv'  

# Read plant names from CSV
plant_names = read_plant_names_from_csv(csv_file_path)

# Scrape phytochemical table data
phytochemical_table_data = scrape_phytochemical_table(plant_names)

# Saving data to CSV
with open('phytochemical_table_data.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerows(phytochemical_table_data)

print("CSV file created successfully")