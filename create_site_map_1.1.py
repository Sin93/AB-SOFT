from bs4 import BeautifulSoup
import urllib3 as u
from random import choice
from multiprocessing import Pool

# 1. main вызывает функцию multi_parse() в которую передаёт адрес сайта
# 2. Функция multi_parse() вызывает в свою очередь функцию get_links_from_main() и передаёт туда адрес сайта
# данная функция собирает все ссылки с главной страницы и возвращает список
# 3. Функция multi_parse() с помощью модуля multiprocessing запускает обработку полученного списка в 50 потоков и
# проходит по всем ссылкам из списка, вызывая функцию get_all_links()
# -- Функции get_links_from_main() и get_all_links() используют функцию get_html(), которая переходит по ссылке и собирает
# -- html код страницы, она в свою очередь использует - get_proxi() чтоб выбрать случайный сокет из файла
# -- и useragent, ну условно, чтоб сайт думал, что запрос идёт не из питона, а из браузера, это чтоб не забанили на
# -- сайте. Так-же используется функция
# 4. проблема возникает, когда надо идти дальше, т.е. рекурсивно переходить по ссылкам, мой список в котором находятся
# собранные ссылки, попадая в функцию, более не находится в глобальной области видимости, соответственно всё, что функция
# get_all_links() насобирает, так там и останется, кроме того, каждый последующий вызов вункции не знает о том, что насобирала
# предыдущая, и на этом моменте я застрял и пока-что отложил решение таким путём

def get_proxi():
    useragents = open('useragents.txt').read().split('\n')
    proxies = open('proxies.txt').read().split('\n')
    use_socket = {'http': 'http://' + choice(proxies)}
    use_useragents = {'User-Agent': choice(useragents)}
    proxi = [use_socket, use_useragents]
    return proxi

def get_html(url):
    http = u.PoolManager()
    proxi = get_proxi()
    if url in parsed_pages:
        return
    else:
        print('Парсим: ', url)
        resp = http.request('GET', url, proxi[0], proxi[1])
        a = resp.data.decode('utf-8')
        soup = BeautifulSoup(a, "html.parser")
        parsed_pages.append(url)
        return soup
        # TODO - сделать функцию, которая будет преобразовывать url в словарь

def get_links_from_main(url):
    pages_to_parse = [url]
    soup = get_html(url)
    find_links = soup.find_all('a')
    for link in find_links:
        link = link.get('href')
        print(link)
        try:
            if link[:21] == url:
                if link == url:
                    continue
                elif link not in pages_to_parse and link[:len(url)] == site and len(link) > len(url) + 1:
                    pages_to_parse.append(link)
                elif link not in pages_to_parse:
                    pages_to_parse.append(site + link)
            else:
                pages_to_parse.append(site + link)
        except:
            continue
    for itm in enumerate(pages_to_parse):
        print(itm) # Вот тут список pages_to_parse из 102 ссылок, местами кривых, но реальных
    return pages_to_parse # Возвращаем этот список в multi_parse() на строку 94

def get_all_links(url):
    global parsed_pages
    global page_to_parse
    parsed_pages = []
    parsed_pages.append(url)
    soup = get_html(url)
    find_links = soup.find('div', class_="b_page").find_all_next('a')
    for link in find_links:
        link = link.get('href')
        try:
            if link not in parsed_pages and link[:len(site)] == site:
                if link == site:
                    continue
                elif link[:len(site)] == site and len(link) > len(site) + 1:
                    page_to_parse.append(link)
                    print(link)
            else:
                page_to_parse.append(site + link)
                print(site + link)
        except:
            continue
    # for link in find_links:
    #     link = link.get('href')
    #     if link not in parsed_pages:
    #         page_to_parse.append(link)
    #         get_all_links(link)
    return page_to_parse

def multi_parse(url):
    pages_to_parse = get_links_from_main(url)
    print(page_to_parse)
    # Печатаем список и тут он снова из одного элемента, почему? мы же вернули из функции список из 102 элементов!
    with Pool(50) as p:
        p.map(get_all_links, pages_to_parse)
    with open('1.txt', 'a') as in_file:
        print(parsed_pages)
        for itm in parsed_pages:
            in_file.write(itm)
    return

def main():
    multi_parse(site)
    return

if __name__ == '__main__':
    site = 'https://asus-store.ru'
    page_to_parse = [site]
    parsed_pages = []
    site_links = []
    main()
