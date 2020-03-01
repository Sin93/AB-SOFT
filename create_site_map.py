import requests
import re
from random import choice
from pymongo import MongoClient

# Так-как в задании указано, что необходимо написать скрипт, который делает карту "любого" сайта,
# я расценивал задачу как "любого на мой выбор", а не "любого сайта впринципе", надеюсь это верно,
# так-как учесть все мелочи, для меня пока-что не представляется возможным.


# Итак, в первую очередь снимем html код страницы с помощью модуля requests и запишем в переменную,
# атрибут объекта класса Response - text

def get_proxi():
    useragents = open('useragents.txt').read().split('\n')
    proxies = open('proxies.txt').read().split('\n')
    use_proxi = {'http': 'http://' + choice(proxies)}
    use_useragents = {'User-Agent': choice(useragents)}
    proxi = [use_useragents, use_proxi]
    return proxi

def unique_link(getting_list):
    getting_list = set(getting_list)
    getting_list = list(getting_list)
    return getting_list

def get_links(url):
    proxi = get_proxi()
    links = []
    html = requests.get(url, headers=proxi[0], proxies=proxi[1]).text
    href_links = re.findall(r'a href="\S*"', html)
    temp_links = [itm[8:-1] for itm in href_links if itm[8] != '#' and itm[-2] != '/' and (itm[8] == '/' or itm[8] == 'h')]
    for itm in temp_links:
        if itm == 'http://www.avsw.ru' or itm == 'https://avsw.ru' or itm in check_links or itm[:14] in check_links:
            continue
        elif itm[:14] == 'http://avsw.ru':
            itm = itm[14:]
            check_links.append(itm)
            new_url = site + itm
            links.append(itm)
            get_links(new_url)
        else:
            check_links.append(itm)
            new_url = site + itm
            links = links + [itm]
            get_links(new_url)
    links = unique_link(links)
    global glob_links
    glob_links = glob_links + links
    glob_links = unique_link(glob_links)
    print('собираем относительныйе ссылки с ' + url)
    return

def set_key_in_dict():
    map_dict = {'root': {'root_url': 'https://avsw.ru'}
                }
    url = site
    for link in glob_links:
        link_list = link.split('/')
        for itm in link_list:
            url = url + '/' + itm
        url = site
    return map_dict

def to_db():
    site_dict = set_key_in_dict()
    with MongoClient() as client:
        conn = client.mydb.map_site
        insert_dict = conn.insert_one(site_dict)
    return

def main(url):
    get_links(url)
    print(glob_links)
    to_db()
    return print('Выполнено!')


if __name__ == '__main__':
    glob_links = []
    check_links = []
    site = 'https://avsw.ru'
    main(site)






