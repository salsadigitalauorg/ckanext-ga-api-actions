import ckan.plugins.toolkit as toolkit
import hashlib
import logging
from ckan.controllers.api import ApiController
import json

import plugin as ga_api_actions

log = logging.getLogger('ckanext.ga_api_actions')
c = toolkit.c


class GoogleAnalyticsApiController(ApiController):

    def _alter_sql(self, sql_query):
        '''Quick and dirty altering of sql to prevent injection'''
        sql_query = sql_query.lower()
        sql_query = sql_query.replace('select', 'CK_SEL')
        sql_query = sql_query.replace('insert', 'CK_INS')
        sql_query = sql_query.replace('update', 'CK_UPD')
        sql_query = sql_query.replace('upsert', 'CK_UPS')
        sql_query = sql_query.replace('declare', 'CK_DEC')
        sql_query = sql_query[:450].strip()
        return sql_query

    def _post_analytics(self, user, request_event_action, request_event_label):
        '''intercept API calls to record via google analytics's'''
        if ga_api_actions.GoogleAnalyticsPlugin.google_analytics_id:
            data_dict = {
                "v": 1,
                "tid": ga_api_actions.GoogleAnalyticsPlugin.google_analytics_id,
                "cid": hashlib.md5(user).hexdigest(),
                # customer id should be obfuscated
                "t": "event",
                "dh": c.environ['HTTP_HOST'],
                "dp": c.environ['PATH_INFO'],
                "dr": c.environ.get('HTTP_REFERER', ''),
                "ec": c.environ['HTTP_HOST'] + " CKAN API Request",
                "ea": request_event_action,
                "el": request_event_label
            }
            ga_api_actions.GoogleAnalyticsPlugin.analytics_queue.put(data_dict)

    def _get_action_request_data(self, api_action):
        function = toolkit.get_action(api_action)
        side_effect_free = getattr(function, 'side_effect_free', False)
        request_data = self._get_request_data(try_url_params=side_effect_free)
        return request_data

    def _get_parameter_value(self, request_data):
        parameter_value = ''
        if isinstance(request_data, dict):     
            parameter_value = request_data.get('id', '')
            if parameter_value == '' and 'resource_id' in request_data:
                parameter_value = request_data['resource_id']
            if parameter_value == '' and 'q' in request_data:
                parameter_value = request_data['q']
            if parameter_value == '' and 'query' in request_data:
                parameter_value = request_data['query']
            if parameter_value == '' and 'sql' in request_data:
                parameter_value = self._alter_sql(request_data['sql'])
            # Send all request_data if defined parameter cannot be found
            if parameter_value == '' and len(request_data) > 0:
                parameter_value = json.dumps(request_data)

        return parameter_value

    def action(self, api_action, ver=None):
        try:
            request_data = self._get_action_request_data(api_action)
            parameter_value = self._get_parameter_value(request_data)
            capture_api_actions = ga_api_actions.GoogleAnalyticsPlugin.capture_api_actions           
            event_action = ''
            event_label = ''   
            
            # Only send api actions if it is in the capture_api_actions dictionary
            if api_action in capture_api_actions:
                capture_api_action = capture_api_actions.get(api_action)
                event_action = capture_api_action['action'].format(api_action)
                event_label = capture_api_action['label'].format(parameter_value)
             # If catch_all_api_actions is True send api action
            elif ga_api_actions.GoogleAnalyticsPlugin.catch_all_api_actions:
                event_action = api_action
                event_label = parameter_value                
                
            # Only send to google analytics if event_action is set to reduce noise    
            if event_action:             
                self._post_analytics(c.user, event_action, event_label)

        except Exception as e:
            log.debug(e)
            pass

        return ApiController.action(self, api_action, ver)
