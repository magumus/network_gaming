import socket
import pickle

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "localhost"  # veya "127.0.0.1"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def getP(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(4096))  # 2048 yerine 4096 kullanıldı
        except:
            pass

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            full_data = b""
            while True:
                part = self.client.recv(4096)  # 2048 yerine 4096 kullanıldı
                full_data += part
                try:
                    return pickle.loads(full_data)
                except EOFError:
                    continue
        except socket.error as e:
            print(e)
