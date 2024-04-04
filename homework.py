import json
from typing import Tuple
from typing import Optional

import bs4
import requests
from bs4 import BeautifulSoup
from fake_headers import Headers


""" Функции 1-2

1.get_headers() - выводит фэйковые заголовки, необходимые для 
успешного проведения GET-запросов.

2.get_response(url, timeout) - осуществляет GET-запросы и выводит 
результат работы класса BeautifulSoup. Вводные параметры: ссылка 
URL (url), тайм-аут подключения (timeout).

"""

def get_headers()->dict:
    return Headers(os='win', browser='chrome').generate()

def get_response(url:str, timeout:int=10)->bs4.BeautifulSoup:
    response = requests.get(url, headers=get_headers(), timeout=timeout)
    bs = BeautifulSoup(response.text, 'lxml')
    return bs


""" Функции 3-5

el_tag - объект Tag (bs4.element.Tag) является вводным параметром.

3.get_vacancy_link(el_tag) - выводит ссылки на вакансии (HH.ru).
4.get_vacancy_name(el_tag) - выводит названия вакансий.
5.solve_attr_error(el_tag) - нивелирует ошибку AttributeError.

"""

def get_vacancy_link(el_tag:bs4.element.Tag)->str:
    return el_tag.find('a', {'class': 'bloko-link'})['href']

def get_vacancy_name(el_tag:bs4.element.Tag)->str:
    class_name = 'serp-item__title-link'
    data_qa_name = 'serp-item__title'
    vacancy_name = el_tag.find('span', {'class': class_name, 
                                'data-qa': data_qa_name}).text
    return vacancy_name

def solve_attr_error(el_tag:bs4.element.Tag)->Optional[str]:
    try:
        return str(el_tag.text)
    except AttributeError:
        return None


""" Функция 6

6.solve_attr_error_check(bs_vacancy, class_name, data_qa_name) - выводит 
зарплату с учетом ошибки AttributeError (None или размер зарплаты). 

Вводные параметры: 
- результат работы класса BeautifulSoup относительно ссылки 
на конкретную вакансию (bs_vacancy);
- название атрибута class относительно тега (class_name);
- название атрибута data-qa относительно тега (data_qa_name).

"""

def solve_attr_error_check(bs_vacancy:bs4.BeautifulSoup,
                    class_name:str, data_qa_name:str)->Optional[str]:
    span_tag = bs_vacancy.find('span', {'class': class_name, 
                                        'data-qa': data_qa_name})
    salary = solve_attr_error(span_tag)
    return salary


""" Функции 7-11

bs_vacancy - результат работы класса BeautifulSoup относительно ссылки 
на конкретную вакансию (bs_vacancy). Вводной параметр функций 7-10.
el_tag - объект Tag (bs4.element.Tag) является вводным параметром функции 11.

7.get_salary(bs_vacancy) - выведение потенциальной зарплаты работадателя.
с учетом всех нюансов: 1) вид зарплаты; 2) наличие зарплаты.
8.get_company_name(bs_vacancy) - выведение названия компании или ИП.
9.get_city(bs_vacancy) - выведение названия города.
10.get_vacancy_text(bs_vacancy) - получение текста вакансии.

11.get_all_values(el_tag) - выведение значений, полученных из предыдущих 
функций (ссылка на вакансию, название вакансии, зарплата, название компании, 
город, описание вакансии).

"""

def get_salary(bs_vacancy:bs4.BeautifulSoup)->Optional[str]:
    class_name = 'bloko-header-section-2'
    data_qa_name_gross = 'vacancy-salary-compensation-type-gross'
    data_qa_name_net = 'vacancy-salary-compensation-type-net'
    salary_gross = solve_attr_error_check(bs_vacancy, class_name, 
                                            data_qa_name_gross)
    salary_net = solve_attr_error_check(bs_vacancy, class_name, 
                                            data_qa_name_net)
    if salary_gross is not None:
        return str(salary_gross).replace('\xa0', ' ')
    elif salary_net is not None:
        return str(salary_net).replace('\xa0', ' ')
    else:
        return None

