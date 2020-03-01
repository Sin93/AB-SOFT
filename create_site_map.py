import requests
import re
from random import choice

# Так-как в задании указано, что необходимо написать скрипт, который делает карту "любого" сайта,
# я расценивал задачу как "любого на мой выбор", а не "любого сайта впринципе", надеюсь это верно,
# так-как учесть все мелочи, для меня пока-что не представляется возможным

# Итак, в первую очередь снимем html код страницы с помощью модуля requests и запишем в переменную,
# атрибут объекта класса Response - text
 
def get_proxi():
    useragents = open('useragents.txt').read().split('\n')
    proxies = open('proxies.txt').read().split('\n')
    use_proxi = {'http': 'http://' + choice(proxies)}
    use_useragents = {'User-Agent': choice(useragents)}
    proxi = [use_proxi, use_useragents]
    return proxi

def unique_link(getting_list):
    getting_list = set(getting_list)
    getting_list = list(getting_list)
    return getting_list

def get_links(url):
    proxi = get_proxi()
    html = requests.get(url, headers=proxi[1], proxies=proxi[0]).text
    href_links = re.findall(r'a href="\S*"', html)
    temp_links = [itm[8:-1] for itm in href_links if itm[8] != '#' and itm[-2] != '/' and (itm[8] == '/' or itm[8] == 'h')]
    links = []
    for itm in temp_links:
        if itm == 'http://www.avsw.ru' or itm == 'https://avsw.ru':
            continue
        elif itm[:14] == 'http://avsw.ru':
            itm = itm[14:]
            links.append(itm)
        else:
            links.append(itm)
    links = unique_link(links)
    print('собираем urlы с ' + url)
    print(links)
    return links

def collect_all_links(url):
    all_links = [url]
    check_url = [url]
    print('первичный url ' + url + ' получен')
    getting_links = get_links(url)
    urls = [url + itm for itm in getting_links]
    for itm in urls:
        all_links = all_links + get_links(itm)
        check_url.append(itm)
    all_links = unique_link(all_links)
    return all_links


if __name__ == '__main__':
    site = 'https://avsw.ru'
    print(collect_all_links(site))






