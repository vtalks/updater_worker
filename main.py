import sys
import time
import logging

import schedule
import requests


def job():
    logging.debug("Get a random talk ...")
    # get a random talk
    r = requests.get('https://vtalks.net/api/random-talk/')
    if r.status_code != 200:
        logging.error("Can't fetch a random talk, response status code is", r.status_code)
        exit(1)

    talk_json = r.json()

    logging.debug(talk_json)


def main(argv):
    logging.basicConfig(level=logging.DEBUG)
    logging.debug('Starting updater-worker ...')

    job()

    # schedule.every(6).hours.do(job)
    schedule.every(30).seconds.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main(sys.argv[1:])
