import datetime


def update_log(id, log_path):  # para los comentarios que ya respondi
    with open(log_path, 'a') as my_log:
        my_log.write('{}\n'.format(id))


def load_log(log_path):  # para los comentarios que ya respondi
    with open(log_path) as my_log:
        log = my_log.readlines()
        log = [x.strip('\n') for x in log]
        return log


def output_log(text, debug_mode=False):  # lo uso para ver el output del bot
    date_text = datetime.date.today().strftime('%Y_%m')
    output_log_path = './logs/{}_output_log.txt'.format(date_text)
    with open(output_log_path, 'a') as myLog:
        s = '[{}] {}\n'.format(
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            text
        )
        myLog.write(s)
    if debug_mode:
        print(text)
