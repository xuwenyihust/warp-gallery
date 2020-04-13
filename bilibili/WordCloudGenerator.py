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


class WordCloudGenerator(object):

    logging.basicConfig(level="INFO")

    def __init__(self):
        logging.info("Initializing WordCloudGenerator.")
        # load config
        auth = ConfigFactory.parse_file('auth.conf')
        self.sess_data = auth.get_string("sess_data")

        # url
        self.barrage_url_base = 'http://comment.bilibili.com/{}.xml'

        # file path
        self.stopwords = "stopwords.txt"
        self.bilibili_meaninglesswords = "bilibili_meaninglesswords.txt"
        self.barrages_dir = "resources/barrages"
        self.barrages_by_uid_file = "barrage_by_uid_{}"
        self.barrages_by_cid_file = "barrage_by_cid_{}"

        # image
        self.font_path = '/System/Library/Fonts/STHeiti Light.ttc'
        self.background_color = 'white'
        self.max_words = 100000
        self.max_font_size = 400
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

    def clean_data(self, comments: List[str]) -> dict:
        stopwords = [line.strip() for line in open(self.stopwords, 'r', encoding='utf-8').readlines()]
        bilibili_meaninglesswords = [line.strip() for line in
                                     open(self.bilibili_meaninglesswords, 'r', encoding='utf-8').readlines()]
        dm_str = " ".join(comments)
        words_list = jieba.lcut(dm_str)
        words_map = Counter(words_list)
        for word in stopwords + bilibili_meaninglesswords:
            if word in words_map:
                del words_map[word]
        logging.info("Data cleaned.")
        return words_map

    def get_barrages_by_uid(self, uid: int, videos: List[dict]) -> None:
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
        file_name = (self.barrages_dir + self.barrages_by_uid_file).format(uid)
        df.to_csv(file_name, encoding='utf-8')

    def get_barrages_by_cid(self, cid: str, save_to_file: bool = False) -> List[str]:
        realtime_barrage_url = self.barrage_url_base.format(cid)
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
            file_name = (self.barrages_dir + self.barrages_by_cid_file).format(cid)
            df.to_csv(file_name, encoding='utf-8')
            logging.info("Barrages saved to file: {}".format(file_name))
        else:
            logging.info("Skipped save to file.")
        return comments

    def generate_graph_from_file(self, file_path: str, uid: str, mask_file_path: str) -> None:
        try:
            df = pd.read_csv(file_path, sep=",", usecols=["text"])
            barrages = df["text"].values.tolist()
            barrages_map = self.clean_data(barrages)
            self.generate_graph_from_map(barrages_map, uid, mask_file_path)
        except Exception as e:
            logging.error("Failed to open {}: ".format(file_path) + str(e))

    def generate_graph_from_map(self, words_map: dict, uid: str, mask_file_path: str) -> None:
        background_image = plt.imread(mask_file_path)
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
        logging.info("Graph generated.")
