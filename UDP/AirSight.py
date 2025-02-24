import socket
import threading
from datetime import datetime
import time

class AirSight:
    def __init__(self, net1_ip, net2_ip):
        self.g_data = []
        self.g_data_lock = threading.Lock()
        self.version = "1.0"
        
        # Broadcast servers
        self.broadcast_servers = [
            (net1_ip, 9999),
            (net2_ip, 9999)
        ]
        
        # Multicast settings
        self.mcast_send_group = ('224.10.11.12', 8888)
        self.mcast_recv_group = ('224.10.11.22', 7777)
        self.net1_ip = net1_ip
        self.net2_ip = net2_ip

    def start(self):
        # Start broadcast servers
        for ip, port in self.broadcast_servers:
            thread = threading.Thread(target=self.run_broadcast_server, args=(ip, port))
            thread.daemon = True
            thread.start()

        # Start multicast receiver (网1)
        threading.Thread(target=self.run_mcast_receiver, daemon=True).start()
        
        # Start multicast sender (网2)
        threading.Thread(target=self.run_mcast_sender, daemon=True).start()

        while True: time.sleep(1)

    def run_broadcast_server(self, bind_ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((bind_ip, port))
        print(f"Broadcast server running on {bind_ip}:{port}")
        
        while True:
            data, addr = sock.recvfrom(1024)
            cmd = data.decode().strip()
            response = self.handle_command(cmd, bind_ip)
            sock.sendto(response.encode(), addr)

    def handle_command(self, cmd, current_ip):
        if cmd == "get_server_ip": return current_ip
        elif cmd == "get_mcast_server": return f"{self.mcast_recv_group[0]}:{self.mcast_recv_group[1]}"
        elif cmd == "get_mcast_client": return f"{self.mcast_send_group[0]}:{self.mcast_send_group[1]}"
        elif cmd == "get_time": return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        elif cmd == "get_version": return self.version
        else: return "Invalid command"

    def run_mcast_receiver(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.net1_ip, self.mcast_recv_group[1]))
        
        mreq = socket.inet_aton(self.mcast_recv_group[0]) + socket.inet_aton(self.net1_ip)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        print(f"Multicast receiver started on {self.mcast_recv_group}")

        while True:
            data, _ = sock.recvfrom(1024)
            with self.g_data_lock:
                self.g_data.append(data)

    def run_mcast_sender(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, 
                       socket.inet_aton(self.net2_ip))
        print(f"Multicast sender ready for {self.mcast_send_group}")

        while True:
            time.sleep(0.1)
            with self.g_data_lock:
                if self.g_data:
                    data = b"".join(self.g_data)
                    self.g_data.clear()
                    sock.sendto(data, self.mcast_send_group)

if __name__ == "__main__":
    # 根据实际网络配置修改IP地址
    server = AirSight(net1_ip="192.168.43.100", 
                     net2_ip="192.168.99.100")
    server.start()
