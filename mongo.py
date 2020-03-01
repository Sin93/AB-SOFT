# from pymongo import MongoClient
#
#
# def main():
#     with MongoClient() as client:
#         col = client.mydb('test2')
#         new_list = {'/root': {'root_url': 'https://avsw.ru',
#                               'about/': {'/contacts': 'https://avsw.ru/contacts',
#                                          '/vakansii': 'https://avsw.ru/vakansii'
#                                          },
#                               '/products': {'/octopus': 'https://avsw.ru/octopus',
#                                             '/athena': 'https://avsw.ru/products/athena'}
#                               }
#         }
#         insert_list = col.insert_one(new_list)
#         return
#
# if __name__ == '__main__':
#     main()

new_list = {'/root': {'root_url': 'https://avsw.ru',
                              'about/': {'/contacts': 'https://avsw.ru/contacts',
                                         '/vakansii': 'https://avsw.ru/vakansii'
                                         },
                              '/products': {'/octopus': 'https://avsw.ru/octopus',
                                            '/athena': 'https://avsw.ru/products/athena'}
                              }
            }

map_dict = {'root': {'root_url': 'https://avsw.ru'}
                }
str_map_dict = '''map_dict['root']'''
str_map_dict = str_map_dict + '[' + 'link' + ']'
eval(str_map_dict) = 'link'
print(map_dict)