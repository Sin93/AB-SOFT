from urllib.parse import urlparse
from random import choice
from multiprocessing import Pool
from bs4 import BeautifulSoup
from urllib3 import PoolManager
import urllib3.exceptions


"""
Хотел писать данные в MongoDB, на мой взгляд его иерархическая структура идеально подходит для
этого, но уже не осилил, надо либо расковырять каждую ссылку на составляющие, с сохранением
иерархического порядка, либо использовать какие-то более изящные решения, но этого пока не
смог сделать без кошмарных костылей. Хотел копать в сторону выполнения задания на Scrapy,
но там столько всего, что решил оставить это на потом.

Обходить сайт в глубину и ширину - так-же пока сложновато для меня, хватило только на то,
чтобы собрать ссылки с главной страницы, пройти по ним и собрать ссылки там, в несколько
процессов.
В качестве бонуса, чтоб не выглядеть совсем глупым, использовал прокси, чтоб не забанили на
сайте, если что.
"""

# Префиксы ссылок, которые будем игнорировать
EXCLUDE_PREFIX = ['#', 'tel:', 'javascript:', 'mailto:', 'skype:',
                  'callto:', 'file:', 'chrome:', 'sms:', 'data:',
                  'itms:', 'mid:', 'ftp:', 'maphttps:']
# Форматы, которые необходимо игнорировать
EXCLUDE_FORMAT = ['.jpeg', '.jpg', '.pdf', '.png']
# Для перехвата ошибки из-за большого количества перенаправлений
MAX_RETRY = 'MAX_RETRY'


class MyParser:
    def __init__(self, site):
        # адрес стартовой страницы
        self.site = site
        # разбор url стартовой страницы для получения домена
        self.url_site = urlparse(self.site)

        # если домен сайта не в ASCII кодировке
        if not self.url_site.netloc.isascii():
            # взять домен и перевести его в ASCII
            site_netloc = str(self.url_site.netloc.encode('idna'))[2:-1]
            # сформировать новую ссылку на домен с протоколом
            self.domain = f'{self.url_site.scheme}://{site_netloc}'
            # сформировать новую ссылку на сайт
            self.site = f'{self.url_site.scheme}://{site_netloc}{self.url_site.path}'
        else:
            # Если кодировка верная - просто сделать ссылку на домен с протоколом
            self.domain = f'{self.url_site.scheme}://{self.url_site.netloc}'

        # ссылки которые предстоит обойти
        self.pages_to_parse = {site}
        # ссылки которые уже обходили
        self.parsed_pages = set()
        # контейнер для найденных ссылок
        self.site_links = set()
        # парсинг ссылок со стартовой страницы
        self.get_all_links(self.site)
        # Запуск персинга сайта
        self.multi_parse()

        for num, link in enumerate(self.site_links):
            # Вывести все ссылки на печать
            # если ссылка была не в кодировке ASCII, то привести её к читаемому виду
            if 'xn--' in link:
                link_parse = urlparse(link)
                link_netloc = link_parse.netloc.encode('idna').decode('idna')
                link = f'{link_parse.scheme}://{link_netloc}{link_parse.path}'
            print(f'{num}. {link}')

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
        http = PoolManager(1)
        # берётся один случайный прокси
        proxy = self.get_proxy()

        # Если страницу с таким url уже парсили, то не повторяем
        if url in self.parsed_pages:
            return ''

        try:
            # запрашиваем страницу, получаем объект HTTPResponse
            resp = http.request('GET', url, proxy[0], proxy[1])
        # обработка ошибки при слишком большом количестве перенаправлений
        except urllib3.exceptions.MaxRetryError:
            print(f'Достигнут лимит перенаправлений со страницы: {url}')
            return MAX_RETRY

        page = resp.data.decode('utf-8', 'ignore')
        # приводим response в читаемый вид
        soup = BeautifulSoup(page, "html.parser")
        # Регистрируем, что эту страницу обошли
        self.parsed_pages.add(url)
        # Возвращаем html код страницы
        return soup

    def get_all_links(self, url):
        """
        Функция заказывает html-код у функции get_html собирает ссылки из него ссылки
        и пишет их в список, который затем возвращает.

        :param url: адрес страницы, на которой ищем
        :return: список найденных ссылок на странице
        """
        links_from_url = []
        # Забираем код страницы url
        soup = self.get_html(url)
        if soup == MAX_RETRY or soup == '':
            # Проверяем, что не было ошибки и строка не пустая,
            # если пустая, то в этой итерации возвращаем пустой список
            return []

        # ищем всё с тегом 'a' на странице
        find_links = soup.findAll('a')

        # перебираем все найденные блоки
        for link in find_links:
            # берём из блоков ссылки href
            link = link.get('href')
            # обрабатываем ссылку только если она не None
            if link:
                # отсеять откровенно лишние ссылки
                if all(not link.startswith(prefix) for prefix in EXCLUDE_PREFIX) and all(
                        form not in link for form in EXCLUDE_FORMAT):

                    if link in url or link in f'{url}/':
                        # если найденная ссылка ведёт на ту же страницу, то игнорировать её
                        continue

                    if 'http' in link and not link.startswith(self.domain):
                        # Если ссылка на другой сайт, то игнорировать её
                        continue

                    if self.domain in link:
                        # если ссылка абсолютная
                        if link not in self.pages_to_parse:
                            # добавить в массиве на парсинг, если данной ссылки там нет
                            self.pages_to_parse.add(link)
                            links_from_url.append(link)
                    else:
                        # если ссылка относительная
                        if '://' in link:
                            # Игнорировать ссылки в которых есть '://'
                            continue

                        if link.startswith('/') and link[:2] != '//':
                            # если в начале ссылки есть /, но не //, то преобразовать в url
                            link = f'{self.domain}{link}'

                            # добавить в массиве на парсинг
                            self.pages_to_parse.add(link)
                            links_from_url.append(link)

                        elif link[:2] != '//' and r'':
                            # или если начинается не с // (внешний сайт), то преобразовать в url
                            link = f'{self.domain}/{link}'

                            # добавить в массиве на парсинг
                            self.pages_to_parse.add(link)
                            links_from_url.append(link)
        return links_from_url

    def multi_parse(self):
        """
        Функция с помощью мультипроцессинга запускает обход всех ссылок с
        главной страницы и парсинг ссылок с них.

        :return:
        """
        temp_list = self.pages_to_parse.copy()
        with Pool(40) as pool:
            # запускаем 40 процессов
            for result in pool.map(self.get_all_links, temp_list):
                # функцией map обходим все ссылки с главной страницы
                if not result:
                    # Пустой список не обрабатывать
                    continue

                for link in result:
                    # добавить все ссылки в массив с найденными
                    self.site_links.add(link)


if __name__ == '__main__':
    # url стартовой страницы
    PARSE = MyParser('https://сайтыобразованию.рф')
