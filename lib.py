import socket
#外部函数1，用于判断前端传入是IP还是域名
def is_valid_ip(address):
    try:
        socket.inet_aton(address)
        return True
    except socket.error:
        return False
#外部函数2
