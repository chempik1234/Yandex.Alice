from flask import Flask, request
import logging
import json
# мы передаём __name__, внутри лога это 'logging
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

# Создадим словарь, чтобы для каждой сессии общения
# с навыком хранились подсказки, которые видел пользователь.
# Это поможет нам немного разнообразить подсказки ответов
# (buttons в JSON ответа).
# Когда новый пользователь напишет нашему навыку,
# то мы сохраним в этот словарь запись формата
# sessionStorage[user_id] = {'suggests': ["Не хочу.", "Не буду.", "Отстань!" ]}
# Такая запись говорит, что мы показали пользователю эти три подсказки.
# Когда он откажется купить слона,
# то мы уберем одну подсказку.
sessionStorage = {}
flag, start = False, True


@app.route('/post', methods=['POST'])  # POST для использования json внутри handle_dialog
def main():
    logging.info(f'Request: {request.json!r}')

    # Начинаем формировать ответ, согласно документации
    # мы собираем словарь, который потом при помощи
    # библиотеки json преобразуем в JSON и отдадим Алисе
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    # Преобразовываем в JSON и возвращаем
    return json.dumps(response)


def handle_dialog(req, res):
    global flag, start
    if flag:
        animal = 'кролика'
    else:
        animal = 'слона'
    user_id = req['session']['user_id']

    if req['session']['new'] or start:  # если только зашел то начало игры
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        start = False
        res['response']['text'] = f'Привет! Купи {animal}!'
        res['response']['buttons'] = get_suggests(user_id, animal[: -1])
        return
    # Если он написал 'ладно', 'куплю', 'покупаю', 'хорошо',
    # то мы считаем, что пользователь согласился.
    okreq = ['ладно', 'куплю', 'покупаю', 'хорошо', 'япокупаю', 'якуплю']
    if req['request']['original_utterance'].lower().strip().replace(' ', '') in okreq:
        res['response']['text'] = f'{animal[0].upper() + animal[1:]} можно найти на Яндекс.Маркете!'
        start = True
        if not flag:
            flag = True
        else:
            flag = False
            res['response']['end_session'] = True
        return
    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {animal}!"
    res['response']['buttons'] = get_suggests(user_id, animal[: -1])


def get_suggests(user_id, animal):  # обычно даёт 2 подсказки из списка,
    session = sessionStorage[user_id]  # а когда они кончаются, яндекс маркет

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session
    # в конце подсказок яндекс маркет
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": f"https://market.yandex.ru/search?text={animal}",
            "hide": True
        })
    return suggests


if __name__ == '__main__':
    app.run()
