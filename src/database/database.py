import json
import redis

def get_redis():
    return redis.Redis(

    host= 'fly-still-rain-6277.upstash.io',

    port= 6379,

    password= 'dd26a8084bfe41008070e27fb584bbc9',

    decode_responses=True

    )


def store_data(func):
    r = get_redis()
    def inner_func(*args, **kwargs):
        output = func(*args, **kwargs)
        for (key, value) in json.loads(output).items():
            res = ''.join([str(ele) + "~" for ele in value])
            r.set(key, res)
        return output

    return inner_func