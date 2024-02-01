import json
from tqdm.auto import tqdm
import requests
from bs4 import BeautifulSoup


def save_to_jsonl(file_path: str, data: list[dict]):
    """Save a given data to a specified ``file_path`` in JSONL format"""
    with open(file_path, 'w') as jsonl_file:
        for item in data:
            jsonl_file.write(json.dumps(item) + '\n')


def download_soups(urls: list):
    """
    Download soups from a given list of URLs
    """
    soups = []
    for url in tqdm(urls):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
        else:
            print(url)
        soups.append(soup)
    return soups


def get_doctor_details(doctor_soup: BeautifulSoup):
    """
    Get a profile from a given doctor soup.
    See https://www.siphhospital.com/th/medical-services/find-doctor as an example.
    Each doctor's information can be found in a gray box.
    """
    name = doctor_soup.find('div', class_='card-text-name-doctor').get_text(strip=True)
    image_src = doctor_soup.find('img', class_='circular--square')['src']
    url = doctor_soup.find('a', class_='card-btn-view-data-doctor')['href']
    try:
        tablecheck = doctor_soup.find('ul', class_='text-table-day').get_text()
        tablecheck = " ".join(tablecheck.strip().split())
    except:
        tablecheck = ""
    return {
        "name": name,
        "image_src": image_src,
        "url": url,
        "table_check": tablecheck,
    }


def get_profile_details(doctor_url: BeautifulSoup):
    """
    Get an additional details from a scraped doctor URL.
    This include qualification and expertise.
    """
    response = requests.get(doctor_url)
    details_soup = BeautifulSoup(response.text, 'html.parser')
    try:
        qualification = details_soup.find("div", class_="layout-column-one layout-column-editable").get_text(strip=True)
    except:
        qualification = ""
    try:
        expertise = details_soup.find("div", class_="doctor-qualification-content").get_text(strip=True)
    except:
        expertise = ""
    return qualification, expertise



if __name__ == "__main__":
    urls = ["https://www.siphhospital.com/th/medical-services/find-doctor"] + [
        f"https://www.siphhospital.com/th/medical-services/find-doctor?page={i}"
        for i in range(2, 70)
    ]
    soups = download_soups(urls)

    doctor_details = []
    for soup in tqdm(soups):
        # find profile information
        divs = soup.find_all("div", class_='box-bg-gray text-center')
        for div in divs:
            doctor_detail = get_doctor_details(div)
            qual, expertise = get_profile_details(doctor_detail["url"])
            doctor_detail["qualification"] = qual
            doctor_detail["expertise"] = expertise
            doctor_details.append(doctor_detail)

    save_to_jsonl("sip_doctor_profiles.json", doctor_details)
