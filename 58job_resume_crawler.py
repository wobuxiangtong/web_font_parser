"""
测试 font_parser
抓取字体 文件为 woff 格式
"""

from bs4 import BeautifulSoup
import hashlib
import requests
import re
import base64
from font_parser import WebFontParser

webFontParser = WebFontParser()

crawler_address_list = [
    ("义乌", "yiwu.58.com"),
    ("浦江", "jh.58.com/pujiang"),
    ("金华", "jh.58.com"),
    ("东阳", "dongyang.58.com"),
    ("慈溪", "cixi.58.com"),
    ("余姚", "yuyao.58.com")
]

hl = hashlib.md5()
hl.update("123456".encode(encoding='utf-8'))
password = hl.hexdigest()

# 58同城分类接口
for crawler_address_key, crawler_address_value in crawler_address_list:
    r_1 = requests.get(
        'https://api.58.com/comm/cate/?api_type=json&api_pid=9225')
    for category_1 in r_1.json()["comms_getcatelist"]:
        category_1_name = category_1["cateName"]
        r_2 = requests.get(
            'https://api.58.com/comm/cate/?api_type=json&api_pid=%d' % category_1["dispCategoryID"])
        for category_2 in r_2.json()["comms_getcatelist"]:
            category_2_name = category_2["cateName"]
            page_count = 0
            while True:
                page_count += 1
                r_3 = requests.get("https://%s/%s/pn%d/" %
                                   (crawler_address_value, category_2["catelist"], page_count))
                if "firewall" in r_3.url:
                    print(r_3.url)
                    print("58验证码" * 30)
                    exit()

                base64Font = re.findall(r'src:url\((.*?)\)', r_3.text)
                base64Font = base64Font[0].split(',')[-1].encode()
                font = base64.decodebytes(base64Font)

                webFontParser.font_store(font)
                font_parser_dict = webFontParser.parse(base64Font)

                soup_1 = BeautifulSoup(r_3.text.replace("&#x", "uni"))

                for user in soup_1.select(".infocardLi"):
                    for stone in user.select(".stonefont"):
                        stone_text = stone.get_text()
                        for k, v in font_parser_dict.items():
                            stone_text = stone_text.strip().replace(k.lower(), v)
                        print(stone_text.replace(";", ""))
                print("https://%s/%s/pn%d/" %
                      (crawler_address_value, category_2["catelist"], page_count), "-->")
                if page_count >= 30:
                    break
