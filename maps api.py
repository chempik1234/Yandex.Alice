from flask import Flask, request
import logging
import json
from geo import get_geo_info, get_distance

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s %(levelname)s %(name)s %(message)s')
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Request: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        sessionStorage[user_id] = {
            'first_name': None
        }
        res['response']['text'] = 'Привет! Назови своё имя!'
        return

    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            first_name = first_name[0].upper() + first_name[1:]
            sessionStorage[user_id]['first_name'] = first_name
            res['response']['text'] = f'Привет, {first_name}! Я могу сказать в какой стране город' \
                                      'или сказать расстояние между городами!'
        return
    cities = get_cities(req)
    first_name = sessionStorage[user_id]['first_name']
    first_name = first_name[0].upper() + first_name[1:]
    if len(cities) == 0:
        res['response']['text'] = f'{first_name} ты не написал название не одного города!'
    elif len(cities) == 1:
        res['response']['text'] = f'{first_name}, этот город в стране - ' + get_geo_info(cities[0], 'country')
    elif len(cities) == 2:
        distance = get_distance(get_geo_info(cities[0], 'coordinates'), get_geo_info(cities[1], 'coordinates'))
        res['response']['text'] = f'{first_name}, расстояние между этими городами: ' + str(round(distance)) + ' км.'
    else:
        res['response']['text'] = f'{first_name}, слишком много городов!'


def get_cities(req):
    cities = []
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            if 'city' in entity['value'].keys():
                cities.append(entity['value']['city'])
    return cities


def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name', то возвращаем её значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()