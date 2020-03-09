# from pymongo import MongoClient
#
# # надо установить библиотеку pymongo (pip install pymongo)
# # из списка:
# # my_list = ['/root/about', '/root/about/contacts', '/root/about/vakansii', '/root/products', '/root/products/octopus',
# #            '/root/products/athena']
# # должна выходить следующая фигня (как выполнится смотри что получилось в MongoDB Compass):
#
# def main():
#     with MongoClient() as client:
#         col = client.mydb('test2')
#         new_list = {'/root': {'root_url': 'https://avsw.ru',
#                               'about/': {'/contacts': 'https://avsw.ru/contacts',
#                                          '/vakansii': 'https://avsw.ru/vakansii'
#                                          },
#                               '/products': {'/octopus': 'https://avsw.ru/products/octopus',
#                                             '/athena': 'https://avsw.ru/products/athena'}
#                               }
#         }
#         insert_list = col.insert_one(new_list)
#         return
#
# if __name__ == '__main__':
#     main()
#
# # дальше фигня всякая
#
# # new_list = {'/root': {'root_url': 'https://avsw.ru',
# #                               'about/': {'/contacts': 'https://avsw.ru/contacts',
# #                                          '/vakansii': 'https://avsw.ru/vakansii'
# #                                          },
# #                               '/products': {'/octopus': 'https://avsw.ru/octopus',
# #                                             '/athena': 'https://avsw.ru/products/athena'}
# #                               }
# #             }
# #
# # map_dict = {'root': {'root_url': 'https://avsw.ru'}
# #                 }
# # str_map_dict = '''map_dict['root']'''
# # str_map_dict = str_map_dict + '[' + 'link' + ']'
# # eval(str_map_dict) = 'link'
# # print(map_dict)

import requests
with open('new.txt', 'w') as ugvbhjdv:
    a = ugvbhjdv.write(requests.get('https://python-scripts.com').text)