import datetime

from selenium import webdriver
from pyvirtualdisplay import Display
import threading
from selenium.webdriver.common.keys import Keys
from .tools import *
from .Translation import *
from enum import Enum
import time
import logging
import datetime
import logging

FILE_NAME = 'chat.log'

display = Display(visible=0, size=(1920, 1080))
display.start()

fetch_num = 10
save_num = 10


def load_webpage():
    # 网站连接
    driver = webdriver.Firefox()
    driver.get('https://my.replika.ai/')
    # driver.implicitly_wait(30)
    return driver


def login(driver, email, password):
    log_in = driver.find_element_by_xpath('//*[@id="root"]/div/div[1]/main/a[2]')
    log_in.click()
    login_result = Log_in_old(driver, email, password)
    print(login_result)
    return login_result


def send_message(driver, msg):
    print('now execute send_message.')
    print('msg: ' + str(msg))
    logging.info('you: ' + str(msg))
    inputfield = driver.find_element_by_xpath('//*[@id="send-message-textarea"]')
    try:
        time.sleep(1)
        while True:
            try:
                zh_send = baidu_translate_Chinese_to_English(str(msg))
                break
            except Exception as e:
                logging.info('1'+str(e))
                print(e)
        inputfield.send_keys(zh_send)
        inputfield.send_keys(Keys.ENTER)
    except Exception as e:
        print(e)
        logging.info('2'+str(e))


class Listener_Thread(threading.Thread):
    def __init__(self, driver):
        threading.Thread.__init__(self)
        logging.info('listener thread establish.')
        self.valid = 0
        self.flag = 1
        self.driver = driver
        self.clientsock = None

    def setClient(self,clientsock):
        self.clientsock = clientsock

    def clearClient(self):
        self.clientsock = None

    def setStop(self):
        self.flag = 0

    def setValid(self):
        self.valid = 1

    def getValid(self):
        return self.valid

    def clearValid(self):
        self.valid=0

    def getlog(self):
        return "chat.log"

    def run(self):
        global record_last, record_first
        first_flag = 0
        add_flag = 0
        chat_log = open(self.getlog(), 'a')
        while self.flag:
            #有效位为0，等待Operator将其置1
            if not self.valid:
                continue
            try:
                msg_last = self.driver.find_element_by_xpath(
                    '//*[@class="MessageGroup__MessageGroupRoot-h4dfhv-0 AwjZS"][last()]')
                if first_flag == 0:
                    record_first = msg_last
                    record_last = msg_last
                    first_flag = 1
                    continue
                if msg_last == record_last:
                    if msg_last == record_first:
                        continue
                    # 若遇到与上一次检查相同的元素，检查一次有无同框新消息
                    if add_flag == 0:
                        follow_message = 2
                        msg_text = ''
                        while True:
                            try:
                                msg_text_follow = msg_last.find_element_by_xpath(
                                    './div/div[' + str(follow_message) + ']/div[2]/div/span/span/span').text
                                print('your replika add: ' + str(msg_text_follow))
                                msg_text += msg_text_follow + "%%"
                                follow_message += 1
                                logging.info('Find a add message.')
                            except Exception as e:
                                logging.info('End of add message.')
                                add_flag = 1
                                # 有效位置0，说明信息已获取完成，可以让Operator发送下一条消息了
                                self.clearValid()
                                break
                        if msg_text != '':
                            zh_follow = baidu_translate_English_to_Chinese(msg_text.strip('%%'))
                            print(zh_follow)
                            chat_log.write( "replika: " + str(msg_text).replace("%%", ""))
                            chat_log.write(" 翻译：" + str(zh_follow).replace("%%", "") + "\n")
                            if self.clientsock:
                                self.clientsock.send(str(zh_follow).encode())
                                self.clearClient()
                            else:
                                logging.error('No clientsock.')
                else:
                    add_flag = 0
                    record_last = msg_last
                    msg_from_AI = msg_last.find_element_by_xpath('./div/div/div[2]/div/span/span/span').text
                    print('your replika: ' + str(msg_from_AI))
                    logging.info('your replika: ' + str(msg_from_AI))
                    zh_msg = baidu_translate_English_to_Chinese(str(msg_from_AI))
                    if zh_msg:
                        print(str(zh_msg))
                        chat_log.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +
                                       " replika: " + str(msg_from_AI) + " 翻译: " + str(zh_msg) + "\n")
                        if self.clientsock:
                            self.clientsock.send(str(zh_msg).encode())
                        else:
                            logging.error('No clientsock.')
                        # time_str = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                        # log.write(time_str + "AI: " + str(msg_from_AI) + " " + str(zh_msg))

            except Exception as e:
                print("unable to locate replika's last message.")
            time.sleep(3)
        logging.info("Listener Thread close.")
        chat_log.close()


