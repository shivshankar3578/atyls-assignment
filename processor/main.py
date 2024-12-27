import redis
import json

class RedisSubscriber:
    def __init__(self, redis_host="localhost", redis_port=6379):
        self.redis = redis.Redis(host=redis_host, port=redis_port)

    def subscribe_to_channel(self, channel):
        pubsub = self.redis.pubsub()
        pubsub.subscribe(channel)
        print(f"Subscribed to {channel}")
        for message in pubsub.listen():
            if message["type"] == "message":
                self.process_event(json.loads(message["data"]))

    def process_event(self, data):
        print(f"Processing event: {data}")
        # Add additional processing logic here, such as saving to another DB or triggering downstream services.

if __name__ == "__main__":
    subscriber = RedisSubscriber()
    subscriber.subscribe_to_channel("product_updates")