#!/usr/bin/python
import socket,threading, re,time
threads=[]
#dhost='';
#dnsip='';
def cserver():
	global buf
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
	sock.bind(('localhost', 8002)) 
	sock.listen(100)
	while True:
		connection,address = sock.accept() 
		if connection:  
			connection.settimeout(10)  
			pbuf = connection.recv(1024)  
			#print pbuf
			pbuf=re.search("GET http://(.*?)/(.*?) HTTP/1.1([\s\S]*)",pbuf)
			if pbuf:
				buf="GET /"+pbuf.group(2)+" HTTP/1.1"+pbuf.group(3)
				#print rbuf
				if buf:
					getHost()
			#t2=threading.Thread(target=getIp(),args=())
			#t2.start()
			#t2.join()
					getIp()
			#print dnsip
					t=threading.Thread(target=forworld,args=())
					t.start()
					t.join()
					print cbuf
					connection.send(cbuf)
		connection.close()  
		
def getHost():
	global dhost
	dhost_se=re.search('Host: (.*)\r\n',buf)
	if dhost_se:
		dhost=dhost_se.group(1)
		#file=open('content.txt','w+')
		#file.write(dhost)
		#file.close
		resultt = socket.getaddrinfo(dhost,None)
		print 'get host success!!!!!!!!!!'
		return dhost
def getIp():
	global dnsip
	#result = socket.getaddrinfo('wenku.baidu.com', None)
	#resultt = socket.getaddrinfo('www.test.com', None)
	resultt = socket.getaddrinfo(dhost,None)
	if resultt:
		dnsip=resultt[0][4][0]
		print 'get ip success!!!!!!!!!!'
		return dnsip
#	global ip
#	dnsData='Queries'+dhost+': type A,class In Name:'+dhost+'Type: A (Host address)Class: IN (0x0001)'
#	dnscl  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#	if dnscl.sendto(dnsData,dnsip):
#		dnsdata=dnscl.recvfrom(10240)
#		if dnsdata:
#			print dnsdata
def forworld():
	global cbuf
	cl  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
	cl.connect((dnsip,80))
	cl.settimeout(1)
	print 'starting send buf'
	cl.send(buf)
	print 'buf is ', buf
	cbuf=cl.recv(1024)
	print 'starting recving cbuf.....'
	if cbuf:
		cbufLen_g=re.search("Content-Length: (.*)\r\n",cbuf)
		if cbufLen_g:
			cbufLen=int(cbufLen_g.group(1))
			print 'Centent-Length is ' ,cbufLen
			if cbufLen:
				cbuf1=cl.recv(cbufLen,socket.MSG_WAITALL)
				cbuf=cbuf+cbuf1
		else:
			print 'recv again one'
			try:
				cbuf1=cl.recv(1024)
			except socket.timeout:
				return 0
			if cbuf1!=None:
				cbuf=cbuf+cbuf1
			while  cbuf1!=None:
				try:
					print 'recv again'
					cbuf1=cl.recv(1024)
					print cbuf1
					cbuf=cbuf+cbuf1
				except socket.timeout:
					cbuf1=None
	cl.close()  
	print 'get data success!!!!!!!!!!!'
	return cbuf
#		if buf == '1':  
#			connection.send('welcome to server!')  
#		else:  
#			connection.send('please go out!')  
#	cl  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
#	cl.connect(('www.baidu.com',80))
cserver()
