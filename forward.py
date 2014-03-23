#!/usr/bin/python
#coding:utf-8
import socket,threading, re,time,os,traceback,sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
sock.bind(('localhost', 8002)) 
sock.listen(1000)
def reap():
    while 1:
        try:
            result=os.waitpid(-1,os.WNOHANG)
            if not result[0]:break
        except:
            break
        print"已被杀掉的子进程 %d" % result[0]
        
def cserver():
    global buf
    if connection:  
        connection.settimeout(10)  
        #######接收保存client请求信息
        pbuf = connection.recv(1024)  
        print pbuf
        #提取请求头中的host,修改请求头
        pbuf=re.search("GET http://(.*?)/(.*?) HTTP/1.1([\s\S]*)",pbuf)
        if pbuf:
            buf="GET /"+pbuf.group(2)+" HTTP/1.1"+pbuf.group(3)
            #print rbuof
            print '收到请求 --- > http://',pbuf.group(1),pbuf.group(2)
            print '开始转发....'
            if buf:
                getHost()
                getIp()
                ###遇到302重定向无法转发的问题
                forward()
                if cbuf:
                    print '返回给client header'
                    connection.send(cbuf_all[0])
                    print '返回给client data'
                    connection.send(cbuf_all[1])
                    time.sleep(5)
    print '发送完，关口socket'
    connection.close()  
    sys.exit(0)
        
##提取主机名
def getHost():
    global dhost
    dhost_se=re.search('Host: (.*)\r\n',buf)
    if dhost_se:
        dhost=dhost_se.group(1)
        resultt = socket.getaddrinfo(dhost,None)
        print '获取请求的主机名成功'
        return dhost
##解析ip
def getIp():
    global dnsip
    resultt = socket.getaddrinfo(dhost,None)
    if resultt:
        dnsip=resultt[0][4][0]
        print '获取ip成功'
        return dnsip
def forward():
    global cbuf
    global cbuf_data
    global cbuf_all
    cbuf_data=''
    cl  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    cl.connect((dnsip,80))
    cl.settimeout(10)
    cl.send(buf)
    #####返回给client时也应该分2次返回，一次返回header，一次返回数据
    print '发送代理请求中....'
    ##第一次接收headers,如果有Content-Length，以固定长度一次接收剩下的，如果没有该字段，循环每次接收1024字节，直到超时，判定接收完,将尔后每次接收的内容追加到第一次接收的内容中，一次返回给client
    try:
        print '开始接收数据...'
        cbuf=cl.recv(1024)
   #     if re.search('\r\n\r\n',cbuf)==True:
    #        print cbuf
    except socket.timeout:
        print 'bad!'
        return 1
    if cbuf:
        print '第一次数据接收成功'
        print cbuf
        header_length=len(cbuf)
        cbufLen_g=re.search("Content-Length: (.*)\r\n",cbuf)
        if cbufLen_g:
            cbufLen=int(cbufLen_g.group(1))
            if cbufLen:
                #######应该计算已接收数据长度，如果刚好等于该值，则不需要进行下一步接收
                print '长度为:',cbufLen
                print '头部长度 %d' % header_length
                if cbufLen != header_length:
                    print '获取长度成功，开始接收全部数据...'
                    while (len(cbuf_data)<cbufLen):
                        try:
                            cbuf1=cl.recv(1460)
                    #cbuf1=cl.recv(cbufLen,socket.MSG_WAITALL)
                            cbuf_data=cbuf_data+cbuf1
                        except Exception,ex:
                            print Exception,":",ex
                            print '已接收完'
                    if len(cbuf_data)==cbufLen:
                        print '接收所有数据成功'
#考虑到有的请求里面并不返回length这个字段，暂时不处理这种请求 else 段注释掉
        else:
            print '不包含length字段，无法处理请求!'
#        else:
#            try:
#                cbuf1=cl.recv(1024)
#                print '第二次，没有长度的接收'
#            except socket.timeout:
#                cbuf1=None
#            if cbuf1!=None and cbuf1!='':
#                cbuf=cbuf+cbuf1
#            while  cbuf1!=None and cbuf1!='':
#                try:
#                    print 'recv again'
#                    cbuf1=cl.recv(1024)
#    #                print cbuf1
#                    cbuf=cbuf+cbuf1
#                except socket.timeout:
#                    cbuf1=None
    cl.close()  
    cbuf_all=[cbuf,cbuf_data]
    return cbuf_all
while True:
    try:
        connection,address = sock.accept() 
    except:
        traceback.print_exc()
        continue
    reap()
    pid=os.fork()
    if pid:
        connection.close   
    else:
        print '开启子进程处理请求: %d'  % os.getpid()
        sock.close
        try:
            cserver()
        except Exception,ex:
            print Exception,":",ex
            continue
            
                