def get_company_name(bs_vacancy:bs4.BeautifulSoup)->str:
    try:
        class_name = 'bloko-link'
        data_qa_name = 'vacancy-company-name'
        a_tag = bs_vacancy.find('a', {'class': class_name,
                                'data-qa': data_qa_name})
        company_name = str(a_tag.text).replace('\xa0', ' ')
    except AttributeError:
        print("AttributeError. Пробуем найти название компании еще раз")
        class_name = 'bloko-header-section-2'
        data_qa_name = 'bloko-header-2'
        a_tag = bs_vacancy.find('a', {'class': class_name,
                                    'data-qa': data_qa_name})
        company_name = str(a_tag.text).replace('\xa0', ' ')
    return company_name

def get_city(bs_vacancy:bs4.BeautifulSoup)->str:
    try:
        data_qa_name = 'vacancy-view-raw-address'
        city_find = bs_vacancy.find('span', {'data-qa': data_qa_name})
        city = str(city_find.text)
    except AttributeError:
        print("AttributeError. Пробуем найти город еще раз")
        data_qa_name = 'vacancy-view-location'
        city_find = bs_vacancy.find('p', {'data-qa': data_qa_name})
        city = str(city_find.text)
    if ',' in city:
        city = city[:city.index(',')]
    return city

def get_vacancy_text(bs_vacancy:bs4.BeautifulSoup)->str:
    class_name = 'vacancy-section'
    div_tag = bs_vacancy.find('div', {'class': class_name})
    text = str(div_tag.text)
    return text

def get_all_values(el_tag:bs4.element.Tag)-> Tuple[str, str, 
                                                Optional[str],
                                                str, str, str]:
    link = get_vacancy_link(el_tag)
    vacancy_name = get_vacancy_name(el_tag)
    bs_vacancy = get_response(link)
    salary = get_salary(bs_vacancy)
    company_name = get_company_name(bs_vacancy)
    city = get_city(bs_vacancy)
    text = get_vacancy_text(bs_vacancy)
    return (link, vacancy_name, salary, 
            company_name, city, text)


""" Функции 12-15

Вводные параметры функций 12-15:
idx - порядковый индекс цикла; 
link - ссылка на вакансию; 
vacancy_name - название вакансии; 
salary - зарплата; 
company_name - название компании;
city - город;
key_words - ключевые слова для поиска нужных вакансий по их основному тексту;
text - основной текст вакансии; 
data - словарь с данными относительно вакансии, имеющий следующую структуру:
{'Название вакансии': {'link': '<ссылка на вакансию>', 'salary': '<зарплата>',
                        'company': '<компания>', 'city': '<город>'}}

12.show_loop_description(idx, link, vacancy_name, salary, company_name, 
city) - вывод данных о текущей обрабатываемой вакансии HH.ru. 

13.check_key_word_in_text(key_words, text) - проверка наличия ключевых слов
из списка KEY_WORDS в тексте вакансии.

14.count_dict_keys_repeats(vacancy_name, data) - поиск повторяющихся ключей
в словаре. Необходимо для предотвращения проблемы повторяющихся вакансий.

15.check_vacancy_name_repeat(vacancy_name, data) - проверка наличия 
повторяющихся вакансий. Если вакансия повторяется, то выводится True. 
В обратном случае выводится False.

"""

def show_loop_description(idx:int, link:str, vacancy_name:str, 
                        salary:Optional[str], company_name:str, 
                        city:str):
    print(f'### Обрабатываем вакансию № {idx+1} ###')
    print(f'Ссылка: {link}', f'Вакансия: {vacancy_name}', 
        f'Зарплата: {salary}', f'Компания: {company_name}', 
        f'Город: {city}', sep = '\n')

def check_key_word_in_text(key_words:list, text:str)->bool:
    if sum([int(word.lower() in text.lower()) 
            for word in key_words]) >= 1:
        return True
    else:
        return False

def count_dict_keys_repeats(vacancy_name:str, data:dict)->int:
    return len([key for key in data if vacancy_name == key])

def check_vacancy_name_repeat(vacancy_name:str, data:dict)->bool:
    if vacancy_name in data:
        vacancy_repeat_count = count_dict_keys_repeats(vacancy_name, 
                                                        data)
        if vacancy_repeat_count > 1:
            return True
        else:
            return False
    else:
        return False


