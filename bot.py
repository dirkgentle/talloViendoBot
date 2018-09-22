import datetime
import getopt
import json
import random
import re
import sys
import traceback  # para logear los errores

import praw  # reddit
import pyowm  # informacion meteorologica

import login  # informacion personal para log in del bot


PATTERN = re.compile(
    r'(?<!\\)!talloviendo ?(?:en )?(\"?)([a-záéíóúñ ]+?\b)?\1',
    re.IGNORECASE
)  # Tests: https://regex101.com/r/dovCdU/4


def update_log(id, log_path):  # para los comentarios que ya respondi
    with open(log_path, 'a') as my_log:

        my_log.write(id + '\n')


def load_log(log_path):  # para los comentarios que ya respondi
    with open(log_path) as my_log:
        log = my_log.readlines()
        log = [x.strip('\n') for x in log]
        return log


def output_log(text, debug_mode=False):  # lo uso para ver el output del bot
    date_text = datetime.date.today().strftime('%Y_%m')
    output_log_path = './logs/' + date_text + '_output_log.txt'
    with open(output_log_path, 'a') as myLog:
        s = '[' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ']'
        s = s + text + '\n'
        myLog.write(s)
    if debug_mode:
        print(text)


def check_condition(c):  # llamaron al bot?
    # TODO tratar de meter esta primera normalizacion en la regex
    text = c.body.replace('”', '\"').replace('“', '\"')
    match = PATTERN.search(text)
    if match is None:
        return False
    elif not match.group(2) or len(match.group(2)) < 3:
        return 'Montevideo'
    else:
        return match.group(2)


def get_temperature(w):
    temp_dict = w.get_temperature(unit='celsius')
    output_log('Temperature: ' + str(temp_dict), debug_mode)
    return temp_dict['temp']


def get_reply_rain():
    replies = json.load(open('./replies/rain_replies.json'))
    return random.choice(replies)


def get_reply_drizzle():
    replies = json.load(open('./replies/drizzle_replies.json'))
    return random.choice(replies)


def get_reply_thunderstorm():
    replies = json.load(open('./replies/thunderstorm_replies.json'))
    return random.choice(replies)


def get_reply_no_rain(temp=22):
    replies = json.load(open('./replies/no_rain_replies.json'))
    replies_hot = json.load(open('./replies/no_rain_hot_replies.json'))
    if temp >= 26:
        replies = replies + replies_hot
    return random.choice(replies)


replies_dict = {
    'Rain': get_reply_rain,
    'Thunderstorm': get_reply_thunderstorm,
    'Drizzle': get_reply_drizzle,
    }


allowed_subreddits = ['Uruguay', 'ROU', 'pitcnt', 'test']


epilogue_text = (
    '\n\n*****'
    '\n\n *Solo funciono en Uruguay, manéjense.*'
    ' Owned by \/u/DirkGentle.'
    ' [Source.](https://github.com/dirkgentle/talloViendoBot)'
    )

hint_text = (
    ' ¿No es tu ubicación?'
    ' Recordá usar \"\" para lugares con más de una palabra')

not_found_text = (
    ' no está en la lista de ciudades uruguayas en OpenWeatherMap. '
    'Podés verificar el nombre de tu ciudad [acá.]'
    '(https://openweathermap.org/find)')


if __name__ == '__main__':

    comment_log_path = 'log.txt'
    multireddit = '+'.join(allowed_subreddits)
    debug_mode = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd', 'debug')
    except getopt.GetoptError:
        print('bot.py -d')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-d', '--debug'):
            debug_mode = True

    while True:
        try:
            output_log('Comenzando el script', debug_mode)
            log = load_log(comment_log_path)
            reddit = praw.Reddit(
                client_id=login.client_id,
                client_secret=login.client_secret,
                password=login.password,
                user_agent='tescript for /u/talloViendoBot',
                username=login.username
            )
            output_log(
                'Login to reddit as: ' + reddit.user.me().name,
                debug_mode)
            owm = pyowm.OWM(login.owm_key)

            for comment in reddit.subreddit(multireddit).stream.comments():
                location = check_condition(comment)
                if location and comment.id not in log:
                    output_log(comment.body, debug_mode)
                    output_log(location + ',UY')

                    try:
                        obs = owm.weather_at_place(location + ',UY')
                        w = obs.get_weather()
                        status = w.get_status()
                        output_log('Status: ' + status, debug_mode)
                        # TODO: reimplmement hot day answers
                        reply = replies_dict.get(status, get_reply_no_rain)()
                        reply += '\n\n *****'
                        reply += '\n\n*En: ' + location + '.*'
                    except pyowm.exceptions.not_found_error.NotFoundError:
                        output_log('Location not found', debug_mode)
                        reply = location + not_found_text

                    reply += hint_text
                    reply += epilogue_text
                    output_log('{' + reply + '}', debug_mode)

                    if not debug_mode:
                        comment.reply(reply)
                        log.append(comment.id)
                        update_log(comment.id, comment_log_path)

        except Exception as exception:
            output_log(str(exception))
            output_log(traceback.format_exc())
            if debug_mode:
                raise(exception)
