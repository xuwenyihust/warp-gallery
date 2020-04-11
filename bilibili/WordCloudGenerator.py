import requests
from bs4 import BeautifulSoup
import pandas as pd
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator


class WordCloudGenerator(object):

    def __init__(self):
        self.cid: str = '73417156'
        self.url = 'http://comment.bilibili.com/{}.xml'.format(self.cid)

    def main(self):
        html = requests.get(self.url).content
        html_data = str(html, 'utf-8')
        soup = BeautifulSoup(html_data, 'lxml')
        results = soup.find_all('d')
        comments = [comment.text for comment in results]
        # save to csv
        df = pd.DataFrame(comments, columns=['comments'])
        file_name = 'resources/barrages/barrage_{}.csv'.format(self.cid)
        df.to_csv(file_name, encoding='utf-8')

        dm_str = " ".join(comments)
        words_list = jieba.lcut(dm_str)  # 切分的是字符串,返回的是列表
        words_str = " ".join(words_list)

        backgroud_Image = plt.imread('resources/masks/film.jpg')

        wc = WordCloud(
            background_color='white',
            mask=backgroud_Image,
            font_path='/System/Library/Fonts/STHeiti Light.ttc',  # 设置本地字体
            max_words=20000,
            max_font_size=50,
            min_font_size=5,
            # random_state=50,
        )

        word_cloud = wc.generate(words_str)  # 产生词云
        word_cloud.to_file("images/word_cloud_{}.jpg".format(self.cid))  # 保存图片


if __name__ == '__main__':
    word_cloud_generator = WordCloudGenerator()
    word_cloud_generator.main()

