import json
import random
from urllib import parse  # 对文本进行 url encode 再拼接到 url_full 中
from hashlib import md5  # 生成url的签名
from http.client import HTTPConnection
from flask import current_app
from flask_babel import _

url_head = '/api/trans/vip/translate'


def translate(text_query, src_lang, dst_lang):
    if 'FANYI_APP_ID' not in current_app.config or not current_app.config['FANYI_APP_ID']:
        return _('Error: The translation service is not configured.')

    app_id = current_app.config['FANYI_APP_ID']
    secret_key = current_app.config['FANYI_SECRET_KEY']
    salt = random.randint(32768, 65536)  # 生成url签名所需的随机数
    sign_str = app_id + text_query + str(salt) + secret_key  # 按照 appid+q+salt+密钥 的顺序拼接得到字符串
    sign = md5(sign_str.encode()).hexdigest()  # 对字符串做md5，得到32位小写的sign
    url_full = url_head + '?appid=' + app_id + '&q=' + parse.quote(text_query) \
               + '&from=' + src_lang + '&to=' + dst_lang + '&salt=' + str(salt) + '&sign=' + sign

    httpClient = None
    try:
        httpClient = HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', url_full)

        # response是HTTPResponse对象
        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)

        # print(result)
        # print(result['trans_result'][0]['dst'])
        return result['trans_result'][0]['dst']

    except Exception as e:
        raise e
    finally:
        if httpClient:
            httpClient.close()
