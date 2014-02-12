#!/usr/bin/python
#coding:utf-8
import socket,threading, re,time

threads=[]
#dhost='';
#dnsip='';
class pserver:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.sock.bind(('localhost', 8002)) 
        self.sock.listen(1000)
        while True:
            num='1'
            client='client'
            client=client+num
            self.client=threading.Thread(target=self.cserver,args=())
            self.client.start()
            self.client.join()
            num=int(num)
            num+=1
            num=str(num)
    def cserver(self):
            self.connection,self.address = self.sock.accept() 
            if self.connection:  
                self.connection.settimeout(10)  
                #######接收保存client请求信息
                self.pbuf = self.connection.recv(1024)  
                print self.pbuf
                #提取请求头中的host,修改请求头
                self.pbuf=re.search("GET http://(.*?)/(.*?) HTTP/1.1([\s\S]*)",self.pbuf)
                if self.pbuf:
                    self.buf="GET /"+self.pbuf.group(2)+" HTTP/1.1"+self.pbuf.group(3)
                    #print rbuf
                    if self.buf:
                        self.getHost()
                #t2=threading.Thread(target=getIp(),args=())
                #t2.start()
                #t2.join()
                        self.getIp()
                #print dnsip
                        self.t=threading.Thread(target=self.forworld,args=())
                        self.t.start()
                        self.t.join()
                        #print self.cbuf
                        if self.cbuf:
                            self.connection.send(self.cbuf)
            self.connection.close()  
            
    ##提取主机名
    def getHost(self):
        self.dhost_se=re.search('Host: (.*)\r\n',self.buf)
        if self.dhost_se:
            self.dhost=self.dhost_se.group(1)
            #file=open('content.txt','w+')
            #file.write(dhost)
            #file.close
            self.resultt = socket.getaddrinfo(self.dhost,None)
            return self.dhost
    ##解析ip
    def getIp(self):
        #result = socket.getaddrinfo('wenku.baidu.com', None)
        #resultt = socket.getaddrinfo('www.test.com', None)
        self.resultt = socket.getaddrinfo(self.dhost,None)
        if self.resultt:
            self.dnsip=self.resultt[0][4][0]
            return self.dnsip
    #   global ip
    #   dnsData='Queries'+dhost+': type A,class In Name:'+dhost+'Type: A (Host address)Class: IN (0x0001)'
    #   dnscl  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #   if dnscl.sendto(dnsData,dnsip):
    #       dnsdata=dnscl.recvfrom(10240)
    #       if dnsdata:
    #           print dnsdata
    def forward(self):
        self.cl  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.cl.connect((self.dnsip,80))
        self.cl.settimeout(10)
        self.cl.send(self.buf)
        print '发丝代理请求中....'
        ##第一次接收headers,如果有Content-Length，以固定长度一次接收剩下的，如果没有该字段，循环每次接收1024字节，直到超时，判定接收完,将尔后每次接收的内容追加到第一次接收的内容中，一次返回给client
        try:
            print '开始接收数据...'
            self.cbuf=self.cl.recv(1024)
            if re.search('\r\n\r\n',self.cbuf)==True:
                print self.cbuf
        except socket.timeout:
            print 'bad!'
            return 1
        if self.cbuf:
            print '第一次数据接收成功'
            print self.cbuf
            self.cbufLen_g=re.search("Content-Length: (.*)\r\n",self.cbuf)
            if self.cbufLen_g:
                self.cbufLen=int(self.cbufLen_g.group(1))
                if self.cbufLen:
                    print '长度为:',self.cbufLen
                    print '获取长度成功，开始接收全部数据...'
                    self.cbuf1=self.cl.recv(self.cbufLen)
                        #self.cbuf1=self.cl.recv(self.cbufLen,socket.MSG_WAITALL)
                    self.cbuf=self.cbuf+self.cbuf1
                #   try:
            #           print '长度为:',self.cbufLen
        #               print '获取长度成功，开始接收全部数据...'
    #                   self.cbuf1=self.cl.recv(self.cbufLen)
                        #self.cbuf1=self.cl.recv(self.cbufLen,socket.MSG_WAITALL)
#                       self.cbuf=self.cbuf+self.cbuf1
#                       print '第二次'
                #       print self.cbuf
#                   except socket.timeout:
#                       print '接收全部数据超时'
#                       return 1
            else:
                try:
                    self.cbuf1=self.cl.recv(1024)
                    print '第二次，没有长度的接收'
                except socket.timeout:
                    self.cbuf1=None
                if self.cbuf1!=None and self.cbuf1!='':
                    self.cbuf=self.cbuf+self.cbuf1
                while  self.cbuf1!=None and self.cbuf1!='':
                    try:
                        print 'recv again'
                        self.cbuf1=self.cl.recv(1024)
                        print self.cbuf1
                        self.cbuf=self.cbuf+self.cbuf1
                    except socket.timeout:
                        self.cbuf1=None
        self.cl.close()  
        return self.cbuf
    #       if buf == '1':  
    #           connection.send('welcome to server!')  
    #       else:  
    #           connection.send('please go out!')  
    #   cl  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    #   cl.connect(('www.baidu.com',80))
proxy=pserver()
proxy.cserver()
