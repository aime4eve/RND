import socket
import threading
import time
import datetime
import struct

# 全局变量
g_data = b''
data_lock = threading.Lock()
version = "1.0"

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def get_current_time():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def broadcast_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 9999))
    print("AirSight广播服务已启动 (端口:9999)")
    while True:
        data, addr = sock.recvfrom(1024)
        cmd = data.decode().strip()
        resp = ""
        if cmd == "get_server_ip":
            resp = get_local_ip()
        elif cmd == "get_mcast_server":
            resp = "224.10.11.12:8888"
        elif cmd == "get_mcast_client":
            resp = "224.10.11.22:7777"
        elif cmd == "get_time":
            resp = get_current_time()
        elif cmd == "get_version":
            resp = version
        else:
            resp = "未知命令"
        sock.sendto(resp.encode(), addr)

def multicast_receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 7777))
    mreq = struct.pack("4sl", socket.inet_aton("224.10.11.22"), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    print("AirSight组播接收服务已启动 (224.10.11.22:7777)")
    while True:
        data, _ = sock.recvfrom(1024)
        with data_lock:
            global g_data
            g_data += data

def multicast_sender():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    print("AirSight组播发送服务准备就绪 (224.10.11.12:8888)")
    while True:
        with data_lock:
            global g_data
            if g_data:
                sock.sendto(g_data, ("224.10.11.12", 8888))
                g_data = b''
        time.sleep(1)

if __name__ == "__main__":
    threading.Thread(target=broadcast_server, daemon=True).start()
    threading.Thread(target=multicast_receiver, daemon=True).start()
    threading.Thread(target=multicast_sender, daemon=True).start()
    while True:
        time.sleep(1)