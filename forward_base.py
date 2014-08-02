#coding:utf-8
import socket,threading, re,time,os,traceback,sys
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
        print '第一次接收数据就失败!'
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
        proxy_transfer_g=re.search("Transfer-Encoding: (.*)\r\n",buf)
        #第一次接收中，就带有主体信息的
        #第一次接收中，只有纯头部信息，头部信息中带有length的.没有主体信息,则send_first_body 为空
        if proxy_first_body_g:
            proxy_first_body = proxy_first_body_g.group(2)
        proxy_first_body_len = len(proxy_first_body)
        #头部带有Transfer-Encoding
        if proxy_transfer_g:
            print "头部不带长度"
            while 1:
            
                try:
                    #cl.settimeout(1)
                    #need_len = again_len+proxy_first_data_len
                    #print "已获取长度为 %d" % (len(buf))
                    cache = cl.recv(1024)
                    #print "多次接收时cache 长度为%d" % (len(cache))
                    if len(cache) == 0:
                        return buf
                    hex_cache = cache.encode('hex')
                    if re.search("0d0a300d0a0d0a$",hex_cache):
                        cl.close
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
        elif proxy_body_len_g:
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
        else:
            while 1:
                #need_len = again_len+proxy_first_data_len
                #print "已获取长度为 %d" % (len(buf))
                #print '再收一次'
                cache = cl.recv(1024)
                #if len(cache) < 1024:
                #    return buf
                if len(cache) == 0:
                    cl.close
                    return buf
                buf = buf+cache
                #带有长度的长连接，需要用实际长度来判断接收完毕
            cl.close
            return 1
        cl.close()
        return  1
