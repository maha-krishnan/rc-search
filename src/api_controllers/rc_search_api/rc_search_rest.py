import jsonpickle
from flask import g, Blueprint, jsonify, request, current_app, send_file
from flask_responses import json_response
from dict2obj import Dict2Obj
import logging
import requests
import os
from configs import config as cfg
from configs.config import get_from_env
from api_controllers.rc_search_api.context import required_authorization
from exceptions import errors
from r2essentials.context import RContext
from lib.provider.dynamo_provider import DynamoDBProvider
from lib.models.model import RCJSON_DATAFORMAT

import time
import json
from json import JSONEncoder
from http import HTTPStatus

RC_SEARCH_ROUTE = Blueprint('rc_search', __name__)
ALLOWED_EXTENSIONS = set(['csv'])

is_dev, is_test = cfg.mode()

@RC_SEARCH_ROUTE.route('/external/v1/rc_search/<string:search_term>', methods=['GET'])
@required_authorization(allowed_roles=["rc-workbench:fetch:lookup"])
def generate_rc_search(search_term):

    context = g.context
    dynamo_provider = DynamoDBProvider(connection=None, context=context)
    tenant_id = f"{context.tenant_context.tenant_id}"
    table_name = "tenant_" + tenant_id[0] + "_rc_search"

    items = dynamo_provider.fetch_items(table_name)
    rc_jsons_found = process_items(items, search_term)

    data_found_list = format_rc_jsons(rc_jsons_found)

    # Return back successful acknowledge and the generated desk
    resp = jsonify({'message' : 'RC Search Successfully returned', 'data_items' : data_found_list})
    resp.status_code = HTTPStatus.CREATED
    return resp

def process_items(items, search_term):
    rc_jsons_found = {}
    for item in items:
        tenant_rc_id = item.get('tenant_rc_id')
        rc_json_str = item.get('rc_json')
        if search_term in rc_json_str:
            rc_id = tenant_rc_id.split('_')[-1]
            rc_json = json.loads(rc_json_str)
            rc_jsons_found[rc_id] = rc_json
            
    return rc_jsons_found

def format_rc_jsons(rc_jsons_found):
    data_found_list = []
    for rc_id, rc_json in rc_jsons_found.items():
        name = rc_id
        version = rc_json.get('version')
        isonhold = True if rc_json.get('holds') else False
        customer = rc_json['rc_attributes']['customer_name']
        rc_metrics = rc_json.get('rc_metrics', None)
        value, billed, recognized, scheduled = fetch_metrics_vals(rc_metrics)
        transactional_currency_code = rc_json['rc_attributes']['currency_code']
        created_period = rc_json['statuses']['created_period']
        modified_period = rc_json['statuses']['modified_period']
        rc_json_format = RCJSON_DATAFORMAT(name, version, isonhold, customer, value, transactional_currency_code, billed, recognized, scheduled, created_period, modified_period)       
        data_found_list.append(rc_json_format.__dict__)

    return data_found_list

def fetch_metrics_vals(rc_metrics):
    value, billed, recognized, scheduled = 0, 0, 0, 0
    if not rc_metrics:
        return value, billed, recognized, scheduled
    
    metrics = rc_metrics['metrics']
    value_index = metrics.index('contract_value')
    billed_index = metrics.index('billed_amount')
    recognized_index = metrics.index('net_revenue_recognized')
    scheduled_index = metrics.index('net_revenue_planned')

    amount = rc_metrics['amount']
    return amount[value_index], amount[billed_index], amount[recognized_index], amount[scheduled_index]

def make_header_info(context: RContext, user_roles: str):
    return {'X-R2-USER-ID': context.user_context.user_id, 'x-r2-tenant-id': context.tenant_context.tenant_id, 'x-r2-user-roles': user_roles}

@RC_SEARCH_ROUTE.errorhandler(errors.IncompliantData)
def incompliant_json_data(error):
    """Empty or invalid file exception"""
    error = error.__dict__
    response = jsonify(message=error['error_message'])
    response.status_code = error['response_code']
    return response

@RC_SEARCH_ROUTE.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """Internal Server Error"""
    error = error.__dict__
    response = jsonify(message=errors.SERVER_ERROR)
    response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    return response                    

@RC_SEARCH_ROUTE.before_request
def before_request():
    from api_controllers.rc_search_api.metrics import before_request as br
    from flask import request
    br(request)

@RC_SEARCH_ROUTE.after_request
def after_request(response):
    """We will conclude desk and add some headers as required"""
    from api_controllers.rc_search_api.metrics import after_request as br
    return br(response)

