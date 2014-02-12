#!/usr/bin/python
import time,re,socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect(('127.0.0.1', 80))  
sock.connect(('115.239.210.27', 80))  
#message = "GET /test.html HTTP/1.1\r\nHost: localhost\r\n\r\n"
data=("GET / HTTP/1.1\r\nHost: www.baidu.com\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0\r\nAccept: */*\r\nConnection: Close\r\n\r\n")
#data=("GET / HTTP/1.1\r\nHost: baidu.com\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0\r\nAccept: */*\r\nConnection: Keep-Alive\r\n\r\n")
#data=("GET /test.jpg HTTP/1.1\r\nHost: www.test.com\r\nUser-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0\r\nAccept: */*\r\nConnection: Close\r\n\r\n")
sock.sendall(data)
sock.settimeout(1)
content=sock.recv(1024)
print content
if content:
	contentLen_g=re.search("Content-Length: (.*)\r\n",content)
	if contentLen_g:
		contentLen=int(contentLen_g.group(1))
		print 'contentLen is ',contentLen
		if contentLen:
			headers=re.search("(.*)\r\n\r\n",content)
			if headers:
	#			headers_len=len(headers.group(1))+4
	#			realLen=contentLen-(300-headers_len)
	#			print realLen
				content1=sock.recv(contentLen,socket.MSG_WAITALL)
				content=content+content1
	else:
		print 'recv again one'
		content1=sock.recv(1024)
		if content1!=None:
			content=content+content1
		while  content1!=None and content1!='':
			try:
				#print 'recv again'
				content1=sock.recv(1024)
				print content1
				content=content+content1
			except socket.timeout:
				content1=None	
				break
sock.close()  
#print content
