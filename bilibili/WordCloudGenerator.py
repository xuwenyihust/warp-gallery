from typing import *
import requests
from bs4 import BeautifulSoup
import pandas as pd
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator, random_color_func


class WordCloudGenerator(object):

    def __init__(self):
        self.cid: str = '73417156'
        self.url = 'http://comment.bilibili.com/{}.xml'.format(self.cid)
        # image related
        self.mask_image = 'resources/masks/film.jpg'
        self.font_path = '/System/Library/Fonts/STHeiti Light.ttc'
        self.background_color = 'white'
        self.max_words = 2000
        self.max_font_size = 45
        self.min_font_size = 5

    def get_barrages(self) -> List[str]:
        html = requests.get(self.url).content
        html_data = str(html, 'utf-8')
        soup = BeautifulSoup(html_data, 'lxml')
        results = soup.find_all('d')
        comments = [comment.text for comment in results]
        # save to csv
        df = pd.DataFrame(comments, columns=['comments'])
        file_name = 'resources/barrages/barrage_{}.csv'.format(self.cid)
        df.to_csv(file_name, encoding='utf-8')
        return comments

    def generate_graph(self, comments: List[str]):
        dm_str = " ".join(comments)
        words_list = jieba.lcut(dm_str)  # 切分的是字符串,返回的是列表
        words_str = " ".join(words_list)

        background_image = plt.imread(self.mask_image)

        wc = WordCloud(
            background_color=self.background_color,
            mask=background_image,
            font_path=self.font_path,
            max_words=self.max_words,
            max_font_size=self.max_font_size,
            min_font_size=self.min_font_size,
            color_func=random_color_func,
            random_state=50,
        )

        word_cloud = wc.generate(words_str)  # 产生词云
        word_cloud.to_file("outputs/word_cloud_{}.jpg".format(self.cid))  # 保存图片

    def main(self):
        comments = self.get_barrages()
        self.generate_graph(comments)


if __name__ == '__main__':
    word_cloud_generator = WordCloudGenerator()
    word_cloud_generator.main()

