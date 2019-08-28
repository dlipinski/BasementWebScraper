import requests as r
from bs4 import BeautifulSoup
import re

def get_soup(link):
    page = r.get(link)
    return BeautifulSoup(page.content, 'html.parser')

def get_location(soup):
    location = soup.select_one('header a[href="#map"]').findAll(text=True)[2].split(', ')
    city = location[0] or ''
    district = location[1] or ''
    street = location[2] if len(location) == 3 else ''
    if any(p in city for p in ['ul.', 'al.', 'os.']):
        city = location[1]
        district = ''
        street = location[0]
    return { 'city': city, 'district': district, 'street': street }

def get_price(soup):
    whole_price = soup.select_one('header small').parent.text
    price = whole_price[:whole_price.find('zł')]
    return price

details_dict = {
    'deposit': 'Kaucja',
    'rent': 'Czynsz - dodatkowo',
    'rooms': 'Liczba pokoi',
    'floor': 'Piętro',
    'surface': 'Powierzchnia',
    'year': 'Rok budowy',
    'heating': 'Ogrzewanie',
    'windows': 'Okna',
    'state': 'Stan wykończenia',
    'building': 'Rodzaj zabudowy',
    'material': 'Materiał budynku'
}

def get_details(soup):
    details_containers = soup.select('section.section-overview ul li')
    details_raw = [re.sub('(m²)|(zł)', '', d.text) for d in details_containers]
    details = {}
    for key in details_dict:
        phrase = details_dict[key] + ':'
        detail_raw = [re.sub(phrase, '', d) for d in details_raw if phrase in d]
        details[key] = detail_raw[0].strip() if len(detail_raw) > 0 else ''
    return details

def get_additional_info(soup):
    info_raw = soup.select('section.section-features ul li')
    info = ', '.join([i.text for i in info_raw])
    return info

def write_row(file, article_data):
    row = f'{article_data["location"]["city"]};{article_data["location"]["district"]};{article_data["location"]["street"]};{article_data["price"]};'
    for key in article_data["details"]:
        row = row + f'{article_data["details"][key]};'
    row = row + f'{article_data["additional_info"]}\n'
    file.write(row)

def process_article(link):
    soup = get_soup(link)
    location = get_location(soup)
    price = get_price(soup)
    details = get_details(soup)
    additional_info = get_additional_info(soup)
    return { 'location': location, 'price': price, 'details': details, 'additional_info': additional_info }

def main():
    base_counter = 0
    output = open('output.csv', 'w+')
    output.write('city;district;street;price;deposit;rent;rooms;floor;surface;year;heating;windows;state;building;material;additional_info\n')
    for page_num in range(1,879):
        soup = get_soup(f'https://www.otodom.pl/wynajem/mieszkanie/?search%5Border%5D=created_at_first%3Adesc&page={page_num}')
        links_containers = soup.select('header.offer-item-header a')
        links = [l.get('href') for l in links_containers if l.get('href') != '#']
        
        for link in links:
            article_data = process_article(link)
            write_row(output, article_data)
            base_counter = base_counter + 1
            print(f'    PAGE_{page_num} BASE_{base_counter} ({article_data["location"]["city"]})')

if __name__ == '__main__':
    main()
