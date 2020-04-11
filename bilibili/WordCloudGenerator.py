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
from bilibili_api import video
from bilibili_api.user import UserInfo
from bilibili.UserInfo import user_info_map


class WordCloudGenerator(object):

    logging.basicConfig(level="INFO")

    def __init__(self):
        # load config
        auth = ConfigFactory.parse_file('auth.conf')
        self.sess_data = auth.get_string("sess_data")

        self.cid: str = '73417156'
        # image related
        self.mask_image = 'resources/masks/bilibili_tv.jpg'
        self.font_path = '/System/Library/Fonts/STHeiti Light.ttc'
        self.background_color = 'white'
        self.max_words = 100000
        self.max_font_size = 200
        self.min_font_size = 10

    @staticmethod
    def get_videos_by_user(uid: int) -> List[dict]:
        user = UserInfo(uid=uid)
        info = user.get_info()
        logging.info("Got information of user: {}".format(info['name']))
        videos = user.get_video()
        logging.info("Got {} videos of user {}".format(len(videos), info['name']))
        videos = sorted(videos, key=lambda x: x["play"], reverse=True)
        return videos

    def get_history_barrages_by_cid(self, cid: str, date: str, save_to_file: bool = False):
        history_barrage_url = 'https://api.bilibili.com/x/v2/dm/history?type=1&oid={}&date={}'.format(cid, date)
        cookies = {
            "SESSDATA": self.sess_data
        }
        # get xml
        html = requests.get(url=history_barrage_url, cookies=cookies).content
        html_data = str(html, 'utf-8')
        # parse xml
        soup = BeautifulSoup(html_data, 'lxml')
        results = soup.find_all('d')
        logging.info("Got totally {} barrages".format(len(results)))
        # extract barrages
        comments = [comment.text for comment in results]
        # save to csv
        if save_to_file:
            df = pd.DataFrame(comments, columns=['comments'])
            file_name = 'resources/barrages/history_barrage_{}_{}.csv'.format(date, cid)
            df.to_csv(file_name, encoding='utf-8')
            logging.info("Barrages saved to file: {}".format(file_name))
        else:
            logging.info("Skipped save to file.")
        return comments

    @staticmethod
    def get_realtime_barrages_by_uid(uid: int, videos: List[dict]) -> None:
        aids = [x["aid"] for x in videos]
        barrages = []

        for aid in aids:
            video_info = video.VideoInfo(aid=aid)
            danmuku = video_info.get_danmaku(page=0)
            danmuku_text = [x.text for x in danmuku]
            barrages.extend(danmuku_text)
            logging.info("Got {} barrages from {}".format(len(danmuku), video_info.get_video_info()))
        # save to file
        df = pd.DataFrame(barrages, columns=['text'])
        file_name = 'resources/barrages/realtime_barrage_by_user_{}.csv'.format(uid)
        df.to_csv(file_name, encoding='utf-8')

    @staticmethod
    def get_realtime_barrages_by_cid(cid: str, save_to_file: bool = False) -> List[str]:
        realtime_barrage_url = 'http://comment.bilibili.com/{}.xml'.format(cid)
        # get xml
        html = requests.get(realtime_barrage_url).content
        html_data = str(html, 'utf-8')
        # parse xml
        soup = BeautifulSoup(html_data, 'lxml')
        results = soup.find_all('d')
        logging.info("Got totally {} barrages".format(len(results)))
        # extract barrages
        comments = [comment.text for comment in results]
        # save to csv
        if save_to_file:
            df = pd.DataFrame(comments, columns=['comments'])
            file_name = 'resources/barrages/realtime_barrage_{}.csv'.format(cid)
            df.to_csv(file_name, encoding='utf-8')
            logging.info("Barrages saved to file: {}".format(file_name))
        else:
            logging.info("Skipped save to file.")
        return comments

    @staticmethod
    def clean_data(comments: List[str]) -> dict:
        stopwords = [line.strip() for line in open("stopwords.txt", 'r', encoding='utf-8').readlines()]
        bilibili_meaninglesswords = [line.strip() for line in open("bilibili_meaninglesswords.txt", 'r', encoding='utf-8').readlines()]
        dm_str = " ".join(comments)
        words_list = jieba.lcut(dm_str)
        words_map = Counter(words_list)
        for word in stopwords + bilibili_meaninglesswords:
            if word in words_map:
                del words_map[word]
        return words_map

    def generate_graph_from_file(self, file_path: str, uid: str) -> None:
        try:
            df = pd.read_csv(file_path, sep=",", usecols=["text"])
            barrages = df["text"].values.tolist()
            barrages_map = self.clean_data(barrages)
            self.generate_graph_from_map(barrages_map, uid)
        except Exception as e:
            logging.error("Failed to open {}: ".format(file_path) + str(e))

    def generate_graph_from_map(self, words_map: dict, uid: str) -> None:
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
        word_cloud.to_file("outputs/word_cloud_{}.jpg".format(uid))

    def main(self):
        # comments = self.get_history_barrages(self.cid, '2020-04-03')
        # comments = self.get_realtime_barrages(self.cid)
        # words_str = self.clean_data(comments)
        # self.generate_graph(words_str)

        uid = user_info_map["media_storm"]["mid"]

        # videos = self.get_videos_by_user(uid)
        # self.get_realtime_barrages_by_uid(uid, videos)

        barrages_file_path = 'resources/barrages/realtime_barrage_by_user_{}.csv'.format(uid)
        self.generate_graph_from_file(barrages_file_path, uid)


if __name__ == '__main__':
    word_cloud_generator = WordCloudGenerator()
    word_cloud_generator.main()