def fetch_history(driver):
    global all_msg
    send = ''
    msg_to_fetch = fetch_num
    try_time = 3
    while try_time > 0:
        try:
            all_msg = driver.find_element_by_xpath('//*[@class="ChatMessagesList__ChatMessagesListInner-sc-1ajwmer-1 '
                                                   'lhAcwO"]')
            break
        except Exception as e:
            time.sleep(3)
            try_time -= 1
            if try_time == 0:
                raise Exception("can't find history messages")

    while msg_to_fetch >= 0:
        msg = all_msg.find_element_by_xpath('./div[last()-' + str(msg_to_fetch) + ']')
        who_speak = msg.get_attribute('class')

        msg_text = msg.find_element_by_xpath('./div/div/div[2]/div/span/span/span').text
        follow_message = 2
        while True:
            try:
                msg_text_follow = msg.find_element_by_xpath(
                    './div/div[' + str(follow_message) + ']/div[2]/div/span/span/span').text
                msg_text += "%%" + msg_text_follow
                follow_message += 1
            except Exception as e:
                break
        if who_speak == 'MessageGroup__MessageGroupRoot-h4dfhv-0 AwjZS':
            single = '2:' + msg_text + '|'
            send += single
        elif who_speak == 'MessageGroup__MessageGroupRoot-h4dfhv-0 imdLOh':
            single = '3:' + msg_text + '|'
            send += single
        else:
            raise Exception('fetch error.')
        msg_to_fetch -= 1
    zh_send = baidu_translate_English_to_Chinese(str(send))
    # 处理翻译结果
    zh_list = list(zh_send)
    for i, x in enumerate(zh_list):
        if x == '|' and i != len(zh_list) - 1 and zh_list[i + 1] != ' ':
            zh_list.insert(i + 1, ' ')
    zh_send_after = ''.join(zh_list)
    print(str(zh_send_after))
    return zh_send_after


def save_history(driver):
    global all_msg
    chat_record = open(FILE_NAME, "a")
    msg_to_save = save_num
    try_time = 3
    while try_time > 0:
        try:
            all_msg = driver.find_element_by_xpath('//*[@class="ChatMessagesList__ChatMessagesListInner-sc-1ajwmer-1 '
                                                   'lhAcwO"]')
            break
        except Exception as e:
            time.sleep(3)
            try_time -= 1
            if try_time == 0:
                raise Exception("can't find history messages")

    while msg_to_save >= 0:
        msg = all_msg.find_element_by_xpath('./div[last()-' + str(msg_to_save) + ']')
        follow_message = 1
        while True:
            try:
                msg_text_follow = msg.find_element_by_xpath(
                    './div/div[' + str(follow_message) + ']/div[2]').get_attribute('aria-label')
                while True:
                    try:
                        chat_record.write(str(msg_text_follow) + ' 翻译结果: ' + baidu_translate_English_to_Chinese(
                            str(msg_text_follow)) + '\r\n')
                        break
                    except Exception as e:
                        pass
                follow_message += 1
            except Exception as e:
                break
        msg_to_save -= 1
    chat_record.write('\r\n')
    chat_record.close()


def quit(driver):
    # display.stop()
    driver.quit()


def test():
    display = Display(visible=0, size=(1920, 1080))
    display.start()
    driver = webdriver.Firefox()
    driver.get('https://www.baidu.com')
    print(driver.title)
    driver.quit()
    display.stop()
