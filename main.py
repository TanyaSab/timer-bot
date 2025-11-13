import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from datetime import datetime
import time

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

for event in longpoll.listen():
    if event.type != VkBotEventType.MESSAGE_NEW:
        continue
    msg = event.object.message
    text = msg['text'].lower()
    peer_id = msg['peer_id']
    user_id = msg['from_id']
    msg_time = msg['date']
    if peer_id not in sl:
        sl[peer_id] = {'admin': None, 'time': like_time, 'flag': False, 'past_time': msg_time}
    try:
        if text.startswith('!время'):
            a = int(text.split()[1])
            sl[peer_id]['time'] = a
            s = f"Вы успешно изменили время на защиту.\nТекущее число секунд на защиту — {sl[peer_id]['time']}"
            vk.messages.send(peer_id=peer_id,
                             random_id=int(time.time() * 1000),
                             message=s)
        if text == '!стоп' and user_id == sl[peer_id]['admin']:
            vk.messages.send(user_id=sl[peer_id]['admin'],
                             random_id=int(time.time() * 1000),
                             message='Подсчет времени завершен')
            sl[peer_id]['flag'] = False
            sl[peer_id]['admin'] = None
        if sl[peer_id]['flag']:
            total_time = msg_time - sl[peer_id]['past_time']
            sl[peer_id]['past_time'] = msg_time
            name = vk.users.get(user_ids=user_id, v=API_VERSION)[0]
            normal_time = datetime.fromtimestamp(msg_time)
            if total_time <= sl[peer_id].get('time', like_time):
                s = f"{name['first_name']} {name['last_name']}\nВремя отправки: {normal_time.strftime('%H:%M:%S')}\n✔ Время, затраченное на защиту: {total_time}"
            else:
                s = f"{name['first_name']} {name['last_name']}\nВремя отправки: {normal_time.strftime('%H:%M:%S')}\n❌ Время, затраченное на защиту: {total_time}"
            try:
                vk.messages.send(user_id=sl[peer_id]['admin'],
                             random_id=int(time.time() * 1000), message=s)
            except:
                vk.messages.send(peer_id=peer_id,
                                 random_id=int(time.time() * 1000),
                                 message='Бот не может вам писать')
        if text == '!старт':
            sl[peer_id]['flag'] = True
            sl[peer_id]['admin'] = user_id
            sl[peer_id]['past_time'] = msg_time
            vk.messages.send(user_id=sl[peer_id]['admin'],
                             random_id=int(time.time() * 1000),
                             message='Подсчет времени начат')
    except:
        pass
