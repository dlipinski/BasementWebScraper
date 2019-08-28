import re

def parse_time(time_created, time_dirty):
    return ''

def parse_location(location_raw):
    location = location_raw.split(', ')
    if any(p in location[0] for p in ['ul.', 'al.', 'os.', 'pl.']):
        return { 'city': location[1], 'district': 'district', 'street': location[0] }
    else:
        return { 'city': location[0], 'district': location[1], 'street': location[2] if len(location) == 3 else '' }

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
    details_raw_a = [re.sub('(m²)|(zł)', '', d) for d in details_raw.split(', ')]
    details = {}
    for key in details_dict:
        phrase = details_dict[key] + ':'
        detail_raw = [re.sub(phrase, '', d) for d in details_raw if phrase in d]
        details[key] = detail_raw[0].strip() if len(detail_raw) > 0 else ''
    return details

def parse_row(row):
    data_raw = row.split(';')
    location = parse_location(data_raw[3])
    details = parse_details(data_raw[5])
    return {
        'created': parse_time(data_raw[0], data_raw[1]),
        'updated': parse_time(data_raw[0], data_raw[2]),
        'city': location["city"],
        'district': location["district"],
        'street': location["street"],
        'price': parse_price(data_raw[4]),
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
        'additional_info': data_raw[6].replace('\n','')
    }

def write_row(file, data):
    row = f'{";".join(data.values())}\n'
    file.write(row)

def parse():
    input = open('scraped.csv', 'r')
    output = open('parsed.csv', 'w+')
    output.write('created;updated;city;district;street;price;deposit;rent;rooms;floor;surface;year;heating;windows;state;building;material;additional_info')
    for row in input:
        data = parse_row(row)
        write_row(output, data)

if __name__ == "__main__":
    parse()
