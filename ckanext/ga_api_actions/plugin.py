import json
import logging
import queue
import requests
import threading
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ckanext.ga_api_actions.helpers as helpers
from os import path
from six.moves.urllib.parse import urlencode

log = logging.getLogger(__name__)
config = toolkit.config


class AnalyticsPostThread(threading.Thread):
    """Threaded Url POST"""

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.ga_collection_url = toolkit.config.get('ckan.ga_api_actions_googleanalytics.collection_url',
                                                    'https://www.google-analytics.com/collect')

    def run(self):
        # User-Agent must be present, GA might ignore a custom UA.
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'
        }
        while True:
            # Get host from the queue.
            data_dict = self.queue.get()
            log.debug("Sending API event to Google Analytics: " + data_dict['ea'])

            # Send analytics data.
            try:
                data = urlencode(data_dict)
                requests.post(self.ga_collection_url, data=data, headers=headers, timeout=5)
                self.queue.task_done()
                log.debug("Google Analytics API event was sent successfully")
            except requests.exceptions.RequestException as e:
                log.error(f"Sending API event to Google Analytics failed: {e}")
                # If error occurred while posting - dont try again or attempt to fix  - just discard from the queue.
                self.queue.task_done()


class GoogleAnalyticsPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IBlueprint)

    analytics_queue = queue.Queue()
    capture_api_actions = {}
    google_analytics_id = None
    catch_all_api_actions = False

    def configure(self, config):
        '''Load config settings for this extension from config file.

        See IConfigurable.

        '''
        # Load capture_api_actions from JSON file
        here = path.abspath(path.dirname(__file__))
        with open(path.join(here, 'capture_api_actions.json')) as json_file:
            GoogleAnalyticsPlugin.capture_api_actions = json.load(json_file)

        # Get google_analytics_id from config file
        GoogleAnalyticsPlugin.google_analytics_id = toolkit.config.get('ckan.ga_api_actions.id')

        # Get catch_all_api_actions from config file
        GoogleAnalyticsPlugin.catch_all_api_actions = toolkit.asbool(toolkit.config.get('ckan.ga_api_actions.catch_all_api_actions', False))

        # spawn a pool of 5 threads, and pass them queue instance
        for i in range(5):
            t = AnalyticsPostThread(self.analytics_queue)
            t.setDaemon(True)
            t.start()

    # IBlueprint
    def get_blueprint(self):
        return helpers._register_blueprints()
