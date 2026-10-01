import json
import time
import asyncio
import aiohttp
import ssl
import certifi

import requests

from . import app


AUTH_HEADER = f'Bearer {app.config["DROPBOX_TOKEN"]}'

UPLOAD_LINK = 'https://content.dropboxapi.com/2/files/upload'
SHARING_LINK = (
    'https://api.dropboxapi.com/2/'
    'sharing/create_shared_link_with_settings'
)

async def async_upload_files_to_dropbox(images):
    if images is None:
        return []


def upload_files_to_dropbox(images):
    # Начинаем замер до обработки всех изображений.
    start_time = time.time()

    urls = []

    if images is not None:
        for image in images:
            dropbox_args = json.dumps({
                'autorename': True,
                'path': f'/{image.filename}',
            })

            print(f'Загрузка изображения {image.filename}')

            response = requests.post(
                UPLOAD_LINK,
                headers={
                    'Authorization': AUTH_HEADER,
                    'Content-Type': 'application/octet-stream',
                    'Dropbox-API-Arg': dropbox_args,
                },
                data=image.read(),
            )

            path = response.json()['path_lower']

            print(f'Получение ссылки для {image.filename}')

            response = requests.post(
                SHARING_LINK,
                headers={
                    'Authorization': AUTH_HEADER,
                    'Content-Type': 'application/json',
                },
                json={'path': path},
            )

            data = response.json()

            if 'url' not in data:
                data = data['error']['shared_link_already_exists']['metadata']

            url = data['url']
            url = url.replace('&dl=0', '&raw=1')
            urls.append(url)

    # Завершаем замер после обработки всех изображений.
    print('Итоговое время загрузки', time.time() - start_time)

    return urls


async def async_upload_files_to_dropbox(images):
    if images is None:
        return []

    start_time = time.time()

    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_context)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            upload_file_and_get_url(session, image)
            for image in images
            if image and image.filename
        ]
        urls = await asyncio.gather(*tasks)

    print('Итоговое время загрузки', time.time() - start_time)
    return urls


async def upload_file_and_get_url(session, image):
    dropbox_args = json.dumps({
        'autorename': True,
        'mode': 'add',
        'path': f'/{image.filename}',
    })   
    # Асинхронная загрузка в aiohttp выполняется 
    # с помощью асинхронного контекстного менеджера.
    async with session.post(
        UPLOAD_LINK,
        headers={
            'Authorization': AUTH_HEADER,
            'Content-Type': 'application/octet-stream',
            'Dropbox-API-Arg': dropbox_args
        },
        data=image.read()
    ) as response:
        # Асинхронное получение ответа должно сопровождаться 
        # ключевым словом await.
        data = await response.json()
        path = data['path_lower']
    async with session.post(
        SHARING_LINK,
        headers={
            'Authorization': AUTH_HEADER,
            'Content-Type': 'application/json',
        },
        json={'path': path}
    ) as response:
        data = await response.json()
        if 'url' not in data:
            data = data['error']['shared_link_already_exists']['metadata']
        url = data['url']
        url = url.replace('&dl=0', '&raw=1')
    return url
