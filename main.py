import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from datetime import datetime, timezone, timedelta
import time
import os

TOKEN = os.getenv("VK_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
API_VERSION = '5.199'
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)
flag = False
admin = None
past_time = 0
like_time = 45
sl = {}
tz_by_admin = {}

for event in longpoll.listen():
    if event.type != VkBotEventType.MESSAGE_NEW:
        continue
    msg = event.object.message
    text = msg['text'].lower()
    peer_id = msg['peer_id']
    user_id = msg['from_id']
    msg_time = msg['date']
    if peer_id not in sl:
        sl[peer_id] = {'admin': None, 'time': like_time, 'flag': False,
                       'past_time': msg_time, 'one': False}
    try:
        if text.startswith('!время'):
            try:
                a = int(text.split()[1])
                sl[peer_id]['time'] = a
                s = f"Вы успешно изменили время на защиту.\nТекущее число секунд на защиту — {sl[peer_id]['time']}"
                vk.messages.send(peer_id=peer_id,
                                 random_id=int(time.time() * 1000),
                                 message=s)
            except:
                vk.messages.send(peer_id=peer_id,
                                 random_id=int(time.time() * 1000),
                                 message='Вы ввели некорректное время')

        if text.startswith('!чп'):
            try:
                a = int(text.split()[1])
                tz_by_admin[user_id] = a + 3
                if a > 0:
                    s = f"Вы успешно изменили свой часовой пояс.\nТекущий часовой пояс — МСК+{a}"
                elif a < 0:
                    s = f"Вы успешно изменили свой часовой пояс.\nТекущий часовой пояс — МСК{a}"
                else:
                    s = f"Вы успешно изменили свой часовой пояс.\nТекущий часовой пояс — МСК"
                vk.messages.send(peer_id=peer_id,
                                 random_id=int(time.time() * 1000),
                                 message=s)
            except:
                vk.messages.send(peer_id=peer_id,
                                 random_id=int(time.time() * 1000),
                                 message='Вы ввели некорректный часовой пояс')

        if text == '!стоп' and user_id == sl[peer_id]['admin']:
            vk.messages.send(user_id=sl[peer_id]['admin'],
                             random_id=int(time.time() * 1000),
                             message='Подсчет времени завершен')
            sl[peer_id]['flag'] = False
            sl[peer_id]['admin'] = None
            sl[peer_id]['one'] = False

        if sl[peer_id]['flag']:
            total_time = msg_time - sl[peer_id]['past_time']
            sl[peer_id]['past_time'] = msg_time
            name = vk.users.get(user_ids=user_id, v=API_VERSION)[0]
            offset = tz_by_admin.get(sl[peer_id]['admin'], 3)
            utc_time = datetime.fromtimestamp(msg_time, tz=timezone.utc)
            normal_time = utc_time + timedelta(hours=offset)
            if total_time <= sl[peer_id].get('time', like_time):
                s = f"{name['first_name']} {name['last_name']}\nВремя отправки: {normal_time.strftime('%H:%M:%S')}\n✔ Время, затраченное на защиту: {total_time}"
            else:
                s = f"{name['first_name']} {name['last_name']}\nВремя отправки: {normal_time.strftime('%H:%M:%S')}\n❌ Время, затраченное на защиту: {total_time}"
            vk.messages.send(user_id=sl[peer_id]['admin'],
                             random_id=int(time.time() * 1000), message=s)

        if text == '!старт':
            sl[peer_id]['flag'] = True
            sl[peer_id]['admin'] = user_id
            sl[peer_id]['past_time'] = msg_time
            try:
                vk.messages.send(user_id=sl[peer_id]['admin'],
                                 random_id=int(time.time() * 1000),
                                 message='Подсчет времени начат')
            except:
                vk.messages.send(peer_id=peer_id,
                                 random_id=int(time.time() * 1000),
                                 message='Бот не может вам писать')

        if sl[peer_id]['one']:
            if sl[peer_id]['past_time'] is None:
                sl[peer_id]['past_time'] = msg_time
                offset = tz_by_admin.get(sl[peer_id]['admin'], 3)
                utc_time = datetime.fromtimestamp(msg_time, tz=timezone.utc)
                normal_time = utc_time + timedelta(hours=offset)
                s = f"Время отправки атаки: {normal_time.strftime('%H:%M:%S')}"
            else:
                total_time = msg_time - sl[peer_id]['past_time']
                name = vk.users.get(user_ids=user_id, v=API_VERSION)[0]
                offset = tz_by_admin.get(sl[peer_id]['admin'], 3)
                utc_time = datetime.fromtimestamp(msg_time, tz=timezone.utc)
                normal_time = utc_time + timedelta(hours=offset)
                if total_time <= sl[peer_id].get('time', like_time):
                    s = f"{name['first_name']} {name['last_name']}\nВремя отправки: {normal_time.strftime('%H:%M:%S')}\n✔ Время, затраченное на защиту: {total_time}"
                else:
                    s = f"{name['first_name']} {name['last_name']}\nВремя отправки: {normal_time.strftime('%H:%M:%S')}\n❌ Время, затраченное на защиту: {total_time}"
            vk.messages.send(user_id=sl[peer_id]['admin'],
                             random_id=int(time.time() * 1000), message=s)

        if text == '!атака':
            sl[peer_id]['one'] = True
            sl[peer_id]['admin'] = user_id
            sl[peer_id]['past_time'] = None
            try:
                vk.messages.send(user_id=sl[peer_id]['admin'],
                                 random_id=int(time.time() * 1000),
                                 message='Подсчет времени защит от вашей атаки начат')
            except:
                vk.messages.send(peer_id=peer_id,
                                 random_id=int(time.time() * 1000),
                                 message='Бот не может вам писать')

    except:
        pass
