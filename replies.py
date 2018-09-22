import json
import random


def get_reply_rain(temp=22):
    replies = json.load(open('./replies/rain_replies.json'))
    return random.choice(replies)


def get_reply_drizzle(temp=22):
    replies = json.load(open('./replies/drizzle_replies.json'))
    return random.choice(replies)


def get_reply_thunderstorm(temp=22):
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


def get_reply_from_status(status, temp=22):
    return replies_dict.get(status, get_reply_no_rain)(temp)
