#!/usr/bin/python3
# Copyright: See AUTHORS and COPYING
"Usage: {0} -p <port> "


from sys import argv, exit
from socket import *
import _thread, time, struct
import os
import math


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

def sendData(path, sock):
    sizeFile = os.path.getsize(path)
    num_packs = math.ceil(sizeFile/512)
    f = open(path, 'rb')
    response = f.read(512)
    data = struct.pack('!HH' + str(len(response)) + 's', 3, 1, response)
    print('Sending msg')
    while num_packs:
        try:
            sock.send(data)
            num_packs-=1
            msg = sock.recv(518)
        except error:
            print('The client is not connected')
            continue
        else:
            op = struct.unpack('!H', msg[0:2])[0]
            if op == 4:
                data = f.read(512)
                pack = struct.unpack('!H',msg[2:4])[0]+1
                data = struct.pack('!HH'+str(len(data))+'s', 3, pack, data)
                if num_packs == 0:
                    break
    f.close()


def sendACK(response,sock):
    ack=struct.unpack('!H',response[2:4])[0]
    msgtosend=struct.pack('!2H',4,ack)
    sock.send(msgtosend)

def receiveData(path, sock):
    f = open(path, 'wb')
    pack=0
    while 1:
        try:
            response=sock.recv(518)
        except error:
            print('The client is no connected')
        else:
            struct.pack('!2H',4,pack)
            op = struct.unpack('!H', response[0:2])[0]
            if op == 3:
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

def handle(sock, client, n):
    print('Client connected', n, client)
    while 1:
        print('--Waiting for something--')
        msg = sock.recv(518)
        op = struct.unpack('!H', msg[0:2])[0]
        sizefile = len(msg) - 14
        print(op)
        if op == 1:
            filename = struct.unpack('!' + str(sizefile) + 's', msg[2:sizefile + 2])[0]
            path = './' + filename.decode()
            if os.path.isfile(path):
                print('The client is reading')
                sendData(path, sock)
            else:
                sendError(1, client,sock)
        if op == 2:
            filename = struct.unpack('!' + str(sizefile) + 's', msg[2:sizefile + 2])[0]
            path = './' + filename.decode()
            if not os.path.isfile(path):
                print('The client is writing')
                sizefile = len(msg) - 14
                receiveData(path, sock)
            else:
                sendError(6, client,sock)
        elif op== 6:
            print('The client has'+str(client)+ 'disconected')
            exit(0)

sock = socket(AF_INET, SOCK_STREAM)
initialization_handler
sock.bind(('', int(argv[2])))
sec = 50  # Timeout of four seconds
usec = 10000
timevalue = struct.pack('ll', sec, usec)
sock.setsockopt(SOL_SOCKET, SO_RCVTIMEO, timevalue)
sock.listen(5)
n = 0

while 1:
    child_sock, client = sock.accept()
    n += 1
    _thread.start_new_thread(handle, (child_sock, client, n))
