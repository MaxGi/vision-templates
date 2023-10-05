from pythonosc.udp_client import SimpleUDPClient

class OscHandler:

    def __init__(self, ip="127.0.0.1", port=5005):
        self.client = SimpleUDPClient(ip, port)

    def data(self, id, x, y, rot, tm):
        msg = []
        msg.append(int(id))
        msg.append(float(x))
        msg.append(float(y))
        msg.append(int(rot))
        msg.append(float(tm))
        self.client.send_message("/marker/pos", msg)
    
    def remove(self, id):
        self.client.send_message("/marker/remove", int(id))
    
    def rotation(self, id, dir):
        msg = []
        msg.append(id)
        msg.append(dir)
        self.client.send_message("/marker/rotate", msg)

