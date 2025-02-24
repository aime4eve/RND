import socket
import time
import datetime
import threading

def get_current_time():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def fetch_mcast_addr(cmd):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)
    try:
        sock.sendto(cmd.encode(), ('255.255.255.255', 9999))
        data, _ = sock.recvfrom(1024)
        return data.decode().strip()
    except socket.timeout:
        return None
    finally:
        sock.close()

def send_loop(mcast_ip, mcast_port):
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            current_time = get_current_time()
            sock.sendto(current_time.encode(), (mcast_ip, mcast_port))
            print(f"发送时间: {current_time}")
            sock.close()
        except Exception as e:
            print(f"发送失败: {e}")
        time.sleep(3)

def main():
    mcast_server = fetch_mcast_addr("get_mcast_server")
    if not mcast_server:
        print("获取组播地址失败")
        return
    mcast_ip, mcast_port = mcast_server.split(':')
    threading.Thread(target=send_loop, args=(mcast_ip, int(mcast_port)), daemon=True).start()
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
