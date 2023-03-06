
#!/usr/bin/python3
# Copyright: See AUTHORS and COPYING
"Usage: {0} -s <IPhost> -p <port> "

from sys import argv, exit
from socket import *
import struct
import os
import time
import math


def initialization_handler():
    if len(argv) != 5:
        print("That´s not the way to strart it")
        exit(1)
    if argv[1].lower() != "-s":
        print('IP server is wrong')
        exit(1)
    if argv[3].lower() != "-p":
        print('Port is not available')
        exit(1)


def sendACK(response, sock):
    ack = struct.unpack('!H', response[2:4])[0]
    msgtosend = struct.pack('!2H', 4, ack)
    sock.send(msgtosend)

def read(FileName, mode):
    path = './' + FileName
    f = open(path, 'wb')
    while 1:
            response = sock.recv(518)
            op = struct.unpack('!H', response[0:2])[0]
            time.sleep(0.01)
            if op==5:
                msg = len(response) - 6
                data = struct.unpack('!' + str(msg) + 's', response[4:msg+4])[0]
                print(data.decode())
                os.remove(path)
                main()
            elif op == 3:
                size = len(response)
                msg = len(response) - 4
                data = struct.unpack('!' + str(msg) + 's', response[4:size])[0]
                f.write(data)
                sendACK(response, sock)
                if len(data) < 512:
                    print('The message has arrived')
                    break
            else:
                print('That msg was not spected')
    f.close()


def write(FileName, mode):
    path = './' + FileName
    f = open(path, 'rb')
    sizeFile = os.path.getsize(path)
    num_packs = math.ceil(sizeFile / 512)
    f = open(path, 'rb')
    response = f.read(512)
    data = struct.pack('!HH' + str(len(response)) + 's', 3, 1, response)
    print('Sending msg')
    while num_packs:
        try:
            sock.send(data)
            num_packs -= 1
            msg = sock.recv(518)
            op = struct.unpack('!H', msg[0:2])[0]
            if op==5:
                Error = struct.unpack('!' + str(len(msg[4:len(msg)])) + 's', msg[4:len(msg)])[0]
                print(Error.decode())
                break
        except error:
            print('The server closed the conexion')
            exit(1)
        else:
            if op == 4:
                data = f.read(512)
                pack = struct.unpack('!H', msg[2:4])[0] + 1
                data = struct.pack('!HH' + str(len(data)) + 's', 3, pack, data)
                if num_packs == 0:
                    break


    f.close()


initialization_handler()
sock = socket(AF_INET, SOCK_STREAM)
server = (argv[2], int(argv[4]))
sock.connect(server)
sec = 10  # Timeout of four seconds
usec = 10000
timevalue = struct.pack('ll', sec, usec)
sock.setsockopt(SOL_SOCKET, SO_RCVTIMEO, timevalue)
mode = b'NETASCII'
def main():
    while 1:
        instruction = input('TFTP@TCP> ')
        op=instruction.split()
        if op[0].lower() == 'quit':
            msg = struct.pack('!H' + str(len(op[0])) + 'sh' + str(len(mode)) + 'sh', 6, op[0].encode(), 0, mode, 0)
            sock.send(msg)
            sock.close()
            exit(0)
        if len(op) != 2:
            print("Incorrect format")
        else:
            if op[0].lower() == 'read':
                FileName = op[1]
                path='./' + FileName
                if not os.path.isfile(path):
                    msg = struct.pack('!H' + str(len(FileName)) + 'sh' + str(len(mode)) + 'sh', 1, FileName.encode(), 0, mode, 0)
                    sock.send(msg)
                    tw1 = time.time()
                    read(FileName, mode)
                    tw2 = time.time()
                    print("Total time: " + str((tw2 - tw1) * 1000))
                else:
                    print("The file already exists.")
            elif op[0].lower() == 'write':
                FileName = op[1]
                path = '/home/pillete/Desktop/Cliente/' + FileName
                if os.path.isfile(path):
                    FileName = op[1]
                    msg = struct.pack('!H' + str(len(FileName)) + 'sh' + str(len(mode)) + 'sh', 2, FileName.encode(), 0, mode, 0)
                    sock.send(msg)
                    tw1 = time.time()
                    write(FileName, mode)
                    tw2 = time.time()
                    print("Total time: " + str((tw2 - tw1) * 1000))
                else:
                    print("The file you want to send doesn´t exists.")
            else:
                print("Option not available.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        op=6
        print('Interrupted.')
        msg = struct.pack('!H' + str(len(op)) + 'sh' + str(len(mode)) + 'sh', 6, op.encode(), 0, mode, 0)
        sock.send(msg)
        sock.close()
        exit(0)
