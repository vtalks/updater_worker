import os
import sys
import time
import logging
import json

import schedule
import requests


def get_version():
    file = open("VERSION", "r")
    return file.read().rstrip("\n")


def get_random_talk():
    headers = {'user-agent': 'vtalks/updater-worker/'+get_version()}
    r = requests.get('https://vtalks.net/api/talk/random-talk/', headers=headers)
    if r.status_code != 200:
        logging.error("Can't fetch a random talk, HTTP {}".format(r.status_code))
        return
    logging.debug(json.dumps(r.json()))
    return r.json()


def get_youtube_video(youtube_api_key, video_code):
    video_url = "https://www.googleapis.com/youtube/v3/talks"
    payload = {'id': video_code,
               'part': 'snippet,statistics',
               'key': youtube_api_key}
    resp = requests.get(video_url, params=payload)
    if resp.status_code != 200:
        raise Exception('Error fetching video data "%s"' % resp.status_code)
    response_json = resp.json()
    video_data = None
    if len(response_json["items"]) > 0:
        video_data = response_json["items"][0]
    logging.debug(video_data)
    return video_data


def update_talk(talk_json):
    talk_id = talk_json["id"]
    headers = {'user-agent': 'vtalks/updater-worker/' + get_version()}
    r = requests.put("https://vtalks.net/api/talk/" + str(talk_id) + "/",
                     json=talk_json, headers=headers)
    if r.status_code != 200:
        logging.error("Can't update talk '{} {}': HTTP {}".format(talk_json["id"], talk_json["title"], r.status_code))
        logging.error(r.text)
        return
    logging.debug(json.dumps(r.json()))
    logging.info("Updated talk '{} {}' successfully.".format(talk_json["id"], talk_json["title"]))


def update_youtube_stats(talk_json, youtube_video_data):
    if "viewCount" in youtube_video_data["statistics"]:
        talk_json["youtube_view_count"] = youtube_video_data["statistics"]["viewCount"]
    if "likeCount" in youtube_video_data["statistics"]:
        talk_json["youtube_like_count"] = youtube_video_data["statistics"]["likeCount"]
    if "dislikeCount" in youtube_video_data["statistics"]:
        talk_json["youtube_dislike_count"] = youtube_video_data["statistics"]["dislikeCount"]
    if "favoriteCount" in youtube_video_data["statistics"]:
        talk_json["youtube_favorite_count"] = youtube_video_data["statistics"]["favoriteCount"]
    return talk_json


def update_total_stats(talk_json):
    talk_json["total_view_count"] = int(talk_json["view_count"]) + int(talk_json["youtube_view_count"])
    talk_json["total_like_count"] = int(talk_json["like_count"]) + int(talk_json["youtube_like_count"])
    talk_json["total_dislike_count"] = int(talk_json["dislike_count"]) + int(talk_json["youtube_like_count"])
    talk_json["total_favorite_count"] = int(talk_json["favorite_count"]) + int(talk_json["youtube_favorite_count"])
    return talk_json


def job():
    # get a talk
    talk_json = get_random_talk()
    if not talk_json:
        return

    # get data from youtube
    talk_video_code = talk_json["code"]
    video_data = get_youtube_video(os.environ.get("YOUTUBE_API_KEY"),
                                   talk_video_code)
    if not video_data:
        return

    # update youtube stats
    talk_json = update_youtube_stats(talk_json, video_data)

    # update total stats
    talk_json = update_total_stats(talk_json)

    # update talk
    update_talk(talk_json)


def main(argv):
    logging.basicConfig(level=logging.INFO)
    logging.debug('Starting updater-worker ...')
    job()
    schedule.every(5).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main(sys.argv[1:])
