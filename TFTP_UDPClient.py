#!/usr/bin/python3
# Copyright: See AUTHORS and COPYING
"Usage: {0} -s <IPhost> -p <port> "

from sys import *
from socket import *
import struct
import os
import time
import math


def initialization_handler():
    if len(argv) != 5:
        print("That´s not the way to start it")
        exit(1)
    if argv[1].lower() != "-s":
        print('IP server is wrong')
        exit(1)
    if argv[3].lower() != "-p":
        print('Port is not available')
        exit(1)


def read(fileName):
    path = './' + fileName
    f = open(path, 'wb')
    while 1:
        try:
            response, peer=sock.recvfrom(518)
            time.sleep(0.011)
        except error:
            print('The server closed the conexion')
            main()
        else:
            op = struct.unpack('!H', response[0:2])[0]
            if op == 3:
                pack = struct.unpack('!H', response[2:4])[0]
                print('Receive packet : '+str(pack))
                size = len(response)
                msg = len(response) - 4
                data = struct.unpack('!' + str(msg) + 's', response[4:size])[0]
                f.write(data)
                ack_msg = struct.pack('!HH', 4, pack)
                sock.sendto(ack_msg, peer)
                if len(data)<512:
                    print('The message has arrived')
                    break
            elif op==5:
                msg = len(response) - 6
                data = struct.unpack('!' + str(msg) + 's', response[4:msg+4])[0]
                print(data.decode())
                os.remove(path)
                break
            else:
                print('That msg was not spected')
    f.close()

def controlACK(ack, path, peer):

    a = open(path, 'rb')
    puntero=ack * 512
    a.seek(puntero)
    data = a.read(512)
    data = struct.pack('!HH' + str(len(data)) + 's', 3, ack, data)
    sock.sendto(data,peer)
    a.close()

def write(fileName):
    msg = sock.recvfrom(518)[0]
    op = struct.unpack('!H', msg[0:2])[0]
    if op!=5:
        path = '/home/pillete/Desktop/Cliente/' + fileName
        sizeFile = os.path.getsize(path)
        if (sizeFile < 512):
            num_packs = 1
        else:
            num_packs = math.ceil(sizeFile / 512)
        f = open(path, 'rb')
        response = f.read(512)
        pack = 1
        data = struct.pack('!HH' + str(len(response)) + 's', 3, pack, response)
        while 1:
            try:
                print('ACK number: ' + str(pack) + ' for server')
                sock.sendto(data, server)
                msg = sock.recvfrom(518)[0]
                timeout(1)
            except error:
                main()
                continue
            else:
                op = struct.unpack('!H', msg[0:2])[0]
                if op == 4:
                    ack = struct.unpack('!H', msg[2:4])[0]
                    if ack == pack:
                        if num_packs == ack:
                            break
                        else:
                            pack += 1
                            data = f.read(512)
                            data = struct.pack('!HH' + str(len(data)) + 's', 3, pack, data)
                    else:
                        controlACK(ack, path, server)

        f.close()
    else:
        Error = struct.unpack('!' + str(len(msg[4:len(msg)])) + 's', msg[4:len(msg)])[0]
        print(Error.decode())


initialization_handler()
server = (argv[2], int(argv[4]))
sock = socket(AF_INET, SOCK_DGRAM)
sec = 10  # Timeout of four seconds
usec = 10000
timevalue = struct.pack('ll', sec, usec)
sock.setsockopt(SOL_SOCKET, SO_RCVTIMEO, timevalue)
mode = b'NETASCII'
def main():
    while 1:
        instruction = input('TFTP@UDP> ')
        op=instruction.split()
        if op[0].lower()=='quit':
            exit(0)
        if len(op) != 2 :
            print("Incorrect format")
        else:
            FileName = op[1]
            path = './' + FileName
            if op[0].lower() == 'read':
                if not os.path.isfile(path):
                    msg = struct.pack('!H' + str(len(FileName)) + 'sh' + str(len(mode)) + 'sh', 1, FileName.encode(), 0, mode, 0)
                    sock.sendto(msg, server)
                    tw1 = time.time()
                    read(FileName)
                    tw2 = time.time()
                    print("Total time: "+str((tw2 - tw1) * 1000))
                else:
                     print("The file already exists.")
            elif op[0].lower() == 'write':
                if os.path.isfile(path):
                    msg = struct.pack('!H' + str(len(FileName)) + 'sh' + str(len(mode)) + 'sh', 2, FileName.encode(), 0, mode, 0)
                    sock.sendto(msg, server)
                    tr1 = time.time()
                    write(FileName)
                    tr2 = time.time()
                    print("Total time: " +str((tr2 - tr1) * 1000))
                else:
                    print("The file you want to send doesn´t exists.")
            else:
                print("Option not available.")
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted.')
        exit(0)
