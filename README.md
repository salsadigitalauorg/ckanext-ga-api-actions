=============
ckanext-ga-api-actions
=============

CKAN extension which sends back end API events to google analytics's.
The extension is based on the event tracking from the CKAN Google Analytics's Extension (https://github.com/ckan/ckanext-googleanalytics).
This extension has a configurable list of APIs events and labels that can be sent to google analytics's.


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

    ckan.ga_api_actions.id = UA-XXXXXXXXX-X


The google analytics URL to send the data

    ckan.ga_api_actions.collection_url = https://www.google-analytics.com/collect


List of API event actions and labels that can be configured in the file

    ckanext-ga-api-actions/ckanext/ga_api_actions/capture_api_actions.json


To catch all api actions that are not in the capture_api_actions.json file

    ckan.ga_api_actions.catch_all_api_actions = False


