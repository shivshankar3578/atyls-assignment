import redis
import json

class RedisPublisher:
    def __init__(self, redis_host="localhost", redis_port=6379):
        self.redis = redis.Redis(host=redis_host, port=redis_port)

    def publish_event(self, channel, message):
        self.redis.publish(channel, json.dumps(message))
        self.redis.set(message["hash"], json.dumps(message))