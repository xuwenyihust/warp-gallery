from bilibili.WordCloudGenerator import WordCloudGenerator
from bilibili.UserInfo import user_info_map


def run(uid, mask_file_path):
    word_cloud_generator = WordCloudGenerator()

    videos = word_cloud_generator.get_videos_by_user(uid)
    word_cloud_generator.get_barrages_by_uid(uid, videos)
    barrages_file_path = 'resources/barrages/realtime_barrage_by_user_{}.csv'.format(uid)
    word_cloud_generator.generate_graph_from_file(barrages_file_path, str(uid), mask_file_path)


def run_media_storm():
    # 影视飓风
    uid = user_info_map["media_storm"]["mid"]
    mask_file_path = user_info_map["media_storm"]["mask"]
    run(uid, mask_file_path)


def run_xiaomi():
    # 小米公司
    uid = user_info_map["xiaomi"]["mid"]
    mask_file_path = user_info_map["xiaomi"]["mask"]
    run(uid, mask_file_path)
