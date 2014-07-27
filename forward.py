#!/usr/local/python27/bin/python
#coding:utf-8
import socket,threading, re,time,os,traceback,sys
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
sock.bind(('0.0.0.0', 8002)) 
sock.listen(1000)
def start():
    if connection:  
        connection.settimeout(10)  
        #######接收保存client请求信息
        headers_data = connection.recv(1024)  
        #提取请求头中的host,修改请求头
        headers_data_g = re.search("GET http://(.*?) HTTP/(.*?)([\s\S]*)",headers_data)
        #headers_data_g = re.search("GET http://(.*?)/(.*?) HTTP/(.*?)([\s\S]*)" or "GET http://(.*?) HTTP/(.*?)([\s\S]*) ",headers_data)
        if headers_data_g:
            headers="GET /"+headers_data_g.group(1)+" HTTP/"+headers_data_g.group(2)+headers_data_g.group(3)
            #headers="GET /"+headers_data_g.group(2)+" HTTP/"+headers_data_g.group(3)+headers_data_g.group(4)
            #print buf
            print '收到请求 --- > http://',headers_data_g.group(1),headers_data_g.group(2)
            print '开始转发....'
            hostname = get_hostname(headers_data)
            #hostname = getHost(headers)
            hostip = get_ip(hostname)
            if hostip == 1:
                connection.sendall('域名无法解析')
                connection.close
                return 1
            ###遇到302重定向无法转发的问题
            buf = forward(hostip,headers_data)
            #buf = forward(hostip,headers)
            print "开始返回数据"
            if buf and buf != 1:
                buf_len = len(buf)
                print '返回给client的长度为%d' % buf_len
                print '返回给client header'
                connection.sendall(buf)
                #connection.sendall(buf[1])
                #本来此处header和body应该分开返回，待后续处理
                #print '返回给client data'
                #if cbuf_all !='':
                #    connection.send(cbuf_all[1])
                #time.sleep(5)
                print '发送完，关闭socket'
                connection.close()  
                #sys.exit(0)
        else:
            print '没发现请求头'
            connection.close()  
        
##提取主机名
def get_hostname(buf):
    dhost_g=re.search('Host: (.*)\r\n',buf)
    try:
        hostname=dhost_g.group(1)
        #result = socket.getaddrinfo(hostname,None)
        print '获取请求的主机名成功'
        return hostname
    except Exception,ex:
        print Exception,":",ex
        return 1
##解析ip
def get_ip(dhost):
    try:
        result = socket.getaddrinfo(dhost,None)
        if result:
            hostip=result[0][4][0]
            print '获取ip成功'
            return hostip
    except Exception,ex:
        print Exception,":",ex
        return 1
def forward(hostip,headers):
    cl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    cl.connect((hostip,80))
    cl.settimeout(10)
    #print(headers)
    cl.send(headers)
    buf = ''
    #####返回给client时也应该分2次返回，一次返回header，一次返回数据
    print '发送代理请求中....'
    #如果header+data 都小于1024的话，header+data会在一次就全部发送完毕
    try:
        print '开始接收数据...'
        buf=cl.recv(1024)
        #print buf
   #     if re.search('\r\n\r\n',cbuf)==True:
    #        print cbuf
    except socket.timeout:
        print 'bad!'
        return 1
    if buf:
        print '第一次数据接收成功'
        proxy_first_data_len=len(buf)
        proxy_header_g = re.search("([\S\s]+)\r\n\r\n",buf)
        #send_header_g = re.search("([\S\s]+)\r\n\r\n([\S\s]+)",buf)
        try:
            proxy_header = proxy_header_g.group(1)
            #print send_header
            proxy_header_len = len(proxy_header)+4
            #print proxy_proxy_first_data_len
        except Exception,ex:
            print Exception,":",ex
            print 'not found header'
            cl.close()
            return 1
        proxy_first_body_g = re.search("([\S\s]+)\r\n\r\n([\S\s]+)",buf)
        proxy_first_body = ''
        proxy_body_len_g=re.search("Content-Length: (.*)\r\n",buf)
        #第一次接收中，就带有主体信息的
        #第一次接收中，只有纯头部信息，头部信息中带有length的.没有主体信息,则send_first_body 为空
        if proxy_first_body_g:
            proxy_first_body = proxy_first_body_g.group(2)
        proxy_first_body_len = len(proxy_first_body)
        if proxy_body_len_g:
            proxy_body_len=int(proxy_body_len_g.group(1))
            if proxy_body_len:
                print '第一次接收总长度为:',proxy_first_data_len
                print '主体长度 %d' % proxy_body_len
                print '获取长度成功，开始接收全部数据...'
                #带长度的，头和主体一起接收成功的，主体太短，只需要接收一次的
                need = proxy_body_len-proxy_first_body_len+proxy_first_data_len
                if proxy_first_body_len == proxy_body_len:
                    return buf
                #带长度的，头和主体一起接收成功的，主体较长，需要循环多次接收的
                try:
                    #need = proxy_first_data_len-(proxy_first_data_len-proxy_proxy_first_data_len)+body_len
                    print '需要接受的数据长度为 %d' %  need
                    print "第一次接收中的有效数据为%d" % proxy_first_body_len
                    #again_len = body_len-body_in_proxy_first_data_len
                    #print "准备接受的数据长度为%d" %  again_len
                    while 1:
                        #need_len = again_len+proxy_first_data_len
                        #print "已获取长度为 %d" % (len(buf))
                        #print '再收一次'
                        cache = cl.recv(1024)
                        #if len(cache) < 1024:
                        #    return buf
                        buf = buf+cache
                        #带有长度的长连接，需要用实际长度来判断接收完毕
                        if need == len(buf):
                            return buf
                        if len(cache) == 0:
                            return buf
                        #buf = cl.recv(again_len)+buf
        #cbuf1=cl.recv(cbufLen,socket.MSG_WAITALL)
                    #print '已接收长度 %d'  % (len(cbuf_data))
                        #print '接收所有数据成功'
                        #print '所有数据长度为 %d  %d' % (len(buf),len(cache))
                except Exception,ex:
                    print Exception,":",ex
                    cl.close()
                    return 1
            else:
                cl.close
                return 1
        #if body_len_g and send_body_g is None:
        else:
            while 1:
                try:
                    #cl.settimeout(1)
                    #need_len = again_len+proxy_first_data_len
                    #print "已获取长度为 %d" % (len(buf))
                    cache = cl.recv(1024)
                    #print "多次接收时cache 长度为%d" % (len(cache))
                    if len(cache) == 0:
                        return buf
                    buf = buf+cache
                    #buf = cl.recv(again_len)+buf
    #cbuf1=cl.recv(cbufLen,socket.MSG_WAITALL)
                #print '已接收长度 %d'  % (len(cbuf_data))
                    #print '接收所有数据成功'
                    #print '所有数据长度为 %d' % (len(buf))
                except Exception,ex:
                    print Exception,":",ex
                    #print '接收出了问题'
                    cl.close()
                    #print '所有数据长度为 %d' % (len(buf))
                    return buf
            #print '不包含length字段，无法处理请求!'
        cl.close()
        return  1
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
while True:
    try:
        connection,address = sock.accept() 
        start()
        
    except Exception,ex:
        print Exception,":",ex
