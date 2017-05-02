from datetime import datetime
from sqlalchemy import func
import requests
import config
from database import SESSION, BaseModel, BodyfetcherQueueItem, BodyfetcherQueueTiming, BodyfetcherMaxId
from spam_handling import check_if_spam


def _queue_threshold(site):
    overridden = config['queue_sizes']
    if site in overridden:
        return overridden[site]
    else:
        return config['default_queue_size']


def _fire_api_request(items, site):
    item_ids = [x.id for x in items.all()]
    previous_max_id = SESSION.query(func.max(BodyfetcherMaxId)).filter(BodyfetcherMaxId.site_url == site).all()[0][0]
    intermediate_ids = range(previous_max_id + 1, min(item_ids))
    fetch_ids = intermediate_ids + item_ids
    fetch_ids = fetch_ids[-min(len(fetch_ids), 100):]


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