""" Функции 16-21

Вводные параметры функций 16-21: 
url - ссылка на конкретную вакансию;
key_words - ключевые слова для поиска нужных вакансий по их основному тексту;
data - словарь с данными относительно вакансии;
file_name - название json-файла, получаемого в результате записи данных;
search_text - поисковый текст HH.ru;
area_list - список, содержащий коды регионов и городов (1 - Москва, 2 - СПб);
currency_code - код валюты (RUR - руб., USD - долл., EUR - евро);
page_numb - номер страницы;
only_with_salary - параметр выведения только тех вакансий, которые имеют з/п;
result - обработанные данные словаря data, полученные после проверки 
соответствия валюты (т.е. после отработки функции currency_check).

16.get_vacancies_data(url, key_words) - выводит словарь с данными по вакансии.

17.write_json(data, file_name) - записывает словарь в json-файл.

18.build_url(search_text, area_list, currency_code, page_numb, 
only_with_salary) - строит ссылку в разрезе конкретной страницы с учетом зоны 
проживания, валюты и фактора наличия зарплаты.

19.currency_check(currency_code, data) - проверяет соответствие валюты.

20.print_result(result) - выводит полученный результат.

21.main(search_text, key_words, file_name, area_list, currency_code, 
page_numb, only_with_salary) - реализовывает все написанные выше функции.

"""

def get_vacancies_data(url:str, key_words:list)->dict:
    data = {}
    bs = get_response(url)
    span_tag = bs.find_all('span', {'class':'serp-item__title-link-wrapper'})
    for idx, el_tag in enumerate(span_tag):
        link, vacancy_name, salary, company_name,\
        city, text = get_all_values(el_tag)
        show_loop_description(idx, link, vacancy_name, 
                            salary, company_name, city)
        if check_key_word_in_text(key_words, text) == True:
            dict_values = {'link': link, 'salary': salary, 
                            'company': company_name, 'city': city}
            if check_vacancy_name_repeat(vacancy_name, data) == True:
                repeat_count = count_dict_keys_repeats(vacancy_name, data)
                data[f'{vacancy_name}_{repeat_count+1}'] = dict_values
            else:
                data[vacancy_name] = dict_values
    return data

def write_json(data:dict, file_name:str):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def build_url(search_text:str, area_list:list, currency_code:str,
            page_numb:int, only_with_salary:bool):
    text_part = f'text={search_text}'
    area_part = '&' + ''.join([f'area={n}&' for n in area_list])[:-1]
    currency_part = f'&currency_code={currency_code}'
    page_part = f'&page={page_numb}'
    if only_with_salary == True:
        salary_part = '&only_with_salary=true'
    else:
        salary_part = ''
    return 'https://spb.hh.ru/search/vacancy?' +\
            text_part + area_part + currency_part +\
            page_part + salary_part

def currency_check(currency_code:str, data:dict)->dict:
    currency_sign_dict = {'RUR':'₽', 'USD':'$', 'EUR':'€'}
    curr = currency_sign_dict.get(currency_code)
    if currency_code in currency_sign_dict:
        data_dict={}
        for key, val_dict in data.items():
            salary = val_dict.get('salary')
            if salary is not None and curr in salary:
                data_dict[key] = val_dict
    return data_dict

def print_result(result:dict):
    print('### РЕЗУЛЬТАТ ###', result, sep = '\n')

def main(search_text:str, key_words:list, file_name:str='json_data.json',
            area_list:list=[1,2], currency_code:str='RUR', 
            page_numb:int=0, only_with_salary:bool=False):
    while True:
        try:
            url = build_url(search_text, area_list, currency_code, 
                            page_numb, only_with_salary)
            data = get_vacancies_data(url, key_words)
            break
        except AttributeError:
            print('AttributeError. Повторный вызов функций')
    result = currency_check(currency_code, data)
    print_result(result)
    write_json(result, file_name)
    return result


""" Относительно нижепредставленных переменных

SEARCH_TEXT - поисковый текст HH.ru
KEY_WORDS - ключевые слова, относительно которых ведется поиск вакансий
CURRENCY_CODE - код валюты (RUR - руб., USD - долл., EUR - евро)
PAGE_NUMB - номер страницы HH.ru для поиска вакансий

"""

if __name__ == '__main__':
    SEARCH_TEXT = 'python'
    KEY_WORDS = ['Django', 'Flask']
    CURRENCY_CODE = 'RUR'
    PAGE_NUMB = 0
    main(SEARCH_TEXT, KEY_WORDS, 
        currency_code = CURRENCY_CODE,
        only_with_salary = True,
        page_numb = PAGE_NUMB)