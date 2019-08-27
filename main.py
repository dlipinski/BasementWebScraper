import requests as r
from bs4 import BeautifulSoup
import re



def get_location(soup):
    location = soup.select_one('header a[href="#map"]').findAll(text=True)[2].split(', ')
    city = location[0] or ''
    district = location[1] or ''
    street = location[2] if len(location) == 3 else ''
    return { 'city': city, 'district': district, 'street': street }

def get_price(soup):
    whole_price = soup.select_one('header small').parent.text
    price = whole_price[:whole_price.find('zł')]
    return price

details_dict = {
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
        details[key] = ''
    return details

def main():
    page = r.get('https://www.otodom.pl/wynajem/mieszkanie/gdansk/')
    soup = BeautifulSoup(page.content, 'html.parser')
    links_containers = soup.select('header.offer-item-header a')
    links = [l.get('href') for l in links_containers if l.get('href') != '#']
    
    page = r.get(links[0])
    soup = BeautifulSoup(page.content, 'html.parser')

    location = get_location(soup)
    price = get_price(soup)
    details = get_details(soup)

    print('LOCATION: ', location)
    print('PRICE: ', price)
    print('DETAILS: ', details)

if __name__ == '__main__':
    main()

