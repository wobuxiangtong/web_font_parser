from fontTools.misc.py23 import *
from fontTools.pens.basePen import BasePen
from reportlab.graphics.shapes import Path
import cv2 as cv
import os
import math
import numpy as np
import hashlib
import json
import random


# 存储font映射文件
def store(data, file):
    with open(file, 'w') as fw:
        json.dump(data, fw)


# 加载font映射文件
def load(file):
    with open(file, 'r') as f:
        data = json.load(f)
        return data


class ReportLabPen(BasePen):
    """画出字体"""

    def __init__(self, glyphSet, path=None):
        BasePen.__init__(self, glyphSet)
        if path is None:
            path = Path()
        self.path = path

    def _moveTo(self, p):
        (x, y) = p
        self.path.moveTo(x, y)

    def _lineTo(self, p):
        (x, y) = p
        self.path.lineTo(x, y)

    def _curveToOne(self, p1, p2, p3):
        (x1, y1) = p1
        (x2, y2) = p2
        (x3, y3) = p3
        self.path.curveTo(x1, y1, x2, y2, x3, y3)

    def _closePath(self):
        self.path.closePath()


class WebFontParser(object):
    def __init__(self):
        if not os.path.exists(os.path.join(os.path.abspath('.'), "web_font")):
            os.mkdir(os.path.join(os.path.abspath('.'), "web_font"))
            os.mkdir(os.path.join(os.path.abspath('.'), "web_font", "image"))
            os.mkdir(os.path.join(os.path.abspath('.'), "web_font", "json"))
        print("web font 相关文件放在 ",os.path.join(os.path.abspath('.'), "web_font"), " 文件夹")

    def _draw(self):
        """
        :param font_path: 下载的web 字体所在目录
        :param image_path: 转换为image后所在目录
        :return:返回font 对应的编码列表

        """
        import os
        import shutil

        shutil.rmtree(os.path.join(os.path.abspath('.'), "web_font", "image"))  # 能删除该文件夹和文件夹下所有文件
        os.mkdir(os.path.join(os.path.abspath('.'), "web_font", "image"))
        from fontTools.ttLib import TTFont
        from reportlab.lib import colors
        font = TTFont(os.path.join(os.path.abspath('.'), "web_font",
                                   "stonefont.woff"))  # it would work just as well with fontTools.t1Lib.T1Font
        gs = font.getGlyphSet()
        w, h = 40, 40
        keys = gs.keys()[2:]
        for glyphName in keys:
            pen = ReportLabPen(gs, Path(fillColor=colors.red, strokeWidth=0.01))
            imageFile = "%s.png" % glyphName
            g = gs[glyphName]
            g.draw(pen)
            from reportlab.graphics import renderPM
            from reportlab.graphics.shapes import Group, Drawing

            # Everything is wrapped in a group to allow transformations.
            g = Group(pen.path)
            g.translate(10, 13)
            g.scale(0.02, 0.02)
            d = Drawing(w, h)
            d.add(g)
            renderPM.drawToFile(d, os.path.join(os.path.abspath('.'), "web_font", "image", imageFile), fmt="PNG",
                                dpi=100)
        return keys

    def _merge(self, keys):
        """
        :param image_path: 字体图片所在目录
        :param merge_image_path: 合并后字体文件所在目录
        :return: 合并的图片数 也就是应该解析到的字符数 用于校验是否解析

        合并后因识别问题 加入最后一个字符作为冗余，识别后去掉
        """
        count = 0
        files = [key + ".png" for key in keys]
        files.append(files[-1])
        rows = 1
        cols = math.ceil(len(files) / rows)
        current_img = cv.imread(os.path.join(os.path.abspath('.'), "web_font", "image", files[0]))
        new_image = np.zeros([current_img.shape[0] * rows, current_img.shape[1] * cols, 3])
        new_image.fill(255)
        current_count = 0
        current_h = 0
        current_w = 0
        for file in files:
            count += 1
            current_img = cv.imread(os.path.join(os.path.abspath('.'), "web_font", "image", file))
            new_image[current_h * current_img.shape[0]:(current_h + 1) * current_img.shape[0],
            current_w * current_img.shape[1]:(current_w + 1) * current_img.shape[1], :] = current_img
            current_count += 1
            current_w += 1
            if current_count % cols == 0 and current_count != 0:
                current_w = 0
                current_h += 1
            cv.imwrite(os.path.join(os.path.abspath('.'), "web_font", "font_merge.jpg"), new_image)
        return count

    def _ocr(self):
        """
        :return: 返回识别到的文字列表
        """
        import subprocess
        _, _ = subprocess.getstatusoutput(
            'tesseract -l chi_sim+eng  %s %s' % (os.path.join(os.path.abspath('.'), "web_font", "font_merge.jpg"),
                                                 os.path.join(os.path.abspath('.'), "web_font", "result")))
        with open(os.path.join(os.path.abspath('.'), "web_font", "result.txt"), "r") as f:
            text = f.read()
            return [i for i in text.split(" ") if i != ""][:-1]

    def parse(self, unique_id = "uni", limit_count=30, check_count=4):
        """
        解析 font 文件
        1. 绘制 font 图片
        2. 合并 font 图片 为一张图片
        3. 识别图片中文字


        :param unique_id: 可以生成解析文件并用于索引的唯一ID
        :param limit_count: 尝试的最大次数
        :param check_count: 检查结果次数
        :return: 解析结果
        """
        parse_file_name = hashlib.md5(b'%s' % unique_id).hexdigest()
        if os.path.exists(os.path.join(os.path.abspath('.'), "web_font", "json", parse_file_name + ".json")):
            data = load(os.path.join(os.path.abspath('.'), "web_font", "json", parse_file_name + ".json"))
            print("parse from file: ",
                  os.path.join(os.path.abspath('.'), "web_font", "json", parse_file_name + ".json"))
            return data
        else:
            print("解析到新文件: ",os.path.join(os.path.abspath('.'), "web_font", "json", parse_file_name + ".json"))
            result_list = []
            parse_count = 0
            while True:
                font_encode_list = self._draw()
                random.shuffle(font_encode_list)
                self._merge(font_encode_list)
                word_list = self._ocr()
                if len(font_encode_list) != len(word_list):
                    print("解析错误，正在重新解析...")
                else:
                    result_list.append(dict(zip(font_encode_list, word_list)))
                    if len(result_list) != 1:
                        if result_list[-1] != result_list[-2]:
                            result_list = []

                if len(result_list) == check_count:
                    break
                parse_count += 1
                if parse_count >= limit_count:
                    print("解析失败...")
                    return {}

            print("parse from model...")
            store(result_list[0], os.path.join(os.path.abspath('.'), "web_font", "json", parse_file_name + ".json"))
            return result_list[0]

    def font_store(self, data):
        """
        转储 woff 格式文件
        :param data: font文件内容
        :return:
        """
        with open(os.path.join(os.path.abspath('.'), "web_font",
                               "stonefont.woff"), 'wb') as f:
            f.write(data)

if __name__ == '__main__':
    fontParse = WebFontParser()
    fontParse.parse(b"ddd")
