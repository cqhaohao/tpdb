from flask import jsonify, current_app
from flask_restful import Resource, reqparse
from api.settings import APP_IMAGE_FILES
from skimage.metrics import structural_similarity
from PIL import Image
import os
import json
import base64
import numpy as np
import imutils
import cv2
import werkzeug


class ImageView(Resource):
    """
    计算图片差异接口
    [post]
        @param: bfirstImg: 第一张图片base64字符串
        @param: bsecondImg: 第二张图片base64字符串
    """
    parser = reqparse.RequestParser()
    parser.add_argument('bfirstImg', type=str, required=True, help='图1 base64字符串')
    parser.add_argument('bsecondImg', type=str, required=True, help='图2 base64字符串')

    def judge(self, *path_list):
        isNormal = True
        for file_path in path_list:
            try:
                Image.open(file_path).verify()
            except:
                isNormal = False
        return isNormal

    def compare(self, first, second, square_path, fill_path):
        # first和second: 图片文件路径
        imageA = cv2.imread(first)
        imageB = cv2.imread(second)

        grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

        # 计算两个灰度图像之间的结构相似度指数
        (score, diff) = structural_similarity(grayA, grayB, full=True)
        diff = (diff * 255).astype("uint8")
        print("SSIM:{}".format(score))

        # 找到不同点的轮廓以致于我们可以在被标识为“不同”的区域周围放置矩形
        thresh = cv2.threshold(diff, 100, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        # 设置遮罩和填充区域
        mask = np.zeros(imageA.shape, dtype='uint8')
        filled_after = imageB.copy()

        # 找到一系列区域，在区域周围放置矩形
        for c in cnts:
            area = cv2.contourArea(c)
            if area > 200:  # 差异明显的区域才进行绘制
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(imageA, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.rectangle(imageB, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.drawContours(mask, [c], 0, (0, 255, 0), -1)
                cv2.drawContours(filled_after, [c], 0, (0, 255, 0), -1)

        # 用cv2.imshow 展现最终对比之后的图片， cv2.imwrite 保存最终的结果图片
        # cv2.imshow("diff1", imageA)
        # cv2.imshow("diff2", imageB)
        # cv2.imshow('mask',mask)
        # cv2.imshow('filled after', filled_after)

        # 采用框选或者填充的方式来标绘图像差异
        boolA = cv2.imwrite(square_path, imageB)
        boolB = cv2.imwrite(fill_path, filled_after)
        return score, (boolA and boolB)

    def post(self):
        """图片对比
        ---
        consumes:
          - application/json
        parameters:
          - name: body
            in: body
            schema:
              id: data
              required:
                - bfirstImg
                - bsecondImg
              properties:
                bfirstImg: 
                  type: string
                  description: base64 格式的图片必传参数 字符串
                bsecondImg: 
                  type: string
                  description: base64 格式的图片必传参数 字符串
        responses:
          200:
            description: json 格式数据
            examples:
              data: {
                'code': '200',
                'ssim': '0.98238423',
                'squareImg': "base64格式的字符串",
                'fillImg': "base64格式的字符串",
              }
          400:
            description: 请求错误
          500:
            description: 服务错误, 图片对比算法失败
        """
        args = self.parser.parse_args()
        bfirstImg = args.get('bfirstImg')
        bsecondImg = args.get('bsecondImg')
        if not bfirstImg or not bsecondImg:
            return {
                'code': '400',
                'error': '必传参数不可为空'
            }, 400

        try:
            firstImg = base64.b64decode(bfirstImg)
            secondImg = base64.b64decode(bsecondImg)
        except:
            # current_app.logger.info('字符串转化错误: {}'.format(e))
            return {
                'code': '400',
                'error': '非法参数, 参数无法进行 base64 编码'
            }, 400

        img_1_path = os.path.join(APP_IMAGE_FILES, '1.jpg')
        img_2_path = os.path.join(APP_IMAGE_FILES, '2.jpg')
        img_square_path = os.path.join(APP_IMAGE_FILES, 'square.jpg')
        img_fill_path = os.path.join(APP_IMAGE_FILES, 'fill.jpg')
        with open(img_1_path, 'wb') as file:
            file.write(firstImg)
        with open(img_2_path, 'wb') as file:
            file.write(secondImg)

        is_normal_picture = self.judge(img_1_path, img_2_path)
        if not is_normal_picture:
            return {
                'code': '400',
                'error': '非法参数, 参数无法转化为图片格式'
            }, 400

        try:
            (ssim, bool) = self.compare(img_1_path, img_2_path, img_square_path, img_fill_path)
        except Exception as e:
            current_app.logger.info('图片对比错误: {}'.format(e))

        if not bool:
            return {
                'code': '500',
                'error': '服务错误, 图片对比失败'
            }, 500

        with open(img_square_path, 'rb') as file:
            res = file.read()
            square_result = base64.b64encode(res)

        with open(img_fill_path, 'rb') as file:
            res = file.read()
            fill_result = base64.b64encode(res)

        return {
            'code': '200',
            'ssim': '{}'.format(ssim),
            'squareImg': square_result.decode("utf-8"),
            'fillImg': fill_result.decode("utf-8"),
        }


class Picture(Resource):
    """
    图片转化 base64
    """
    parser = reqparse.RequestParser()
    parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files', required=True, help='文件')

    def post(self):
        args = self.parser.parse_args()
        file = args.get('file')
        file_path = os.path.join(APP_IMAGE_FILES, 'basedemo.png')
        file.save(file_path)

        with open(file_path, 'rb') as file:
            res = base64.b64encode(file.read())

        return res.decode('utf-8')
