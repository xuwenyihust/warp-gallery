from bilibili.WordCloudGenerator import WordCloudGenerator
from bilibili.UserInfo import user_info_map


def run():
    word_cloud_generator = WordCloudGenerator()
    # 影视飓风
    # mediastorm_uid = user_info_map["media_storm"]["mid"]
    # mediastorm_mask = user_info_map["media_storm"]["mask"]
    # word_cloud_generator.run(mediastorm_uid, mediastorm_mask)

    # 小米公司
    xiaomi_uid = user_info_map["xiaomi"]["mid"]
    xiaomi_mask = user_info_map["xiaomi"]["mask"]
    word_cloud_generator.run(xiaomi_uid, xiaomi_mask)


if __name__ == '__main__':
    run()
