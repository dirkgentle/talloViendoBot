import datetime


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
