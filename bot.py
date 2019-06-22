import getopt
import re
import sys
import time
import traceback  # para logear los errores

import praw  # reddit
import pyowm  # informacion meteorologica

import login  # informacion personal para log in del bot
import logger
import replies


PATTERN = re.compile(
    r'(?<!\\)!talloviendo ?(?:en )?(\"?)([a-záéíóúñ ]+?\b)?\1',
    re.IGNORECASE
)  # Tests: https://regex101.com/r/dovCdU/4


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
    logger.output_log('Temperature: {}'.format(temp_dict), debug_mode)
    return temp_dict['temp']


allowed_subreddits = ['Uruguay', 'ROU', 'pitcnt', 'test']


epilogue_text = (
    '\n\n*****'
    '\n\n*Solo funciono en Uruguay, manéjense.*'
    ' Owned by \/u/DirkGentle.'
    ' [Source.](https://github.com/dirkgentle/talloViendoBot)'
)

hint_text = (
    '\n\n¿No es tu ubicación?'
    ' Recordá usar \"\" para lugares con más de una palabra'
)

not_found_text = (
    '{} no está en la lista de ciudades uruguayas en OpenWeatherMap. '
    'Podés verificar el nombre de tu ciudad [acá.]'
    '(https://openweathermap.org/find)'
)


if __name__ == '__main__':

    comment_log_path = 'log.txt'
    multireddit = '+'.join(allowed_subreddits)
    debug_mode = False
    backoff_counter = 1

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
            logger.output_log('Comenzando el script', debug_mode)
            log = logger.load_log(comment_log_path)
            reddit = praw.Reddit(
                client_id=login.client_id,
                client_secret=login.client_secret,
                password=login.password,
                user_agent='tescript for /u/talloViendoBot',
                username=login.username
            )
            logger.output_log(
                'Login to reddit as: {}'.format(reddit.user.me().name),
                debug_mode)
            owm = pyowm.OWM(login.owm_key)

            for comment in reddit.subreddit(multireddit).stream.comments():
                location = check_condition(comment)
                if location and comment.id not in log:
                    location = location.title()
                    logger.output_log(comment.body, debug_mode)
                    logger.output_log('{},UY'.format(location))

                    try:
                        obs = owm.weather_at_place('{},UY'.format(location))
                        w = obs.get_weather()
                        status = w.get_status()
                        temp = get_temperature(w)
                        logger.output_log(
                            'Status: {}'.format(status), debug_mode
                        )
                        reply = '{}\n\n*****\n\n*En: {}.*'.format(
                            replies.get_reply_from_status(
                                status, location, temp
                            ),
                            location
                        )
                    except pyowm.exceptions.api_response_error.NotFoundError:
                        logger.output_log('Location not found', debug_mode)
                        reply = not_found_text.format(location)

                    reply = '{}{}{}'.format(
                        reply,
                        hint_text,
                        epilogue_text
                    )
                    logger.output_log('{{ {} }}'.format(reply), debug_mode)

                    if not debug_mode:
                        comment.reply(reply)
                        log.append(comment.id)
                        logger.update_log(comment.id, comment_log_path)

                if backoff_counter > 1:
                    backoff_counter /= 2

        except Exception as exception:
            logger.output_log(str(exception))
            logger.output_log(traceback.format_exc())
            if debug_mode:
                raise(exception)

            time.sleep(backoff_counter * 5)
            backoff_counter *= 2
