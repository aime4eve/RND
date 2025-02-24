import socket
import struct

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

def main():
    mcast_client = fetch_mcast_addr("get_mcast_client")
    if not mcast_client:
        print("获取组播地址失败")
        return
    mcast_ip, mcast_port = mcast_client.split(':')
    mcast_port = int(mcast_port)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', mcast_port))
    mreq = struct.pack("4sl", socket.inet_aton(mcast_ip), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    print(f"监听组播数据 ({mcast_ip}:{mcast_port})...")
    while True:
        data, _ = sock.recvfrom(1024)
        print(f"接收数据: {data.decode()}")

if __name__ == "__main__":
    main()