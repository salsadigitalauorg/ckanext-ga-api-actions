# ckanext-ga-api-actions

CKAN extension which sends back end API events to google analytics.

This extension is based on the event tracking from the CKAN Google Analytics Extension (https://github.com/ckan/ckanext-googleanalytics).

That extension only tracked a limited amount of API events where this extension has a configurable list of APIs events and labels that can be sent to google analytics.

## Installation

Clone repo into your CKAN extension directory, e.g. `/usr/lib/ckan/default/src`, then:

Activate the Python virtual environment, e.g.

        . /usr/lib/ckan/default/bin/activate

        cd ckanext-ga-api-actions
        python setup.py develop

## CKAN Configuration Settings

Make the following changes within your CKAN `.ini` file, e.g. `production.ini`

Enable the `ga_api_actions` extension:

        ckan.plugins = ... ga_api_actions

Add your google analytics tracking ID

        ckan.ga_api_actions_googleanalytics.id = UA-XXXXXXXXX-X

Add google analytics URL to send the data

        ckan.ga_api_actions_googleanalytics.collection_url = http://www.google-analytics.com/collect

## API Action Configuration File

List of API event actions and labels that can be configured in the file

        ckanext-ga-api-actions/ckanext/ga_api_actions/capture_api_actions.json

