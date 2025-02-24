import socket
import time
from datetime import datetime

class AirProbe:
    def __init__(self):
        self.broadcast_addr = ("192.168.43.255", 9999)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.target_mcast = None

    def discover(self):
        commands = ["get_mcast_server", "get_server_ip", "get_version"]
        for cmd in commands:
            self.sock.sendto(cmd.encode(), self.broadcast_addr)
            self.sock.settimeout(2)
            try:
                resp, _ = self.sock.recvfrom(1024)
                print(f"{cmd} => {resp.decode()}")
                if cmd == "get_mcast_server":
                    ip, port = resp.decode().split(":")
                    self.target_mcast = (ip, int(port))
            except socket.timeout:
                print(f"No response for {cmd}")

    def start_sending(self):
        if not self.target_mcast:
            print("先运行discover获取组播地址")
            return
        
        mcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            mcast_sock.sendto(current_time.encode(), self.target_mcast)
            print(f"Sent time to {self.target_mcast}")
            time.sleep(3)

if __name__ == "__main__":
    probe = AirProbe()
    probe.discover()
    probe.start_sending()
