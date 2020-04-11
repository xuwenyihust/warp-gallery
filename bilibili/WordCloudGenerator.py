from typing import *
import requests
from bs4 import BeautifulSoup
from collections import Counter
import pandas as pd
import jieba
import matplotlib.pyplot as plt
import logging
from pyhocon import ConfigFactory
from wordcloud import WordCloud, ImageColorGenerator, random_color_func


class WordCloudGenerator(object):

    logging.basicConfig(level="INFO")

    def __init__(self):
        # load config
        auth = ConfigFactory.parse_file('auth.conf')
        self.sess_data = auth.get_string("sess_data")

        self.cid: str = '73417156'
        self.realtime_barrage_url = 'http://comment.bilibili.com/{}.xml'.format(self.cid)
        self.history_barrage_url = 'https://api.bilibili.com/x/v2/dm/history?type=1&oid={}&date=2020-04-02'.format(self.cid)
        # image related
        self.mask_image = 'resources/masks/bilibili_tv.jpg'
        self.font_path = '/System/Library/Fonts/STHeiti Light.ttc'
        self.background_color = 'white'
        self.max_words = 100000
        self.max_font_size = 45
        self.min_font_size = 5

    def get_history_barrages(self):
        cookies = {
            "SESSDATA": self.sess_data
        }
        # get xml
        html = requests.get(url=self.history_barrage_url, cookies=cookies).content
        html_data = str(html, 'utf-8')
        # parse xml
        soup = BeautifulSoup(html_data, 'lxml')
        results = soup.find_all('d')
        logging.info("Got totally {} barrages".format(len(results)))
        # extract barrages
        comments = [comment.text for comment in results]
        # save to csv
        df = pd.DataFrame(comments, columns=['comments'])
        file_name = 'resources/barrages/history_barrage_{}.csv'.format(self.cid)
        df.to_csv(file_name, encoding='utf-8')

    def get_realtime_barrages(self) -> List[str]:
        # get xml
        html = requests.get(self.realtime_barrage_url).content
        html_data = str(html, 'utf-8')
        # parse xml
        soup = BeautifulSoup(html_data, 'lxml')
        results = soup.find_all('d')
        logging.info("Got totally {} barrages".format(len(results)))
        # extract barrages
        comments = [comment.text for comment in results]
        # save to csv
        df = pd.DataFrame(comments, columns=['comments'])
        file_name = 'resources/barrages/realtime_barrage_{}.csv'.format(self.cid)
        df.to_csv(file_name, encoding='utf-8')
        return comments

    def clean_data(self, comments: List[str]) -> dict:
        dm_str = " ".join(comments)
        words_list = jieba.lcut(dm_str)
        words_map = Counter(words_list)
        return words_map

    def generate_graph(self, words_map: dict):
        background_image = plt.imread(self.mask_image)
        image_colors = ImageColorGenerator(background_image)

        wc = WordCloud(
            background_color=self.background_color,
            mask=background_image,
            font_path=self.font_path,
            max_words=self.max_words,
            max_font_size=self.max_font_size,
            min_font_size=self.min_font_size,
            color_func=image_colors,
            # color_func=random_color_func,
            random_state=50,
        )

        word_cloud = wc.generate_from_frequencies(words_map)
        word_cloud.to_file("outputs/word_cloud_{}.jpg".format(self.cid))

    def main(self):
        # comments = self.get_realtime_barrages()
        self.get_history_barrages()
        # words_str = self.clean_data(comments)
        # self.generate_graph(words_str)


if __name__ == '__main__':
    word_cloud_generator = WordCloudGenerator()
    word_cloud_generator.main()

