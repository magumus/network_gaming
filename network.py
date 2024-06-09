import socket
import pickle
import pika
import time

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "localhost"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.connect()
        self.rabbitmq_channel = self.setup_rabbitmq()

    def setup_rabbitmq(self):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            channel = connection.channel()
            channel.queue_declare(queue='game_queue')
            return channel
        except Exception as e:
            print(f"RabbitMQ setup error: {e}")
            return None

    def getP(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(4096))
        except Exception as e:
            print(f"Connection error: {e}")
            return None

    def reconnect(self):
        try:
            self.client.close()
        except:
            pass
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.p = self.connect()

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            full_data = b""
            while True:
                part = self.client.recv(4096)
                if not part:
                    break
                full_data += part
                try:
                    response = pickle.loads(full_data)
                    if self.rabbitmq_channel:
                        self.rabbitmq_channel.basic_publish(exchange='', routing_key='game_queue', body=pickle.dumps(response))
                    return response
                except EOFError:
                    continue
        except (socket.error, Exception) as e:
            print(f"Socket error: {e}")
            time.sleep(1)  # Kısa bir bekleme
            self.reconnect()
            return None
