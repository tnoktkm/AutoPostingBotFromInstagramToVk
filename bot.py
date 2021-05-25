# -*- coding: utf-8 -*-
import io
from urllib.parse import urljoin
import requests
import unix_time
import os

import vk_api.vk_api
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.bot_longpoll import VkBotEventType

from instagrambot import InstagramBot
from config import username, password




class BotVk:
    def __init__(self, token_app, token_group, group_id, server_name="Empty"):

        self.server_name = server_name
        self.group_id = group_id

        self.vkGroup = vk_api.VkApi(token=token_group, api_version='5.126')
        self.vkApp = vk_api.VkApi(token=token_app)

        self.long_poll = VkBotLongPoll(self.vkGroup, group_id)

        self.app = self.vkApp.get_api()
        self.group = self.vkGroup.get_api()

    def start(self):
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                id_discuss = int(event.object.message.get('peer_id'))
                if self.app.groups.getById(group_id=self.group_id, fields="is_admin")[0]["is_admin"] == 1 and event.object.message.get('id') > 0:

                    text = event.object.message.get('text')
                    text = text.split()

                    if text[0] == "/инстазагрузка":
                        print(text)

                        my_bot = InstagramBot(username, password)
                        my_bot.login()

                        upload_url = self.app.photos.getWallUploadServer(group_id=self.group_id)
                        upload_url = upload_url['upload_url']

                        try:
                            count = self.app.wall.get(owner_id=-self.group_id, filter="postponed ")['count']
                            count -= 1
                            timestamp = self.app.wall.get(owner_id=-self.group_id, offset=count, count=1, filter="postponed ")['items'][0]['date']
                            print(f"Начинаем делать посты с {timestamp}")
                        except:
                            timestamp = unix_time.ts_now()
                            print(f"Начинаем делать посты с {timestamp}")

                        for user in text[1:]:
                            posts = my_bot.get_top_url_photo(user, 3)
                            print(posts)
                            n = 0
                            attachments = ""
                            text = f"https://www.instagram.com/{user}/\n [СТРАНА, ГОРОД] &#10084; \n - [НАДПИСЬ] \n\n#[СТРАНА]@inostranky"
                            try:
                                for post in posts:
                                    get_img = requests.get(post[0])
                                    with open(f"{user}/{user}_{n}_img.jpg", "wb") as img_file:
                                        img_file.write(get_img.content)
                                    n += 1

                                for i in range(0, 3):
                                    filename = f"{user}/{user}_{i}_img.jpg"
                                    r = requests.post(upload_url, files={'file': open(filename, 'rb')}).json()
                                    s = self.app.photos.saveWallPhoto(group_id=self.group_id, server=r['server'], photo=r['photo'], hash=r['hash'])
                                    attachments = f"photo{s[0]['owner_id']}_{s[0]['id']}" + "," + attachments

                                timestamp += 3600*3
                                self.app.wall.post(owner_id=-self.group_id, message=text, attachments=attachments, publish_date=timestamp)

                                os.remove(f"{user}")
                            except Exception as e:
                                print(f"Error: {e}")

                        my_bot.close_browser()
                        self.sendMsg("Парсинг закончен :)", id_discuss)

    def sendMsg(self, message, send_id):
        self.group.messages.send(peer_id=send_id, message=message, random_id=0)

    def sendMsgA(self, message, send_id, attachments):
        self.group.messages.send(peer_id=send_id, message=message, random_id=0, attachments=attachments)

    def get_instagram_photo(self, instagram_photo_link):
        url = urljoin(instagram_photo_link, 'media/?size=l')
        response = requests.get(url)
        if not response.ok:
            raise ValueError()
        file_like = ('photo.jpg', io.BytesIO(response.content))
        return file_like

    def getUserName(self, user_id):
        FIRST_FOUND = 0
        NEEDS_FIELDS = 'first_name'
        return self.group.users.get(user_id=user_id)[FIRST_FOUND][NEEDS_FIELDS]

    def getUserCity(self, user_id):
        NEED_RETURN = 'city'
        FIRST_FOUND = 0
        SET_CITY = 'city'
        NAME_CITY = 'title'
        return self.group.users.get(user_id=user_id, fields=NEED_RETURN)[FIRST_FOUND][SET_CITY][NAME_CITY]

    def getInstagramPhoto(self, instagram_photo_link):
        url = urljoin(instagram_photo_link, 'media/?size=l')
        response = requests.get(url)
        if not response.ok:
            raise ValueError()
        file_like = ('photo.jpg', io.BytesIO(response.content))
        return file_like

    def output(self, event):
        print("Username: " + self.getUserName(event.object.message.get('from_id')))
        print("From: " + self.getUserCity(event.object.message.get('from_id')))
        print("Text: " + event.object.message.get('text'))
        print("Type: ")

        if event.object.message.get('id') > 0:
            print("private message")
        else:
            print("group message")
        print(" --- ")



