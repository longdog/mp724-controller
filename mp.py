
# -*- coding: utf-8 -*-

import pywinusb.hid as hid
from time import sleep
import socket
import threading
import ConfigParser
import sys

class SocketClient:
    __instance = None
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(SocketClient, cls).__new__(cls, *args, **kwargs)
        return cls.__instance
    
    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.__connect()


    def __connect(self):
        print('connect to socket')
        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #self.__socket.settimeout(10.0)
            self.__socket.connect((self.__host, self.__port))
            #self.__socket.setblocking(1)
            #self.__socket.send(b"\x1E")
        except:
            pass

    def read(self):
        result = None
        try:
            result = self.__socket.recv(512)
            if not result:
                raise Exception('socket', 'socket not connected')
        except:
            self.__socket.close()
            sleep(10)
            self.__connect()
        return result

    def disconnect(self):
        self.__socket.close()


class Device:

    R = 3
    G = 2
    B = 4


    __last = 'none'

    @property
    def current(self):
        return self.__current

    @property
    def report(self):
        return self.__report

    __buffer = []
    __bufferi = []

    def __init__(self, vendor_id):
        self.__vendor_id = vendor_id
        self.__connect()        
        self.__buffer = [0x00]*9
        self.__bufferi = [0x00]*9
        self.__reset()

    def __connect(self):
        print('try connect to device')
        all_devices = hid.HidDeviceFilter(vendor_id = 0x16c0).get_devices()
        if (len(all_devices) == 0):
            print('device not found')
            return
        self.__current = all_devices[0]
        self.__open()
        all_reps = self.__current.find_feature_reports()
        if (len(all_reps) == 0):
            print('report not found')
            return
        self.__report = all_reps[0]

    def __clear(self):
        self.__buffer = [0x00]*9
        self.__bufferi = [0x00]*9
        self.__send()

    def __send(self):
        print (self.__buffer)
        try:
            if (not self.__current.is_plugged()):
                raise Exception('device', 'device not plugged')
            self.__report.set_raw_data(self.__buffer)
            self.__report.send()
        except Exception,e:
            print str(e)

    def __open(self):
        self.__current.open()

    def __close(self):
        self.__current.close()

    def __set_work_time(self, sec):
        self.__clear()
        self.__buffer[1] = 0x0E
        self.__buffer[2] = 0x04
        self.__buffer[3] = sec
        self.__send()

    
    def reboot(self):
        self.__clear()
        self.__buffer[1] = 0x60
        self.__send()

    
    def t_led(self, num):
        self.__clear()
        self.__buffer[1] = 0x60
        self.__buffer[num+1] = 255
        self.__send()

    def __reset(self):
        self.rgb(self.__last)
        #print(self.__buffer)           
        self.__t = threading.Timer(60.0, self.__reset).start()

    
    def rgb(self, color):
        self.__last = color
        self.__clear()
        self.__buffer[1] = 0x65
        # if color == 'red':
        #     self.__red()
        # elif color == 'blue':
        #     self.__blue()
        # elif color == 'none':
        #     self.__none()
        if color == 'blue':
            self.__red()
        elif color == 'red':
            self.__blue()
        elif color == 'none':
            self.__none()

    def __red(self):
        self.__clear()
        self.__buffer[1] = 0x65
        self.__buffer[self.R] = 0xff
        self.__buffer[self.B] = 0x00
        self.__buffer[self.G] = 0x00
        self.__send()

        self.__buffer[1] = 0x62
        self.__buffer[self.R] = 0xe0
        self.__buffer[self.B] = 0x00
        self.__buffer[self.G] = 0x0d
        self.__send()

    def __blue(self):
        self.__clear()
        self.__buffer[1] = 0x65
        self.__buffer[self.R] = 0x00
        self.__buffer[self.B] = 0xff
        self.__buffer[self.G] = 0x00
        self.__send()

        self.__buffer[1] = 0x62
        self.__buffer[self.R] = 0x00
        self.__buffer[self.B] = 0xc6
        self.__buffer[self.G] = 0xff
        self.__send()

    def __none(self):
        self.__clear()
        self.__buffer[1] = 0x65
        self.__buffer[self.R] = 0x00
        self.__buffer[self.B] = 0x00
        self.__buffer[self.G] = 0x00
        self.__send()

        self.__buffer[1] = 0x62
        self.__buffer[self.R] = 0x00
        self.__buffer[self.B] = 0x00
        self.__buffer[self.G] = 0x00
        self.__send()

    
    def __del__(self):
        self.__t.cancel()
        self.__close()

if __name__ == '__main__':


    config = ConfigParser.RawConfigParser()
    config.read('mp.cfg')

    addr = config.get('Server', 'host')
    port = config.getint('Server', 'port')

    sc = SocketClient(addr, port)

    d = Device(0x16c0)
    while True:
        try:
            foo = sc.read()
            print(u'from socket: '+foo)
            if (len(foo)>4):
                foo = foo[-4:]
                print('use '+foo)
            if ('red' in foo):
                d.rgb('red')
            elif ('blue' in foo):
                d.rgb('blue')
            elif ('none' in foo):
                d.rgb('none')
            #if (foo == 'red' or foo == 'blue' or foo == 'none'):
            #    d.rgb(foo)
        except KeyboardInterrupt:
            sc.disconnect()
            del d
            sys.exit(1)
        except Exception,e:
            print str(e)
            sleep(5)
    sc.disconnect()
    del d