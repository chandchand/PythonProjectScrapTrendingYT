import csv
from os import write
import time
from googleapiclient.discovery import build
import requests
import sys


api_key = "AIzaSyBOWMStWVtB9F8II3Wc3l9-vfOlkTga0HA"

country_code = "ID"

# youtube = build('youtube', 'v3', developerKey=api_key)

# request = youtube.videos().list(
#     part='snippet,contentDetails,statistics',
#     chart="mostPopular",
#     regionCode="ID"
# )

# List of simple to collect features
snippet_features = ["title",
                    "publishedAt",
                    "channelId",
                    "channelTitle",
                    "categoryId"]

# # Any characters to exclude, generally these are things that become problematic in CSV files
unsafe_characters = ['\n', '"']

# Used to identify columns, currently hardcoded order
# header = ["video_id"] + snippet_features + ['id', 'channels_id', 'channels',
#                                             'judul', 'trending_date', 'tags', 'deskripsi', 'thumbnail', 'likes', 'dislikes', 'views', 'comments', 'waktu_upload']

# print(snippet_features)


def prepare_feature(feature):
    # Removes any character from the unsafe characters list and surrounds the whole item in quotes
    for ch in unsafe_characters:
        feature = str(feature).replace(ch, "")
    return f'"{feature}"'


def api_req():
    url = f"https://www.googleapis.com/youtube/v3/videos?part=id,statistics,snippet&chart=mostPopular&regionCode=ID&maxResults=50&key=AIzaSyBOWMStWVtB9F8II3Wc3l9-vfOlkTga0HA"
    request = requests.get(url)
    if request.status_code == 429:
        print("Temp-Banned due to excess requests, please wait and continue later")
        sys.exit()
    return request.json()

# response = api_req()
# print(response)


def get_tags(tags_list):
    # Takes a list of tags, prepares each tag and joins them into a string by the pipe character
    return prepare_feature("|".join(tags_list))


# print(api_req)
video_data_page = api_req()
items = video_data_page.get('items', [])

# jalan = request.execute()
# print(jalan)

# print(items)

file = open('result/youtube_trending.csv', 'w', newline='', encoding='utf8')
writer = csv.writer(file)
head = ["id", "channel_id", "channel", "judul",
        "trending_date", "tags", "upload_date", "views", "likes", "dislikes", "comments", "thubmnail_link", "description"]

lines = []
for video in items:
    comments_disabled = False
    ratings_disabled = False
    # jika salah satu item yg tidak ada statistik maka kita skip
    if "statistics" not in video:
        continue

    video_id = prepare_feature(video['id'])

    snippet = video['snippet']
    statistics = video['statistics']

    # This list contains all of the features in snippet that are 1 deep and require no special processing
    features = [prepare_feature(snippet.get(feature, ""))
                for feature in snippet_features]

    # items2 di list snippet sama statistic di ambil sebagai variable satu persatu sesaui kebutuhan scrapping
    upload_date = snippet.get("publishedAt")
    channel_id = snippet.get("channelId")
    channel = snippet.get("channelTitle")
    title = snippet.get("title")
    description = snippet.get("description", "")
    thumbnail_link = snippet.get("thumbnails", dict()).get(
        "default", dict()).get("url", "")
    trending_date = time.strftime("%y.%d.%m")
    tags = get_tags(snippet.get("tags", ["[none]"]))
    view_count = statistics.get("viewCount", 0)

    if 'likeCount' in statistics and 'dislikeCount' in statistics:
        likes = statistics['likeCount']
        dislikes = statistics['dislikeCount']
    else:
        ratings_disabled = True
        likes = 0
        dislikes = 0

    if 'commentCount' in statistics:
        comment_count = statistics['commentCount']
    else:
        comments_disabled = True
        comment_count = 0

    lines.append([video_id, channel_id,                                                             # description.replace("\n", ".") di komen karena kada ada vidio yg memilik 3 enter baris atau \n
                 channel, title, trending_date, tags, upload_date, view_count, likes, dislikes, comment_count, thumbnail_link, "-"])
    # lines = [video_id, ]
    # line = [video_id] + features + [prepare_feature(x) for x in [trending_date, tags, view_count, likes, dislikes,
    #                                                              comment_count, thumbnail_link, comments_disabled,
    #                                                              ratings_disabled, description]]
    # lines.append(",".join(line))

    print(snippet)
writer.writerow(head)
for d in lines:
    writer.writerow(d)
file.close
# print(data)
