import logging
from stream_django.managers import FeedManager as DefaultFeedManager

log = logging.getLogger(__name__)


class FeedManager(DefaultFeedManager):
    CHALLENGE_FEED = 'challenge'
    CHALLENGE_FEED_AGGREGATED = 'challenge_aggregated'

    def get_challenge_feed(self, challenge_id: str, aggregated: str = False):
        if aggregated:
            return self.get_feed(self.CHALLENGE_FEED_AGGREGATED, challenge_id)
        return self.get_feed(self.CHALLENGE_FEED, challenge_id)

    def get_global_challenge_feed(self):
        return self.get_feed(self.CHALLENGE_FEED_AGGREGATED, 'global')

    def add_notify_to_activity(self, activity, notify):
        if not isinstance(notify, list):
            notify = [notify]
        activity['to'] = list(
            set(activity.get('to', []) + [n.id for n in notify]))
        return activity

    def add_activity(self, feed, activity):
        try:
            feed.add_activity(activity)
        except Exception as e:
            log.error(str(e))


feed_manager = FeedManager()
