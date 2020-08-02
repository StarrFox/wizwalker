import socket

FOOD_START = b"\x0d\xf0"

# Todo: move this to dll
class SocketListener:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
        # self.socket.bind(("192.168.43.101", 0))
        self.socket.bind(("255.255.255.255", 0))
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

        self.is_listening = False

    def listen(self):
        self.is_listening = True

        while self.is_listening:
            raw_data = self.socket.recvfrom(65565)[0]

            if FOOD_START in raw_data:
                start = raw_data.find(FOOD_START)
                yield raw_data[start:]
