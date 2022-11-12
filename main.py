import logging
import requests
import json
import urllib
from collections import Counter
from datetime import datetime
from tqdm import tqdm

URL_ya = 'https://cloud-api.yandex.net/v1/disk/resources'
URL_vk = f'https://api.vk.com/method'
token_vk = ""
list_file = []
list_photos = []

id = int(input('Введите id пользователя Вконтакте: '))
token_ya = input('Введите токен Яндекс: ')


class VkPhotos:
    def __init__(self, token_vk, id):
        self.token_vk = token_vk
        self.id = id

    def get_photos(self, V='5.131'):
        max_photo = ''
        size_photo = ''
        params = f'owner_id={id}&album_id=profile&rev=0&count=5&extended=1&'
        try:
            res = requests.get(f'{URL_vk}/photos.get?{params}access_token={token_vk}&v={V}').json()
            for photo in tqdm(res['response']['items']):
                for sizes in photo['sizes']:
                    if 'w' in sizes['type']:
                        max_photo = sizes['url']
                        size_photo = 'w'
                    elif 'z' in sizes['type']:
                        max_photo = sizes['url']
                        size_photo = 'z'
                dict = {'file name': f'{photo["likes"]["count"]}.jpg', 'size': size_photo}
                list_file.append(dict)
                list_photos.append([photo['likes']['count'], photo['date'], max_photo])
            with open('photos.json', 'w') as json_file:
                json.dump(list_file, json_file)
        except:
            print('Ошибка\n', res)


class YaUploader:
    def __init__(self, token):
        self.token = token

    def upload(self, loadfile, replace=False):
        likes = []
        likes_list = []
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
                   'Authorization': f'OAuth {token_ya}'}
        try:
            folder = requests.put(f'{URL_ya}?path={urllib.parse.quote("Фото id" + id)}', headers=headers).json
        except:
            print(folder)
        for i in loadfile:
            likes.append(i[0])
        counter = Counter(likes)
        for likes, count in counter.items():
            if count != 1:
                likes_list.append(likes)
        for photo in tqdm(loadfile):
            if photo[0] in likes_list:
                try:
                    date = datetime.utcfromtimestamp(photo[1])
                    date = str(date)
                    res = requests.post(
                        f'{URL_ya}/upload?url={urllib.parse.quote(photo[4])}&path={urllib.parse.quote("Фото id" + id)}/'
                        f'{photo[0]} {urllib.parse.quote(date[:10])}', headers=headers).json()
                except:
                    print(res)
            else:
                try:
                    res = requests.post(
                        f'{URL_ya}/upload?url={urllib.parse.quote(photo[2])}&path={urllib.parse.quote("Фото id" + id)}/'
                        f'{photo[0]}', headers=headers).json()
                except:
                    print(res)


if __name__ == '__main__':
    Photo = VkPhotos(id, token_vk)
    result = Photo.get_photos()
    uploader = YaUploader(token_ya)
    result = uploader.upload(list_photos)
