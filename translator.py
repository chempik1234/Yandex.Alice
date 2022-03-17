from flask import Flask, request
import logging
import json
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s %(levelname)s %(name)s %(message)s')


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
    word = req['request']['original_utterance']
    if not word:
        if req['session']['new']:
            res['response']['text'] = 'Скажите слово, и я переведу его на английский язык'
        else:
            res['response']['text'] = 'Вы не сказали слово'
        return
    word = word.split()[-1]
    url = "https://translated-mymemory---translation-memory.p.rapidapi.com/api/get"
    querystring = {"langpair": "ru|en", "q": word}
    headers = {
        'x-rapidapi-key': "24fd2ead8amshc203cd479b8fa8bp18d9b1jsnb8779c61c6a3",
        'x-rapidapi-host': "translated-mymemory---translation-memory.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    output = response.json()
    new = output['responseData']['translatedText']
    res['response']['text'] = new
    res['end_session'] = True


if __name__ == '__main__':
    app.run()