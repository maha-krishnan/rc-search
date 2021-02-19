import os
import logging
basedir = os.path.abspath(os.path.dirname(__file__))

def get_from_env(key: str, fallback: str) -> str:
    try:
        return os.environ[key]
    except KeyError:
        return fallback

def mode() -> (bool, bool):
    DEVELOPMENT = False
    AUTOMATED_TESTING = False
    mode  = get_from_env('RC_SEARCH_MODE', 'TEST')
    if mode == 'AWS':
        DEVELOPMENT = False
        AUTOMATED_TESTING = False
    elif mode == 'TEST':
        DEVELOPMENT = False
        AUTOMATED_TESTING = True
    else:
        DEVELOPMENT = True
        AUTOMATED_TESTING = False

    return DEVELOPMENT, AUTOMATED_TESTING

class Config(object):
    TARGET_TYPE = None
    DEVELOPMENT, AUTOMATED_TESTING = mode()
    
    CSRF_ENABLED = True
    POLICY_SET_URL = get_from_env("POLICY_SET_URL", "http://localhost:5448")
    RECORDER_DEV_URL = get_from_env("RECORDER_URL", "http://localhost:5449")
    SECRET_KEY = 'rightrev'
    SQLALCHEMY_DATABASE_URI = None
    ACCOUNTING_CALENDAR_ENDPOINT = POLICY_SET_URL + "/external/v1/policy/calendar"
    CURRENT_OPEN_PERIOD_ENDPOINT = POLICY_SET_URL + "/external/v1/policy/period-open-close"
    RECORDER_URL = RECORDER_DEV_URL + '/external/v1/revenue_contract_ids'
    RECORDER_FETCH_URL = RECORDER_DEV_URL + '/external/v1/revenue_contract'

