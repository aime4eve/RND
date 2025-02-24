import socket

class DataStorage:
    def __init__(self):
        self.broadcast_addr = ("192.168.99.255", 9999)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.mcast_group = None

    def discover(self):
        commands = ["get_mcast_client", "get_server_ip"]
        for cmd in commands:
            self.sock.sendto(cmd.encode(), self.broadcast_addr)
            self.sock.settimeout(2)
            try:
                resp, _ = self.sock.recvfrom(1024)
                print(f"{cmd} => {resp.decode()}")
                if cmd == "get_mcast_client":
                    ip, port = resp.decode().split(":")
                    self.mcast_group = (ip, int(port))
            except socket.timeout:
                print(f"No response for {cmd}")

    def start_listening(self):
        if not self.mcast_group:
            print("先运行discover获取组播地址")
            return
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", self.mcast_group[1]))
        
        mreq = socket.inet_aton(self.mcast_group[0]) + socket.inet_aton("0.0.0.0")
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        print(f"Listening on {self.mcast_group}")

        while True:
            data, _ = sock.recvfrom(1024)
            print(f"Received: {data.decode()}")

if __name__ == "__main__":
    ds = DataStorage()
    ds.discover()
    ds.start_listening()
