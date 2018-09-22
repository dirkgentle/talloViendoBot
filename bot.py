import getopt
import re
import sys
import traceback  # para logear los errores

import praw  # reddit
import pyowm  # informacion meteorologica

import login  # informacion personal para log in del bot
import logger
import reply


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
    logger.output_log('Temperature: ' + str(temp_dict), debug_mode)
    return temp_dict['temp']


allowed_subreddits = ['Uruguay', 'ROU', 'pitcnt', 'test']


epilogue_text = (
    '\n\n*****'
    '\n\n *Solo funciono en Uruguay, manéjense.*'
    ' Owned by \/u/DirkGentle.'
    ' [Source.](https://github.com/dirkgentle/talloViendoBot)'
    )

hint_text = (
    '\n\n¿No es tu ubicación?'
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
                'Login to reddit as: ' + reddit.user.me().name,
                debug_mode)
            owm = pyowm.OWM(login.owm_key)

            for comment in reddit.subreddit(multireddit).stream.comments():
                location = check_condition(comment)
                if location and comment.id not in log:
                    logger.output_log(comment.body, debug_mode)
                    logger.output_log(location + ',UY')

                    try:
                        obs = owm.weather_at_place(location + ',UY')
                        w = obs.get_weather()
                        status = w.get_status()
                        temp = get_temperature(w)
                        logger.output_log('Status: ' + status, debug_mode)
                        reply = reply.get_reply_from_status(status, temp)
                        reply += '\n\n *****'
                        reply += '\n\n*En: ' + location + '.*'
                    except pyowm.exceptions.not_found_error.NotFoundError:
                        logger.output_log('Location not found', debug_mode)
                        reply = location + not_found_text

                    reply += hint_text
                    reply += epilogue_text
                    logger.output_log('{' + reply + '}', debug_mode)

                    if not debug_mode:
                        comment.reply(reply)
                        log.append(comment.id)
                        logger.update_log(comment.id, comment_log_path)

        except Exception as exception:
            logger.output_log(str(exception))
            logger.output_log(traceback.format_exc())
            if debug_mode:
                raise(exception)
