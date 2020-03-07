import json
import random
from urllib import parse  # 对文本进行 url encode 再拼接到 url_full 中
from hashlib import md5  # 生成url的签名
from http.client import HTTPConnection
from flask import current_app
from flask_babel import _

url_head = '/api/trans/vip/translate'


def translate(text_query, src_lang, dst_lang):
    """返回翻译结果"""
    if 'FANYI_APP_ID' not in current_app.config or not current_app.config['FANYI_APP_ID']:
        return _('Error: The translation service is not configured.')

    # 语言检测结果和百度翻译语言列表不一致处理
    lang_list = current_app.config['LANG_LIST']
    diff = current_app.config['LANG_DIFF']
    if src_lang in diff.keys():
        src_lang = diff.get(src_lang)
    elif src_lang not in lang_list:
        src_lang = 'auto'
    if dst_lang in diff.keys():  # zh-cn 要换成 zh，啊，耗了我一个下午的时间！
        dst_lang = diff.get(dst_lang)
    else:
        dst_lang = 'zh'

    # 拼接翻译 API
    app_id = current_app.config['FANYI_APP_ID']
    secret_key = current_app.config['FANYI_SECRET_KEY']
    salt = random.randint(32768, 65536)  # 生成url签名所需的随机数
    sign_str = app_id + text_query + str(salt) + secret_key  # 按照 appid+q+salt+密钥 的顺序拼接得到字符串
    sign = md5(sign_str.encode()).hexdigest()  # 对字符串做md5，得到32位小写的sign
    # 拼接完整的百度翻译api:
    url_full = '{}?appid={}&q={}&from={}&to={}&salt={}&sign={}'.format(url_head, app_id, parse.quote(text_query),
                                                                       src_lang, dst_lang, str(salt), sign)

    httpClient = None
    try:
        httpClient = HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', url_full)

        # response是HTTPResponse对象
        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")  # 返回json格式的翻译结果
        result = json.loads(result_all)

        # print(result['trans_result'][0]['dst'])
        if 'trans_result' in result:
            dst_result = result['trans_result'][0]['dst']
            return dst_result
        else:
            return 'unknown_lang'

    except Exception as e:
        raise e
    finally:
        if httpClient:
            httpClient.close()
