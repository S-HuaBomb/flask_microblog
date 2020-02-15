# 百度通用翻译API,不包含词典、tts语音合成等资源，如有相关需求请联系translate_api@baidu.com
# coding=utf-8

import http.client
import hashlib
import urllib.parse as parse
import random
import json
from app import app1

appid = app1.config['FANYI_APP_ID']  # 填写你的appid
secretKey = app1.config['FANYI_SECRET_KEY']  # 填写你的密钥

httpClient = None
myurl = '/api/trans/vip/translate'

fromLang = 'auto'  # 原文语种
toLang = 'en'  # 译文语种
salt = random.randint(32768, 65536)
q = '你想要一个苹果吗？去你妈的！'
sign = appid + q + str(salt) + secretKey
sign = hashlib.md5(sign.encode()).hexdigest()
translate_url = myurl + '?appid=' + appid + '&q=' + parse.quote(q) \
                + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign

try:
    httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
    httpClient.request('GET', translate_url)

    # response是HTTPResponse对象
    response = httpClient.getresponse()
    result_all = response.read().decode("utf-8")
    result = json.loads(result_all)

    print(result)
    print(result['trans_result'][0]['dst'])

except Exception as e:
    print(e)
finally:
    if httpClient:
        httpClient.close()
