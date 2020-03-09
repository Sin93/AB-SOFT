import requests
from random import choice
from pymongo import MongoClient
# import dpath.util
from urllib2 import urlopen
import io

# Так-как в задании указано, что необходимо написать скрипт, который делает карту "любого" сайта,
# я расценивал задачу как "любого на мой выбор", а не "любого сайта впринципе", надеюсь это верно,
# так-как учесть все мелочи, для меня пока-что не представляется возможным.


def get_proxi():
    useragents = open('useragents.txt').read().split('\n')
    proxies = open('proxies.txt').read().split('\n')
    use_proxi = {'http': 'http://' + choice(proxies)}
    use_useragents = {'User-Agent': choice(useragents)}
    proxi = [use_useragents, use_proxi]
    return proxi

def get_links(url):

    return

def set_key_in_dict():
    map_dict = {'python-scripts.com': {'root': 'https://python-scripts.com'}
                }
    url = site
    for link in all_links:
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
    print(all_links)
    return print('Выполнено!')


if __name__ == '__main__':
    all_links = []
    check_links = []
    site = 'https://python-scripts.com'
    main(site)














# elif itm[:14] == 'https://python-scripts.com':
#     itm = itm[14:]
#     check_links.append(itm)
#     new_url = site + itm
#     links.append(itm)
#     get_links(new_url)



def get_links(url):
    links = []
    proxi = get_proxi()
    print('собираем ссылки с ' + url)
    html = requests.get(url, headers=proxi[0], proxies=proxi[1]).text
    href_links = re.findall(r'a href="\S*"', html)
    temp_links = [itm[8:-1] for itm in href_links]
    print(temp_links)
    for itm in temp_links:
        if '#' in itm:
            itm = itm[:itm.find('#')]
        elif '.' in itm[(len(site)+1):] or itm[(len(site)+1):] is None:
            continue

        if itm == site or itm[(len(site)+1):] == [] or itm[(len(site)+1):] in check_links:
            continue
        elif itm[:len(site)] == site:
            itm = itm[(len(site)+1):]
            print(itm)
            check_links.append(itm)
            links = links.append(itm)
            all_links.append(itm)
            new_url = site + '/' + itm
            get_links(new_url)
    print(links)
    return