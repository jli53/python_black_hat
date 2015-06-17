import socket
import paramiko
import threading
import sys
import logging

logging.basicConfig()

host_key = paramiko.RSAKey(filename = 'test_rsa.key')

class Server(paramiko.ServerInterface):
    def _init_(self):
        self.event = threading.Event()
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    def check_auth_password(self, username, password):
        if(username == 'ljm') and (password == 'ljm920819'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED
    
server = sys.argv[1]
ssh_port = int(sys.argv[2])

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((server,ssh_port))
    sock.listen(100)
    print '[+] Listening for connection ...'
    client,addr = sock.accept()
except Exception,e:
    print '[-] Listen Failed: '+str(e)
    sys.exit(1)
print '[+] Got a connection!'

try:
    ljmSession = paramiko.Transport(client)
    ljmSession.add_server_key(host_key)
    server = Server()
    try:
        ljmSession.start_server(server = server)
    except paramiko.SSHException, x:
        print '[-] SSH negotiation failed.'
    chan = ljmSession.accept(20)
    print '[+] Authenticated!'
    print chan.recv(1024)
    chan.send('Welcome to ljm_ssh')
    while True:
        try:
            command = raw_input("Enter command: ").strip('\n')
            if command != 'exit':
                chan.send(command)
                print chan.recv(1024)+'\n'
            else:
                chan.send('exit')
                print 'exiting'
                ljmSession.close()
                raise Exception('exit')
        except KeyboardInterrupt:
            ljmSession.close()
except Exception,e:
    print '[-] Caught exception: '+str(e)
    try:
        ljmSession.close()
    except:
        pass
    sys.exit(1)