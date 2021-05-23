import http.client
import hashlib
import json
import urllib
import random

import time


def baidu_translate_Chinese_to_English(content):
    appid = '20210430000809750'
    secretKey = 'tuHqcPcqSXJgVdsWS4Pk'
    httpClient = None
    myurl = '/api/trans/vip/translate'
    q = content
    fromLang = 'zh'  # 源语言
    toLang = 'en'  # 翻译后的语言
    salt = random.randint(32768, 65536)
    sign = appid + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
        q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign

    # try:
    httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
    httpClient.request('GET', myurl)
    # response是HTTPResponse对象
    response = httpClient.getresponse()
    jsonResponse = response.read().decode("utf-8")  # 获得返回的结果，结果为json格式
    js = json.loads(jsonResponse)  # 将json格式的结果转换字典结构
    time.sleep(2)
    dst = str(js["trans_result"][0]["dst"])  # 取得翻译后的文本结果
    print(dst)  # 打印结果
    return dst
    # except Exception as e:
    #     print('err:' + str(e))
    # finally:
    #     if httpClient:
    #         httpClient.close()

def baidu_translate_English_to_Chinese(content):
    appid = '20210430000809750'
    secretKey = 'tuHqcPcqSXJgVdsWS4Pk'
    httpClient = None
    myurl = '/api/trans/vip/translate'
    q = content
    fromLang = 'en'  # 源语言
    toLang = 'zh'  # 翻译后的语言
    salt = random.randint(32768, 65536)
    sign = appid + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
        q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)
        # response是HTTPResponse对象
        response = httpClient.getresponse()
        jsonResponse = response.read().decode("utf-8")  # 获得返回的结果，结果为json格式
        js = json.loads(jsonResponse)  # 将json格式的结果转换字典结构
        time.sleep(2)
        dst = str(js["trans_result"][0]["dst"])  # 取得翻译后的文本结果
        return dst
    except Exception as e:
        print('err:' + str(e))
    finally:
        if httpClient:
            httpClient.close()


# def writeToTxt(list_name, file_path):
#     try:
#         # 这里把翻译结果写入txt
#         fp = open(file_path, "a+", encoding='utf-8')
#         l = len(list_name)
#         i = 0
#         # fp.write('[')
#         for item in list_name:
#             fp.write(str(item))
#             if i < l:
#                 fp.write(',\n')
#             i += 1
#         # fp.write(']')
#         fp.close()
#     except IOError:
#         print("fail to open file")
#
#
# def openfile(fileinput):
#     list = []  ## 空列表
#     # count=1
#     with open(fileinput, "r", encoding='utf-8') as fl:
#         for line in fl.readlines():
#             # print(line)
#             # l=len(line)
#             # print(line[l-3:l-1])
#             # dst='hello world'
#             if line.strip() == '':  # 跳过空行 isspace
#                 print('string is null')
#                 continue
#
#             dst = baidu_translate(line)
#             list.append(dst)
#             time.sleep(2)  # 不要频繁访问百度翻译，睡2秒
#         # count+=1
#         # str='\"'+line[0:l-2]+'\" = \"'+dst+'\"\n'
#         # print(str)
#         # if count==4:
#         #	break
#     # print(list)
#     fileout = r"f:\Users\Desktop\翻译\iOS\dst.txt"
#     writeToTxt(list, fileout)
#
#
# # translate('不能连接到应用服务器')
# # baidu_translate()
# file = r""
# openfile(file)  # 输入文件路径
