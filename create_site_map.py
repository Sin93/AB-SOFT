from bs4 import BeautifulSoup
import urllib3 as u
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

class MyParser:
    def __init__(self, site):
        self.site = site
        self.pages_to_parse = {site}                # ссылки которые предстоит обойти
        self.parsed_pages = {''}                    # ссылки которые уже обходили
        self.site_links = {''}

        self.get_all_links(self.site)               # парсинг ссылок с главной страницы
        print('Добыли ссылки с главной страницы')
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
        http = u.PoolManager()
        proxy = self.get_proxy()                # берётся один случайный прокси
        if url in self.parsed_pages:            # Если страницу с таким url уже парсили, то не повторяем
            return
        else:
            resp = http.request('GET', url, proxy[0], proxy[1])     # запрашиваем страницу, получаем объект HTTPResponse
            page = resp.data.decode('utf-8')
            soup = BeautifulSoup(page, "html.parser")               # приводим response в читаемый вид
            self.parsed_pages.add(url)                              # Регистрируем, что эту страницу обошли
            return soup                                             # Возвращаем html код страницы

    def get_all_links(self, url):
        """
        Функция заказывает html-код у функции get_html собирает ссылки из него ссылки
        и пишет их в список, который затем возвращает.
        :param url: адрес страницы, на которой ищем
        :return: список найденных ссылок на странице
        """
        links_from_url = []
        soup = self.get_html(url)                                       # Забираем код страницы url
        try:
            find_links = soup.findAll('a')                              # ищем всё с тегом 'a'
        except:
            return  # иногда возникает исключение на главной странице не придумал ничего лучше, чтоб обойти его
        for link in find_links:                                         # перебираем все найденные блоки
            link = link.get('href')                                     # берём из них ссылки href
            try:
                if link[:len(url)] == url:                              # если ссылка абсолютная:
                    if link == url or link == f'{url}/':                # если найденная ссылка = url в котором искали
                        continue                                        # не добавлять такую ссылку
                    elif link not in self.pages_to_parse:               # если ссылки нет в списке на парсинг
                        self.pages_to_parse.add(link)                   # добавить ссылку в список на парсинг
                        links_from_url.append(link)
                        continue
                if link[0] == '/':                                      # если ссылка относительная и без / в начале
                    if f'{url}{link}' not in self.pages_to_parse:       # и её нет в списке на парсинг
                        self.pages_to_parse.add(f'{self.site}{link}')   # добавить её в список преобразовав к url
                        links_from_url.append(f'{self.site}{link}')
                        continue
                else:                                                   # если в начале есть /
                    if link[:4] == 'http' or link[:4] == 'tel:' \
                            or link[:4] == 'java':                      # исключим ссылки на другие сайты и прочий мусор
                        continue
                    if f'{url}/{link}' not in self.pages_to_parse:      # и такой ссылки нет в списке
                        self.pages_to_parse.add(f'{self.site}/{link}')  # то добавить в список преобразовав к url
                        links_from_url.append(f'{self.site}/{link}')
                        continue
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
    parse = MyParser('https://asus-store.ru')
