#!/usr/bin/python
import time,re
if __name__ == '__main__':  
	import socket  
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
	sock.connect(('127.0.0.1', 80))  
	#message = "GET /test.html HTTP/1.1\r\nHost: localhost\r\n\r\n"
	data=("GET /test.jpg HTTP/1.1\r\nHost: www.test.com\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0\r\nAccept: */*\r\nConnection: Keep-Alive\r\n\r\n")
	sock.sendall(data)
	content=sock.recv(1024)
	if content:
		contentLen_g=re.search("Content-Length: (.*)\r\n",content)
		contentLen=int(contentLen_g.group(1))
		headers=re.search("(.*)\r\n\r\n",content)
		if headers:
			headers_len=len(headers.group(1))+4
			realLen=contentLen-(1024-headers_len)
			print realLen
			content1=sock.recv(realLen,socket.MSG_WAITALL)
			content=content+content1
	sock.close()  
	realContent_g=re.search("(.*)\r\n\r\n([\s\S]*)",content)
	if realContent_g:
		realContent=realContent_g.group(2)
		if realContent:
			filename='test.jpg'
			f=open(filename,'w')
			f.writelines(realContent)
			f.close
