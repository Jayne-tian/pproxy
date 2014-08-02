#!/usr/local/python27/bin/python
#coding:utf-8
import socket,threading, re,time,os,traceback,sys
import forward_base
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
            hostname = forward_base.get_hostname(headers_data)
            #hostname = getHost(headers)
            hostip = forward_base.get_ip(hostname)
            if hostip == 1:
                connection.sendall('域名无法解析')
                connection.close
                return 1
            ###遇到302重定向无法转发的问题
            buf = forward_base.forward(hostip,headers_data)
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
        
while True:
    try:
        connection,address = sock.accept() 
        start()
    except Exception,ex:
        print Exception,":",ex
