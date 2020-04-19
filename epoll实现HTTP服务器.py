#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/4/19 9:53
# @Author  : Coco
# @Site    : SH #5-389
# @File    : epoll实现HTTP服务器.py
# @Email   : chao.li@amlogic.com
# @Software: PyCharm


import socket
import select
import re


def server_client(new_socket, recv_date):
    '''

    :param new_socket: 需要服务的套接字
    :param recv_date: 套接字的请求数据
    :return:
    '''
    # 定义想要获取的文件名
    filename = ''
    # 定义响应的数据
    response = ''
    request_linies = recv_data.splitlines()
    ret = re.match(r'[^/]+(/[^ ]*)', request_linies[0])
    if ret:
        filename = ret.group(1)
        # 定义默认请求为请求主页
        if filename == '/':
            filename = '/index.html'
    try:
        print('-----', filename)
        with open('./html' + filename, 'rb') as f:
            html_content = f.read()
    except Exception as e:
        print(e)
        print('----File not found----')
        response += 'HTTP/1.1 404 NOT FOUND\r\n'
        response += '\r\n'
        new_socket.send(response.encode('utf-8'))
    else:
        response_body = html_content
        response_header = 'HTTP/1.1 200 OK \r\n'
        response_header += 'Content-Length:%d\r\n' % (len(response_body))
        response_header += '\r\n'
        response = response_header.encode('utf-8') + response_body
        new_socket.send(response)


if __name__ == '__main__':
    # 创建套接字
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 设置端口复用
    tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 绑定套接字
    tcp_server_socket.bind(('', 7890))
    # 设置套接字监听
    tcp_server_socket.listen(128)

    # 设置非堵塞
    tcp_server_socket.setblocking(False)

    # 创建epoll对象
    epl = select.epoll()
    epl.register(tcp_server_socket.fileno(), select.EPOLLIN)
    fd_event_dict = dict()
    while True:
        # 堵塞 知道接收到数据到来
        fd_event_list = epl.poll()  # [(fd,event),....]
        for fd, event in fd_event_list:
            # 判断是否为监听套接字
            if fd == tcp_server_socket.fileno():
                new_socket, client_addr = tcp_server_socket.accept()
                epl.register(new_socket.fileno(), select.EPOLLIN)
                # 在字典中存储新套接字对象
                fd_event_dict[new_socket.fileno()] = new_socket
            # 判断是否是客户端请求
            elif event == select.EPOLLIN:
                recv_data = fd_event_dict[fd].recv(1024).decode('utf-8')
                # 判断该服务端是否关闭
                if recv_data:
                    server_client(fd_event_dict[fd], recv_data)
                else:
                    # 关闭该套接字
                    fd_event_dict[fd].close()
                    # 在epoll中注销该套接字
                    epl.unregister(fd)
                    del fd_event_dict[fd]
