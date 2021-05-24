import importlib
import logging
import queue
import sys
import threading
import time
from datetime import  datetime
from enum import Enum
from socket import *
from socketserver import TCPServer, ThreadingMixIn, StreamRequestHandler

from web import run

importlib.reload(sys)
address = '0.0.0.0'  # 监听哪些网络  127.0.0.1是监听本机 0.0.0.0是监听整个网络
port = 9998  # 监听自己的哪个端口
buffsize = 1024  # 接收从客户端发来的数据的缓存区大小
s = socket(AF_INET, SOCK_STREAM)
#非阻塞
s.setblocking(False)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s.bind((address, port))
s.listen(5)  # 最大连接数

# 同时打开的线程数和线程列表
thread_num = 0
threads = []
# 黑名单
BlackList = "blacklist.txt"
# 网络连接列表，记录了接入的连接，关闭或中断了的连接需要从该表中清除
ConnectList = []
ConnectMax = 10
# 消息队列
msg_queue = queue.Queue()

# 日志记录
logging.basicConfig(level=logging.INFO,
                    filename='./log.txt',
                    filemode='w',
                    format='%(asctime)s : %(funcName)s : %(levelname)s : %(message)s')


# 状态列表
class THREAD_STATE(Enum):
    stInit = 0
    stChat = 4
    stError = 5
    stFetch = 6
    stSave = 7


# 一条消息的数据结构
class TMSGObj:
    def __init__(self):
        self.clientsock = None
        self.clientaddress = None
        self.TextMsg = ''

    def setText(self, text):
        self.TextMsg = text

    def setclient(self, client_sock, client_address):
        self.clientsock = client_sock
        self.clientaddress = client_address

    def getText(self):
        return self.TextMsg

    def getclientsock(self):
        return self.clientsock

    def getclientaddress(self):
        return self.clientaddress

    def getTextandclient(self):
        return self.TextMsg, self.clientsock, self.clientaddress

class DialogThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.email = 'duplicate2021@163.com'
        self.password = 'duplicate123'
        self.state = THREAD_STATE.stInit
        self.message = None
        self.listener = None
        self.driver = None

    def setState(self, state):
        self.state = state

    def getState(self):
        return self.state

    def setDriver(self, driver):
        self.driver = driver

    def setListenerThread(self, thread):
        self.listener = thread

    def getListenerThread(self):
        return self.listener

    def setEmpty(self):
        self.driver = None
        self.listener = None
        self.message = None

    def run(self):
        global begin_time
        while True:
            if self.state == THREAD_STATE.stInit:
                try:
                    driver = run.load_webpage()
                    self.setDriver(driver)
                    run.login(self.driver,self.email, self.password)
                    self.state = THREAD_STATE.stFetch
                    print('Operator is ready to fetch message.')
                    logging.info('Operator is ready to fetch message.')
                    # 记录开始时间
                    begin_time = datetime.now()
                except Exception as e:
                    logging.error('Operator error in stInit: ' + str(e))
                    self.state = THREAD_STATE.stError
            elif self.state == THREAD_STATE.stFetch:

                try:
                    while True:
                        if msg_queue.empty():
                            cur_time = datetime.now()
                            # 一个小时后重新启动浏览器
                            if (cur_time - begin_time).seconds > 3600:
                                self.state = THREAD_STATE.stError
                                break
                            continue
                        else:
                            self.message = msg_queue.get()
                            self.state = THREAD_STATE.stChat
                            msg_queue.task_done()
                            break
                except Exception as e:
                    logging.error('Operator error in stFetch: ' + str(e))
                    self.state = THREAD_STATE.stError
            elif self.state == THREAD_STATE.stChat:
                try:
                    if not self.getListenerThread():
                        # 打开一个监听线程
                        print(threading.current_thread().name + ' open a listener thread to check '
                                                                'message from replika.')
                        logging.info(threading.current_thread().name + ' open a listener thread to check '
                                                                       'message from replika.')
                        t = run.Listener_Thread(self.driver)
                        self.setListenerThread(t)
                        t.start()
                    #当有效位仍为1，说明监听线程仍在获取AI的消息，现在还不能发下一条消息，直到监听线程将自己的有效位置0
                    while True:
                        if self.getListenerThread().getValid()==1:
                            continue
                        else:
                            break
                    logging.info('Now send the message from ' + str(
                        self.message.getclientaddress()[0]) + ' content:' + self.message.getText())
                    run.send_message(self.driver, self.message.getText())
                    #给监听线程设置clientsock和有效位
                    self.getListenerThread().setClient(self.message.getclientsock())
                    self.getListenerThread().setValid()
                    self.state = THREAD_STATE.stFetch
                except Exception as e:
                    logging.error('Operator error in stChat: ' + str(e))
                    self.state = THREAD_STATE.stError
            elif self.state == THREAD_STATE.stError:
                logging.info('into stError.')
                try:
                    self.setEmpty()
                    self.state = THREAD_STATE.stInit
                    if self.getListenerThread():
                        logging.info('stError close listener.')
                        self.getListenerThread().setStop()
                        self.getListenerThread().join()
                    # 关闭浏览器
                    run.quit(self.driver)
                    logging.info('close driver.')
                    time.sleep(10)
                    logging.info('Operator is preparing for retry on logging to replika.')
                except Exception as e:
                    print('Operator error in stError: ' + str(e))
                    logging.error('Operator error in stError: ' + str(e))
                    logging.info('Operator is preparing for retry on logging to replika.')
                    self.state = THREAD_STATE.stInit

