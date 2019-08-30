import re
from datetime import datetime, timedelta

def parse_time(time_created, time_dirty):
    if 'hour' in time_dirty:
        return time_created
    else:
        date = datetime.strptime(time_created, '%Y.%m.%d')
        amount = [int(s) for s in time_dirty if s.isdigit()]
        if 'day' in time_dirty:
            if not amount:
               date = date - timedelta(days=1)
            else:
                date = date - timedelta(days=amount[0])
        elif 'month' in time_dirty:
            if not amount:
               date = date - timedelta(days=30)
            else:
                date = date - timedelta(days=amount[0]*30)
        else:
            if not amount:
               date = date - timedelta(days=365)
            else:
                date = date - timedelta(days=amount[0]*365)
        return f'{str(date.year).zfill(2)}.{str(date.month).zfill(2)}.{str(date.day).zfill(2)}'

def parse_location(location_raw):
    location = location_raw.split(', ')
    if any(p in location[0] for p in ['ul.', 'al.', 'os.', 'pl.']):
        return { 'city': location[1] if len(location) == 2 else '', 'district': '', 'street': location[0] }
    else:
        return { 'city': location[0], 'district': location[1], 'street': location[2] if len(location) == 3 else '' }

def parse_owner(onwer_raw):
    if onwer_raw == 'Oferta prywatna':
        return '1'
    else:
        return '0'

def parse_price(price_raw):
    return price_raw[:price_raw.find('zł')]

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

def parse_details(details_raw):
    details_raw_a = [re.sub('(m²)|(zł)', '', d) for d in details_raw.split(',')]
    details = {}
    for key in details_dict:
        phrase = details_dict[key] + ':'
        detail_raw = [re.sub(phrase, '', d) for d in details_raw_a if phrase in d]
        details[key] = detail_raw[0].strip() if len(detail_raw) > 0 else ''
    return details

def parse_row(row):
    data_raw = row.replace('\n','').split(';')
    location = parse_location(data_raw[3])
    details = parse_details(data_raw[6])
    return {
        'created': parse_time(data_raw[0], data_raw[1]),
        'updated': parse_time(data_raw[0], data_raw[2]),
        'city': location["city"],
        'district': location["district"],
        'street': location["street"],
        'private': parse_owner(data_raw[4]),
        'price': parse_price(data_raw[5]),
        'deposit': details["deposit"],
        'rent': details["rent"],
        'rooms': details["rooms"],
        'floor': details["floor"],
        'surface': details["surface"],
        'year': details["year"],
        'heating': details["heating"],
        'windows': details["windows"],
        'state': details["state"],
        'building': details["building"],
        'material': details["material"],
        'additional_info': data_raw[7]
    }

def write_row(file, data):
    row = f'{";".join(data.values())}\n'
    file.write(row)

def parse():
    input = open('scraped_all_280819.csv', 'r')
    output = open('parsed.csv', 'w+')
    output.write('created;updated;city;district;street;private;price;deposit;rent;rooms;floor;surface;year;heating;windows;state;building;material;additional_info\n')
    for row in input:
        data = parse_row(row)
        write_row(output, data)

if __name__ == "__main__":
    parse()