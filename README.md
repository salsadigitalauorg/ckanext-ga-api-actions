=============
ckanext-ga-api-actions
=============

CKAN extension which sends back end API events to google analytics.
The extension is based on the event tracking from the CKAN Google Analytics Extension (https://github.com/ckan/ckanext-googleanalytics).
That extension only tracked a limited amount of API events where this extension has a configurable list of APIs events and labels that can be sent to google analytics.


------------
Installation
------------

Clone repo into the /usr/lib/ckan/default/src directory, then:

    cd ckanext-ga-api-actions
    python setup.py develop


---------------
Config Settings
---------------

Your google analytics tracking ID

    ckan.ga_api_actions_googleanalytics.id = UA-XXXXXXXXX-X


The google analytics URL to send the data

    ckan.ga_api_actions_googleanalytics.collection_url = http://www.google-analytics.com/collect

List of API event actions and labels that can be configured in the file

    ckanext-ga-api-actions/ckanext/ga_api_actions/capture_api_actions.json




