import sys
import time

import schedule
import requests


def tweet_content(talk_json):
    content = ""
    content += talk_json["title"]
    content += " "
    content += "https://vtalks.net/talk/{}".format(talk_json['slug'])
    return content


def job():
    print("Get a random talk ...")
    # get a random talk
    r = requests.get('https://vtalks.net/api/random-talk/')
    if r.status_code != 200:
        print("Can't fetch a random talk, response status code is",
              r.status_code)
        exit(1)

    talk_json = r.json()

    print(talk_json)


def main(argv):
    print('Starting twitter-worker ...')

    job()

    schedule.every(6).hours.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main(sys.argv[1:])
