from bs4 import BeautifulSoup
from urllib3 import PoolManager
from urllib.parse import urlparse
from random import choice
from multiprocessing import Pool
# from pymongo import MongoClient

"""
Хотел писать данные в MongoDB, на мой взгляд его иерархическая структура идеально подходит для этого,
но уже не осилил, надо либо расковырять каждую ссылку на составляющие, с сохранением иерархического порядка,
либо использовать какие-то более изящные решения, но этого пока не смог сделать без кошмарных костылей.
Хотел копать в сторону выполнения задания на Scrapy, но там столько всего, что решил оставить это на потом.

Обходить сайт в глубину и ширину - так-же пока сложновато для меня, хватило только на то, чтобы
собрать ссылки с главной страницы, пройти по ним и собрать ссылки там, в несколько процессов.
В качестве бонуса, чтоб не выглядеть совсем глупым, использовал прокси, чтоб не забанили на сайте, если что.
"""

# Префиксы ссылок, которые будем игнорировать
EXCLUDE_PREFIX = ['#', 'tel:', 'javascript:', 'mailto:', 'skype:', 'callto:']
# Форматы, которые необходимо игнорировать
EXCLUDE_FORMAT = ['.jpeg', '.jpg', '.pdf', '.png']

class MyParser:
    def __init__(self, site):
        self.site = site                            # адрес стартовой страницы
        self.url_site = urlparse(self.site)         # разбор url стартовой страницы для получения домена
        self.domain = f'{self.url_site.scheme}://{self.url_site.netloc}'    # домен сайта
        self.pages_to_parse = {site}                # ссылки которые предстоит обойти
        self.parsed_pages = set()                   # ссылки которые уже обходили
        self.site_links = set()

        self.get_all_links(self.site)               # парсинг ссылок со стартовой страницы
        self.multi_parse()                          # Запуск персинга сайта
        for link in enumerate(self.site_links):
            print(link)

    @staticmethod
    def get_proxy():
        """
        Функция берёт случайный сокет и юзерагент из файлов proxies.txt и
        user_agents.txt в корне проекта. Чтоб не забанили за парсинг.

        :return: Возвращает список из сокета и юзерагента
        """
        user_agents = open('user_agents.txt').read().split('\n')
        proxy = open('proxies.txt').read().split('\n')
        use_socket = {'http': 'http://' + choice(proxy)}
        use_user_agents = {'User-Agent': choice(user_agents)}
        proxy = [use_socket, use_user_agents]
        return proxy

    def get_html(self, url):
        """
        Функция принимает url страницы и собирает его html код, возвращая в get_all_links
        :param url:
        :return: html-код
        """
        http = PoolManager()
        proxy = self.get_proxy()                # берётся один случайный прокси
        if url in self.parsed_pages:            # Если страницу с таким url уже парсили, то не повторяем
            return
        else:
            resp = http.request('GET', url, proxy[0], proxy[1])     # запрашиваем страницу, получаем объект HTTPResponse
            try:
                page = resp.data.decode()
                soup = BeautifulSoup(page, "html.parser")           # приводим response в читаемый вид
                self.parsed_pages.add(url)                          # Регистрируем, что эту страницу обошли
                return soup                                         # Возвращаем html код страницы
            except UnicodeDecodeError:
                return ''

    def get_all_links(self, url):
        """
        Функция заказывает html-код у функции get_html собирает ссылки из него ссылки
        и пишет их в список, который затем возвращает.

        :param url: адрес страницы, на которой ищем
        :return: список найденных ссылок на странице
        """
        links_from_url = []
        soup = self.get_html(url)                           # Забираем код страницы url
        try:
            find_links = soup.findAll('a')                  # ищем всё с тегом 'a'
        except:
            return                          # иногда возникает исключение не придумал ничего лучше, чтоб обойти его
        for link in find_links:                             # перебираем все найденные блоки
            link = link.get('href')                         # берём из них ссылки href
            try:
                if all(not link.startswith(prefix) for prefix in EXCLUDE_PREFIX)\
                        and all(form not in link for form in EXCLUDE_FORMAT):       # отсеять откровенно лишние ссылки
                    if link == url or link == f'{url}/':    # если найденная ссылка ведёт на ту же страницу
                        continue                            # игнорировать её
                    if 'http' in link and not link.startswith(self.domain):     # Если ссылка на другой сайт
                        continue                                                # Игнорировать её

                    if self.domain in link:                             # если ссылка абсолютная
                        if link not in self.pages_to_parse:             # и её нет в массиве на парсинг
                            self.pages_to_parse.add(link)               # добавить в массиве на парсинг
                            links_from_url.append(link)
                    else:                                               # если ссылка относительная
                        if link.startswith('/') and link[:2] != '//':   # и в начале ссылки есть /, но не //
                            link = f'{self.domain}{link}'               # преобразовать в url
                            self.pages_to_parse.add(link)               # добавить в массиве на парсинг
                            links_from_url.append(link)
                        elif link[:2] != '//':                          # или если начинается не с // (внешний сайт)
                            link = f'{self.domain}/{link}'              # преобразовать в url
                            self.pages_to_parse.add(link)               # добавить в массиве на парсинг
                            links_from_url.append(link)
            except:
                continue
        return links_from_url

    def multi_parse(self):
        """
        Функция с помощью мультипроцессинга запускает обход всех ссылок с
        главной страницы и парсинг ссылок с них.

        :param url: ссылка на главную страницу
        :return:
        """
        temp_list = self.pages_to_parse.copy()
        with Pool(40) as p:                                         # запускаем 40 процессов
            for result in p.map(self.get_all_links, temp_list):     # функцией map обходим все ссылки с главной страницы
                try:
                    for link in result:
                        self.site_links.add(link)                   # добавляем все ссылки в массив с найденными
                except TypeError:                                   # иногда на странице ничего не находит
                    continue
        return


if __name__ == '__main__':
    parse = MyParser('https://yandex.ru')                           # url стартовой страницы
