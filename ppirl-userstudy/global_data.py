import config
import redis
import os
import data_loader as dl
import data_display as dd
import data_model as dm
import user_data as ud


if config.ENV == 'production':
    r = redis.from_url(os.environ.get("REDIS_URL"))
elif config.ENV == 'development':
    r = redis.Redis(host='localhost', port=6379, db=0)