# # 等待一段时间再处理下一条消息，因为若两条消息发得太快AI可能会认成同一条消息
# def waitBetweenMessage():
#     time.sleep(5)


if __name__ == "__main__":
    # with Server(('49.234.110.208', 9999), Handler) as server:
    #     server.serve_forever()
    Operator = DialogThread()
    Operator.start()
    while True:
        if len(ConnectList) > ConnectMax:
            logging.info('There are more than 10 connects now.')
            continue
        try:
            clientsock, clientaddress = s.accept()
        except:
            pass
        else:
            blackIP = 0
            # 查看黑名单是否有这个IP,有的话直接close连接
            bl = open(BlackList, 'r')
            while True:
                line = bl.readline()
                if not line:
                    break
                line = line.strip('\n')
                if line == str(clientaddress[0]):
                    logging.info('Catch a bad IP: ' + str(clientaddress[0]))
                    clientsock.close()
                    blackIP = 1
                    break
            bl.close()
            if blackIP == 1:
                continue
            print('connect from:' + str(clientaddress))
            logging.info('connect from:' + str(clientaddress))
            clientsock.setblocking(False)
            ConnectList.append((clientsock,clientaddress))
        for clientsock,clientaddress in ConnectList:
            try:
                recvData = clientsock.recv(1024).decode('utf-8')
            except:
                pass
            else:
                if recvData:
                    # 判断是否为退出信息
                    infos = recvData.split('|', 1)
                    if infos[0] == '-1':
                        clientsock.close()
                        ConnectList.remove((clientsock, clientaddress))
                        logging.info("Client %s has closed due to exit code -1." % str(clientaddress))
                    elif infos[0] == '1':
                        msg = TMSGObj()
                        msg.setText(infos[1])
                        msg.setclient(clientsock, clientaddress)
                        logging.info(
                            'A new message is added to queue. ' + str(
                                msg.getclientaddress()[0]) + ' content:' + str(
                                msg.getText()))
                        # 加入消息队列
                        msg_queue.put(msg)
                    elif infos[0] == '0':
                         logging.info('This is a legal login request.')
                         clientsock.send("success".encode())
                    else:
                        # 加入黑名单
                        logging.info('This is an illegal request.')
                        blackL = open(BlackList, "a+")
                        logging.info("Write " + str(clientaddress[0]) + " to black list.")
                        blackL.write(str(clientaddress[0]) + '\n')
                        blackL.close()
                        clientsock.close()
                        ConnectList.remove((clientsock,clientaddress))
                        logging.info("Client %s has closed due to illegal request." % str(clientaddress))
                else:
                    clientsock.close()
                    ConnectList.remove((clientsock, clientaddress))
                    logging.info("Client %s has closed due to exit client." % str(clientaddress))

        # client = ClientThread(clientsock, clientaddress)
        # client.start()
        # threads.append(client)
