import ckan.plugins.toolkit as toolkit
import hashlib
import logging
import json
import ckan.views.api as api
import ckanext.ga_api_actions.plugin as ga_api_actions_plugin

from flask import Blueprint

ga_api_actions = Blueprint(u'ga_api_actions', __name__, url_prefix=u'/api')

log = logging.getLogger(__name__)


def _alter_sql(sql_query):
    '''Quick and dirty altering of sql to prevent injection'''
    sql_query = sql_query.lower()
    sql_query = sql_query.replace('select', 'CK_SEL')
    sql_query = sql_query.replace('insert', 'CK_INS')
    sql_query = sql_query.replace('update', 'CK_UPD')
    sql_query = sql_query.replace('upsert', 'CK_UPS')
    sql_query = sql_query.replace('declare', 'CK_DEC')
    sql_query = sql_query[:450].strip()
    return sql_query


def _post_analytics(user, request_event_action, request_event_label):
    '''intercept API calls to record via google analytics's'''
    if ga_api_actions_plugin.GoogleAnalyticsPlugin.google_analytics_id:
        data_dict = {
            "v": 1,
            "tid": ga_api_actions_plugin.GoogleAnalyticsPlugin.google_analytics_id,
            "cid": hashlib.md5(user.encode()).hexdigest(),
            # customer id should be obfuscated
            "t": "event",
            "dh": toolkit.request.environ['HTTP_HOST'],
            "dp": toolkit.request.environ['PATH_INFO'],
            "dr": toolkit.request.environ.get('HTTP_REFERER', ''),
            "ec": toolkit.request.environ['HTTP_HOST'] + " CKAN API Request",
            "ea": request_event_action,
            "el": request_event_label
        }
        ga_api_actions_plugin.GoogleAnalyticsPlugin.analytics_queue.put(data_dict)


def _get_action_request_data(api_action):
    function = toolkit.get_action(api_action)
    side_effect_free = getattr(function, 'side_effect_free', False)
    request_data = api._get_request_data(try_url_params=side_effect_free)
    return request_data


def _get_parameter_value(request_data):
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
            parameter_value = _alter_sql(request_data['sql'])
        # Send all request_data if defined parameter cannot be found
        if parameter_value == '' and len(request_data) > 0:
            parameter_value = json.dumps(request_data)

    return parameter_value


def action(api_action, ver=api.API_MAX_VERSION):
    try:
        request_data = _get_action_request_data(api_action)
        parameter_value = _get_parameter_value(request_data)
        capture_api_actions = ga_api_actions_plugin.GoogleAnalyticsPlugin.capture_api_actions
        event_action = ''
        event_label = ''

        # Only send api actions if it is in the capture_api_actions dictionary
        if api_action in capture_api_actions:
            capture_api_action = capture_api_actions.get(api_action)
            event_action = capture_api_action['action'].format(api_action)
            event_label = capture_api_action['label'].format(parameter_value)
            # If catch_all_api_actions is True send api action
        elif ga_api_actions_plugin.GoogleAnalyticsPlugin.catch_all_api_actions:
            event_action = api_action
            event_label = parameter_value

        # Only send to google analytics if event_action is set to reduce noise
        if event_action:
            _post_analytics(toolkit.g.user, event_action, event_label)

    except Exception as e:
        log.debug(e)
        pass

    return api.action(api_action, ver)


ga_api_actions.add_url_rule(u'/action/<api_action>',
    methods=[u'GET', u'POST'], view_func=action)

ga_api_actions.add_url_rule(
    u"/<int(min=3, max={0}):ver>/action/<api_action>".format(
        api.API_MAX_VERSION
    ),
    methods=["GET", "POST"],
    view_func=action,
)