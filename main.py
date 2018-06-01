import os
import sys
import time
import logging
import json

import schedule
import requests


def get_random_talk():
    logging.debug("Get a random talk ...")
    r = requests.get('https://vtalks.net/api/random-talk/')
    if r.status_code != 200:
        logging.error("Can't fetch a random talk, response status code is", r.status_code)
        return
    return r.json()


def update_video(youtube_api_key, video_code):
    logging.debug("Fetch video from youtube API ...")
    video_url = "https://www.googleapis.com/youtube/v3/videos"
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
    return video_data


def job():
    # get a talk
    talk_json = get_random_talk()
    if not talk_json:
        return
    logging.debug(json.dumps(talk_json))

    # get data from youtube
    talk_video_code = talk_json["code"]
    video_data = update_video(os.environ.get("YOUTUBE_API_KEY"), talk_video_code)
    if not video_data:
        return
    logging.debug(json.dumps(video_data))

    # update youtube stats
    if "viewCount" not in video_data["statistics"]:
        talk_json["youtube_view_count"] = video_data["statistics"]["viewCount"]
    if "likeCount" not in video_data["statistics"]:
        talk_json["youtube_like_count"] = video_data["statistics"]["likeCount"]
    if "dislikeCount" not in video_data["statistics"]:
        talk_json["youtube_dislike_count"] = video_data["statistics"]["dislikeCount"]
    if "favoriteCount" not in video_data["statistics"]:
        talk_json["youtube_favorite_count"] = video_data["statistics"]["favoriteCount"]

    # update total stats
    talk_json["total_view_count"] = int(talk_json["view_count"]) + \
        int(talk_json["youtube_view_count"])
    talk_json["total_like_count"] = int(talk_json["like_count"]) + \
        int(talk_json["youtube_like_count"])
    talk_json["total_dislike_count"] = int(talk_json["dislike_count"]) + \
        int(talk_json["youtube_like_count"])
    talk_json["total_favorite_count"] = int(talk_json["favorite_count"]) + \
        int(talk_json["youtube_favorite_count"])

    # update talk
    talk_id = talk_json["id"]
    r = requests.put("https://vtalks.net/api/talk/"+str(talk_id)+"/",
                     json=talk_json)
    if r.status_code != 200:
        logging.error("Can't update a talk, response status code is",
                      r.status_code)
        logging.error(r.text)
        return
    logging.debug(json.dumps(r.json()))


def main(argv):
    logging.basicConfig(level=logging.DEBUG)
    logging.debug('Starting updater-worker ...')
    job()
    schedule.every().minute.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main(sys.argv[1:])
