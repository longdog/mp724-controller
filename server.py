#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import socket
from time import sleep
 
host = "10.0.0.140"
port = 44444
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(5)
sock, addr = s.accept()
while True:
	sock.send('red')
	sleep(2)
	sock.send('blue')
	sleep(2)
	sock.send('none')
	sleep(2)
        
sock.close()