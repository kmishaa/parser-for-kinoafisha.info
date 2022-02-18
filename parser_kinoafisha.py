import requests
from bs4 import BeautifulSoup
import csv
import os
import subprocess

URL = 'https://www.kinoafisha.info/rating/movies/'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 YaBrowser/21.11.1.932 Yowser/2.5 Safari/537.36',
               'accept': '*/*'}
FILE = 'results_kinoafisha.csv'
NEW_PAGE = '?page='

def get_html(url):
    r = requests.get(url, headers = HEADERS)
    return r

def get_genres(soup):
    genres = ''
    all_genres = soup.find_all('a', class_='filmInfo_genreItem button-main')
    for genre in all_genres:
        genres += genre.get_text() + ', '
    return genres[:len(genres)-2]

def get_rating(soup):
    spans = soup.find('nav', class_='filmInfo_ratings navigation navigation-cells').find_all('span', class_='navigation_cell')
    return spans[1].get_text()

def get_movie_content(html):
    soup_movie = BeautifulSoup(html, 'html.parser')

    title = soup_movie.find('h1', class_='trailer_title').get_text()
    country = soup_movie.find('span', class_='trailer_year').get_text()
    mark = soup_movie.find('span', class_='rating_num')

    if mark:
        mark = float(mark.get_text())
    else:
        mark = 'Не указано'

    year = ''
    years = soup_movie.find_all('span', class_='filmInfo_infoData')
    if (len(years) > 1):
        year = int(years[1].get_text())
    else:
        year = 'Не указано'

    director = soup_movie.find('span', class_='badgeList_name')
    if director:
        director = director.get_text()
    else: 
        director = 'Не указано'
    
    movie = [{
        'title': title[:len(title) - 6],
        'director': director,
        'country': country[7:],
        'genre': get_genres(soup_movie),
        'year': year,
        'rating': int(get_rating(soup_movie)),
        'mark': mark
    }]
    return movie

def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    all_movies = soup.find_all('a', class_='movieItem_ref')
    movies = []
    counter = 1
    for movie in all_movies:
        if (counter % 10 == 0):
            print (f'Обработано {counter} фильмов из {len(all_movies)}')
        counter += 1
        link = movie.get('href')
        html_movie = get_html(link)
        movies.extend(get_movie_content(html_movie.text))
    return movies

def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Название', 'Режиссёр', 'Страна производства', 'Жанр', 'Год выхода', 'Место в рейтинге', 'Средняя оценка пользователей сайта'])
        for item in items:
            writer.writerow([item['title'], item['director'], item['country'], item['genre'], item['year'], item['rating'], item['mark']])

def parse():
    print ('Установка соединения...')
    movies = []
    html = get_html(URL)
    if (html.status_code == 200):
        for page in range(0, 10):
            print (f'Парсинг страницы {page + 1} из 10...')
            if (page != 0):
                html = get_html(URL + NEW_PAGE + f'{page}')

            movies.extend(get_content(html.text))     
        save_file(movies, FILE)
        print (f'Всего обработано {len(movies)} фильмов')
        
        os.startfile(FILE) #запуск созданного excel-файла для Windows

       #subprocess.call(['open', FILE]) #запуск созданного excel-файла для Mac os
    else:
        print ('Ошибка соединения(')

parse()
