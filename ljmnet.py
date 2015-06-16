import sys
import subprocess
import getopt
import threading
import socket

listen = False
commadn = False
execute = ""
upload = False
target = ""
port = 0
upload_destination = ""

def usage():
    print "LJM Net Tool\n"
    print "Usage: ljmnet.py -t target_host -p port"
    print "-l --listen                      -listen on [host]:[port] for incoming connections"
    print "-e --execute=file_to_run         -execute the given file upon receving a connection"
    print "-c --command                     -initialize a command shell"
    print "-u --upload=destination          -upon receiving connection upload a file and write to [destination]"
    print "\nExample:\n"
    print "ljmnet.py -t 129.168.1.1 -p 5555 -l -e=\"cat /etc/passwd\""
    sys.exit(0)

def main():
    global listen
    global port
    global target
    global upload_destination
    global execute
    global command

    if not len(sys.argv[1:]):
        usage()

    try:
        opts,args = getopt.getopt(sys.argv[1:],"hle:cu:t:p:",["help","listen","execute","command","upload","target","port"])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o,a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-l","--listen"):
            listen = True
        elif o in ("-e","--execute"):
            execute = a
        elif o in ("-c","--command"):
            command = True
        elif o in ("-u","--upload"):
            upload_destination = a
        elif o in ("-t","--target"):
            target = a
        elif o in ("-p","--port"):
            port =a
        else:
            print "Unknown Option"

    if not listen and len(target) and port>0:
        buffer = sys.stdin.readline()
        client_sender(buffer)

    if listen:
        server_loop()

def client_sender(buffer):
    socket_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        print target
        print port
        socket_client.connect((target,port))
        if len(buffer):
            socket_client.send(buffer)
            while True:
                response = ""
                recv_len = 1
                while recv_len:
                    data = socket_client.recv(4096)
                    recv_len = len(data)
                    response += data
                    if(recv_len<4096):
                        break

                print response
                
                buffer = raw_input("input your data:\n")
                buffer += "\n"
                
                socket_client.send(buffer)
    except:
        print "[*] Exception when sending data and receving response."
        socket_client.close()

def server_loop():
    global target
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((target,port))

    server.listen(5)
    while True:
        client,addr = server.accept()

        client_thread = threading.Thread(target= client_handler, args = (client,))
        client_thread.start()
        
def run_command(command):
    command  = command.rstrip()

    try:
        output  = subprocess.check_output(command,stderr=subprocess.STDOUT,shell=True)
    except:
        output = "Failed to execute command.\r\n"

    return output
def client_handler(client):
    global execute
    global command
    global upload_destination

    if len(upload_destination):
        file_buff = ""
        while True:
            data = client.recv(1024)
            if not data:
                break
            file_buffer += data
        try:
            fp = open(upload_destination,"wb")
            fp.write(file_buff)
            fp.close()
            client.send("Finishing saving file as %s\r\n" % upload_destination)
        except:
            client.send("Failed to save file as %s\r\n" % upload_destination)
            
    if len(execute):
        output = run_command(execute)
        client.send(output)

    if command:
        while True:
            client.send("<LJM#>")
            cmd_buff = ""
            while "\n" not in cmd_buff:
                cmd_buff += client.recv(1024)

            response = run_command(cmd_buff)
            client.send(response)
main()
