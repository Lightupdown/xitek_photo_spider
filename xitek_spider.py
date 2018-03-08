#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__  = ''
__author__ = 'zhang'
__mtime__  = '2017/12/1'

              ┏┓      ┏┓
            ┏┛┻━━━┛┻┓
            ┃      ☃      ┃
            ┃  ┳┛  ┗┳  ┃
            ┃      ┻      ┃
            ┗━┓      ┏━┛
                ┃      ┗━━━┓
                ┃  神兽保佑    ┣┓
                ┃　永无BUG！   ┏┛
                ┗┓┓┏━┳┓┏┛
                  ┃┫┫  ┃┫┫
                  ┗┻┛  ┗┻┛
"""
import re

import time

import os
from lxml import etree
from xitek_photo_spider.log_conf import setup_logging

import logging
import requests


URL = 'http://photo.xitek.com'

'''style: 
    0  获奖作品
    1  推荐作品
    2  平图论坛
    3  最新作品
    4  无忌月赛
    5  TOP48评比区
    6  全部作品
'''
style = 6  # 根据你需要的类型填

'''pc:
    0  不限
    1  自然风光
    2  建筑
    3  人像
    4  民俗
    5  纪实与抓拍
    6  动物
    7  昆虫
    8  花卉
    9  微距
    10 静物与小品
    11 旅游
    12 商业
    13 运动
    14 暗房
    15 PS制作
    16 其他类别
    17 体育与新闻纪实
    18 风光建筑
    19 人物肖像
    20 微距世界
    21 创意视角
    22 户外
    23 风光
    24 探险
    25 极限
'''
pc = 3   # 根据你的需要填

# p_start = 1   # 开始的页数
# p_stop = 20   # 结束的页数，填0则全部下载直到没有图片

PATH = os.path.join(os.path.abspath('.'), 'photo')
SAVE_PATH = os.path.join(PATH, '获奖作品-人像')  # 根据你的选择换成相应的名词
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)


def get_image_url(url, p_start=1, p_stop=20):
    if p_start > p_stop:
        logging.error('开始页数[%d]不能大于结束页数[%d]' % (p_start, p_stop))
        return
    while p_start <= p_stop:
        url_get = '/'.join([URL, 'style', str(style), 'pc', str(pc), 'p', str(p_start)])
        logging.info('即将下载的地址： %s' % url_get)
        time.sleep(2)
        html_content1 = requests.get(url_get).content.decode('utf-8')
        # logging.debug(html_content1)

        seletor1 = etree.HTML(html_content1)

        photo_page_url_s = seletor1.xpath("//div[@id='container']/div[@class='element']/a[1]/@href")
        if p_stop == 0:
            photo_page_num_list = seletor1.xpath("//div[@id='page']/text()")
            photo_page_num_str = photo_page_num_list.encode('utf-8')
            try:
                p_stop = re.match(r'[\u4e00-\u9fa5]\s\d*\s[\u4e00-\u9fa5]\s[\u4e00-\u9fa5]\s(\d*)\s[\u4e00-\u9fa5]',
                                  photo_page_num_str).group(1)
            except:
                p_stop = 1

        re_photo_page = re.compile(r'(\/photoid\/\d*)')

        # 获得图片所处的url
        photo_page_list = []
        # 图片的url和命名
        photo = {'url': '', 'alt': ''}
        photo_url_alt = []

        for photo_page_url in photo_page_url_s:
            try:
                photo_page = re_photo_page.match(photo_page_url).group(1)
            except Exception as e:
                logging.info('出现一个小广告： %s' % e)
                continue
            # photo_page_list.append(photo_page)
            logging.info('photo_page: %s' % str(photo_page))
            # 打开每个url来获得图片的下载地址
            time.sleep(1)
            html_content2 = requests.get(URL + photo_page).content.decode('utf-8')
            print('url: ', URL + photo_page)
            # logging.debug(html_content2)
            seletor2 = etree.HTML(html_content2)
            photo_url_infos = seletor2.xpath("//div[@id='group_photo']//div[@class='group_pic']/div[1]/img[1]")
            flag = 0
            for photo_url_info in photo_url_infos:
                flag += 1
                photo_url = photo_url_info.xpath('@src')
                photo['url'] = photo_url[0]
                logging.info('photo_url: %s' % photo['url'])

                photo_alt = photo_url_info.xpath('@alt')
                photo['alt'] = str(photo_alt[0]).replace(':', '-') + str(flag)
                logging.info('photo_alt: %s' % photo['alt'])

                photo_copy = photo.copy()       # copy后再赋值否则添加的是原列表的地址
                photo_url_alt.append(photo_copy)
                logging.info(str(photo_url_alt[:]))
            # print('photo_page_list: ', photo_page_list[:])

            for img in photo_url_alt:
                # print(img['url'], img['alt'])
                image_download(img['url'], img['alt'])
        p_start += 1


def image_download(image_url, image_alt):
    response = requests.get(image_url, stream=True)
    image = response.content
    try:
        # print(image_alt)
        img_path = os.path.join(SAVE_PATH, image_alt + '.jpg')
        logging.info('正在保存图片：%s' % img_path)
        with open(img_path, "wb") as image_object:
            image_object.write(image)
            return
    except IOError:
        print("IO Error\n")
        return


def main():
    # url_get = '/'.join([URL, 'style', str(style), 'pc', str(pc), 'p', str(p_start)])

    get_image_url(URL)


if __name__ == '__main__':
    setup_logging()
    main()
