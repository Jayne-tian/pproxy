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
			#######接收保存client请求信息
			pbuf = connection.recv(1024)  
			#print pbuf
			#提取请求头中的host,修改请求头
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
		
##提取主机名
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
##解析ip
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
	cl.send(buf)
	##第一次接收headers,如果有Content-Length，以固定长度一次接收剩下的，如果没有该字段，循环每次接收1024字节，直到超时，判定接收完,将尔后每次接收的内容追加到第一次接收的内容中，一次返回给client
	cbuf=cl.recv(1024)
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
				cbuf1=None
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
