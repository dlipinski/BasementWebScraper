import re
import datetime
import requests as r
from bs4 import BeautifulSoup

def get_time(delimiter=':'):
    dt = datetime.datetime.now()
    return f'{str(dt.hour).zfill(2)}{delimiter}{str(dt.minute).zfill(2)}{delimiter}{str(dt.second).zfill(2)}'

def get_date():
    dt = datetime.datetime.now()
    return f'{str(dt.year).zfill(2)}.{str(dt.month).zfill(2)}.{str(dt.day).zfill(2)}'

def get_soup(link):
    page = r.get(link)
    return BeautifulSoup(page.content, 'html.parser')

def get_max_page_num():
    soup = get_soup('https://www.otodom.pl/wynajem/?search%5Border%5D=created_at_first%3Adesc&page=1')
    return  int(soup.select('ul.pager li')[4].text)

def get_links(soup):
    links_containers = soup.select('header.offer-item-header a')
    return [l.get('href') for l in links_containers if l.get('href') != '#']

def get_time_created(soup):
    return soup(text=re.compile(r'Data dodania:'))[0]

def get_time_updated(soup):
    return soup(text=re.compile(r'Data aktualizacji:'))[0]

def get_location(soup):
    return soup.select_one('header a[href="#map"]').findAll(text=True)[2]

def get_owner(soup):
    return soup.select_one('section.section-breadcrumb').find_next_sibling('div').text

def get_price(soup):
    return soup.select_one('header small').parent.text

def get_details(soup):
    details_containers = soup.select('section.section-overview ul li')
    return ', '.join([d.text for d in details_containers])

def get_additional_info(soup):
    info_raw = soup.select('section.section-features ul li')
    return ', '.join([i.text for i in info_raw])

def get_base_data(link):
    soup = get_soup(link)
    return { 
        'created': get_time_created(soup),
        'updated': get_time_updated(soup),
        'location': get_location(soup),
        'owner': get_owner(soup),
        'price':  get_price(soup),
        'details': get_details(soup),
        'additional_info': get_additional_info(soup)
    }

def write_row(file, data):
    row = f'{get_date()};{";".join(data.values())}\n'
    file.write(row)

def scrap():
    base_counter = 0
    max_page_num = get_max_page_num()
    output = open('scraped.csv', 'w+')
    print(f'[{get_time()}] [STARTED]')
    for curr_page_num in range(1, max_page_num):
        soup = get_soup(f'https://www.otodom.pl/wynajem/?search%5Border%5D=created_at_first%3Adesc&page={curr_page_num}')
        for link in get_links(soup):
            try:
                data = get_base_data(link)
                write_row(output, data)
            except:
                 print(f'[{get_time()}] [ERROR] [{link}]')
            base_counter = base_counter + 1
            print(f'[{get_time()}] [PAGE {curr_page_num} OF {max_page_num}] [BASE {base_counter}]                                  ', end='\r')

if __name__ == "__main__":
    scrap()
