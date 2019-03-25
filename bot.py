import json
import re
import os
import time
import random
import math
import datetime
import requests
import subprocess

from pyrogram import Client, api, Filters
from pyrogram.api import functions, types
from pyrogram.api.errors import FloodWait, InternalServerError
from pyrogram import Client, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

name_login = 'settings/login_feedback.json'
name_settings = 'settings/settings.json'


files = [
    name_login,
    name_settings
]

login_feedback = {}
settings = {}


try:
    for cur_file in files:
        # getting name of current file
        name = cur_file.split('/')[-1].split('.')[0]
        file = open(cur_file, 'r', encoding="utf8")

        locals()[name] = json.loads(file.read())

        print('%s data has been uploaded' % name)
        file.close()
    del file, name, files
except Exception as msg:
    print('Нарушена целостность структуры. Файл: '+name)
    print(msg)
    raise SystemExit(1)


def state_wrapper(rule, key):
    if rule and rule.get(key):
        return rule.get(key)

    return False


def main():
    print('[FEEDBACK] started')

    app = Client(
        login_feedback['token'],
        api_id=login_feedback["api_id"],
        api_hash=login_feedback["api_hash"]
    )


    @app.on_message(Filters.incoming & Filters.command(['ban', 'unban']) & Filters.reply & Filters.chat(settings['group']))
    def commands_handler(client, message):
        forfrom = int(message['reply_to_message']['forward_from']['id'])
        command = message['text'].lower()

        if command == '/ban':
            settings['banned'][str(forfrom)] = True
            res = 'за'
        elif command == '/unban':
            settings['banned'][str(forfrom)] = False
            res = 'раз'

        with open(name_settings, 'w') as file_:
            json.dump(settings, file_)
          
        file_.close()

        del file_

        app.send_message(forfrom, 'Ты был %sбанен'%res)


    @app.on_message(Filters.incoming & Filters.reply & Filters.chat(settings['group']))
    def answers(client, message):
        print(message)
        forfrom = int(message['reply_to_message']['forward_from']['id'])
        text = message['text']

        while True:
            try:
                app.send_message(forfrom, text)
                break
            except FloodWait as e:
                print('neeed wait a bit %i before inviting'%e.x)
                time.sleep(e.x)
            except Exception:
                pass
    

    @app.on_message(Filters.incoming)
    def message_handler(clien, message):
        # print(message)
        mid = message['message_id']
        user = message['chat']['id']
        
        if state_wrapper(settings['banned'], str(user)) or user < 0:
            return
        
        while True:
            try:
                app.forward_messages(settings['group'], user, mid)
                break
            except FloodWait as e:
                print('neeed wait a bit %i before inviting'%e.x)
                time.sleep(e.x)
            except Exception:
                pass

    app.run()


if __name__ == '__main__':
    main()
