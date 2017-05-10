from datetime import datetime, timedelta
from time import sleep
from threading import Lock
from sqlalchemy import func
import requests
from chat import tell_rooms_with
from post import Post
import config
import secrets
from database import SESSION, BaseModel, BodyfetcherQueueItem, BodyfetcherQueueTiming, BodyfetcherMaxId
from spam_handling import check_if_spam


API_REQUEST_LOCK = Lock()
BACKOFF_UNTIL = datetime(1970, 1, 1, 0, 0, 0)


def _queue_threshold(site):
    overridden = config.queue_sizes
    if site in overridden:
        return overridden[site]
    else:
        return config.default_queue_size


def _fire_api_request(items, site):
    item_ids = [x.id for x in items.all()]
    previous_max_id = SESSION.query(func.max(BodyfetcherMaxId.max_id))\
                             .filter(BodyfetcherMaxId.site_url == site).all()[0][0]
    intermediate_ids = list(range(previous_max_id + 1, min(item_ids)))
    fetch_ids = intermediate_ids + item_ids
    fetch_ids = fetch_ids[-min(len(fetch_ids), 100):]

    api_key = secrets['se_key']
    uri = 'https://api.stackexchange.com/2.2/questions/{}?site={}&key={}'.format(';'.join(fetch_ids), site, api_key)

    API_REQUEST_LOCK.acquire()
    if datetime.utcnow() < BACKOFF_UNTIL:
        sleep((BACKOFF_UNTIL - datetime.utcnow()).total_seconds())

    try:
        response = requests.get(uri, timeout=10)
    except (requests.exceptions.Timeout, requests.ConnectionError) as ex:
        tell_rooms_with('debug', "SE API request errored: {}".format(ex))
        return

    API_REQUEST_LOCK.release()
    response = response.json()

    _clear_queue(fetch_ids, site)
    _process_response(response)


def _clear_queue(ids, site):
    col = SESSION.query(BodyfetcherQueueItem).filter(BodyfetcherQueueItem.post_id.in_(ids),
                                                     BodyfetcherQueueItem.site_url == site)
    BaseModel.delete_collection(col)


def _process_response(response):
    global BACKOFF_UNTIL

    if 'backoff' in response:
        BACKOFF_UNTIL = datetime.utcnow() + timedelta(seconds=response['backoff'])

    for post in response['items']:
        post_obj = Post(api_response=post)
        check_if_spam(post_obj)


def _calculate_queue_timings(items):
    for item in items.all():
        time = (datetime.utcnow() - item.enqueued_at).total_seconds()
        BodyfetcherQueueTiming.create(site_url=item.site_url, time_in_queue=time)


def enqueue(post):
    """
    Adds a post to the bodyfetcher queue so that it gets fetched the next time the queue fills up.
    :param post: a Post instance (see: post.py) containing at minimum post_site and post_id attributes
    :return: None
    """
    site = post.post_site
    BodyfetcherQueueItem.create(site_url=site, post_id=post.post_id, enqueued_at=datetime.utcnow())

    items = BodyfetcherQueueItem.by_site(site)
    if items.count() >= _queue_threshold(site):
        _fire_api_request(items, site)
        _calculate_queue_timings(items)
        BaseModel.delete_collection(BodyfetcherQueueItem.by_site(site))
