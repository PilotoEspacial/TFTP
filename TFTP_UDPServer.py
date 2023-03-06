#!/usr/bin/python3
# Copyright: See AUTHORS and COPYING
"Usage: {0} -p <port> "
from sys import *
from socket import *
import struct
import os
import math
import time

ServerError = {
    0: 'Not defined, see error message( if any).',
    1: 'File not found.',
    2: 'Access violation.',
    3: 'Disk full or allocation exceeded.',
    4: 'Illegal TFTP operation.',
    5: 'Unknown transfer ID.',
    6: 'File already exists.',
    7: 'No such user.',
}
path='/home/pillete/Desktop/Servidor/'

def initialization_handler():
    if len(argv) != 3:
        print("That´s not the way to start it.")
        exit(1)
    if argv[1].lower() != "-p":
        print('You have not assigned a correct port.')
        exit(1)


def sendError(ErrorCode, peer,sock):
    print(ServerError[ErrorCode])
    data = struct.pack('!HH' + str(len(ServerError[ErrorCode])) + 'sH', 5, ErrorCode, ServerError[ErrorCode].encode(), 0)
    sock.sendto(data, peer)

def receiveData(sock,path,peer):
    f = open(path, 'wb')
    ack_msg = struct.pack('!HH', 4, 0)
    sock.sendto(ack_msg, peer)
    while 1:
        try:
            response = sock.recvfrom(518)[0]
        except error:
            msg = struct.pack('!H' + str(len(FileName)) + 'sh' + str(len(mode)) + 'sh', 1, FileName.encode(), 0, mode,0)
            sock.sendto(msg, server)
            read(FileName, mode)
        else:
            op = struct.unpack('!H', response[0:2])[0]
            if op == 3:
                pack = struct.unpack('!H', response[2:4])[0]
                print('Receive packet : ' + str(pack))
                size = len(response)
                msg = len(response) - 4
                data = struct.unpack('!' + str(msg) + 's', response[4:size])[0]
                f.write(data)
                ack_msg = struct.pack('!HH', 4, pack)
                sock.sendto(ack_msg, peer)
                if len(data) < 512:
                    print('The message has arrived')
                    break
            else:
                print('That msg was not spected')
    f.close()

def controlACK(sock, ack, path, peer):

    a = open(path, 'rb')
    ack-=1
    puntero=ack * 512
    a.seek(puntero)
    data = a.read(512)
    data = struct.pack('!HH' + str(len(data)) + 's', 3, ack, data)
    sock.sendto(data,peer)
    a.close()


def sendingData(sock,path, peer):
    sizeFile = os.path.getsize(path)
    if(sizeFile<512):
        num_packs=1
    else:
        num_packs = math.ceil(sizeFile/512)
    f = open(path, 'rb')
    response = f.read(512)
    retransmited=2
    pack = 1
    data = struct.pack('!HH' + str(len(response)) + 's', 3, pack, response)
    while 1:
        try:
            if retransmited!=0:
                print('Paquet number: ' + str(pack) + ' for host: ' + str(peer))
                sock.sendto(data, peer)
                msg = sock.recvfrom(518)[0]

            else:
                break
        except error:
            print('Try to resend message: '+pack)
            retransmited-=1
            continue
        else:
            op = struct.unpack('!H', msg[0:2])[0]
            if op == 4:
                ack = struct.unpack('!H', msg[2:4])[0]
                if ack==pack:
                    if num_packs == ack:
                        break
                    else:
                        print('Number ack:'+str(ack))
                        pack += 1
                        data = f.read(512)
                        data = struct.pack('!HH'+str(len(data))+'s', 3, pack, data)
                else:
                    controlACK(ack,path,peer)

    f.close()


def handler(sock,msg,peer):
    while 1:
        operation = struct.unpack('!H', msg[0:2])[0]
        sizepath = len(msg) - 14
        filename = struct.unpack('!' + str(sizepath) + 's', msg[2:sizepath + 2])[0]
        path = './' + filename.decode()
        if operation == 1:
            if os.path.isfile(path):
                print("Operation 1")
                print(str(peer[0]) + ' wants to read')
                sendingData(sock,path, peer)
                break
            else:
                sendError(1, peer,sock)
                break
        elif operation == 2:
            if not os.path.isfile(path):
                print("Operation 2")
                print(str(peer[0]) + ' wants to write')
                receiveData(sock,path, peer)
                break
            else:
                sendError(6, peer,sock)
                break

def main():
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(('', int(argv[2])))
    sec = 10  # Timeout of four seconds
    usec = 10000
    timevalue = struct.pack('ll', sec, usec)
    sock.setsockopt(SOL_SOCKET, SO_RCVTIMEO, timevalue)
    while 1:
        print('--Waiting for something--')  # It waits infinitly a request of some client.
        try:
            msg, client = sock.recvfrom(518)
            handler(sock,msg, client)
        except error:
            continue
    sock.close()

if __name__ == "__main__":
    try:
        initialization_handler
        main()
    except KeyboardInterrupt:
        print('Interrupted.')
        exit(0)
