import boto3
from r2essentials.config import get_from_env
import jsonpickle
import zlib
from botocore.exceptions import ClientError
from lib.models.model import RCJSON
import typing
import logging
import json

TABLE_NAME = get_from_env('STORAGE_CURRENCY_TABLE_NAME', 'stamper_rc_currency')

def get_db_session(dynamodb=None):
    endpoint_url = get_from_env("DYNAMODB_URL", "http://localhost:6000")
    if endpoint_url == "false":
        dynamodb = boto3.resource('dynamodb')
    else:
        dynamodb = boto3.resource('dynamodb', endpoint_url=endpoint_url)
    return dynamodb

def get_table(table_name, dynamodb=None):
    """Method to get the table object based on table name
    """
    dynamodb = get_db_session(dynamodb) if dynamodb is None else dynamodb
    table = dynamodb.Table(table_name)
    try:
        status = table.table_status
    except ClientError as e:
        logging.info(e.response['Error']['Message'])
        create_table(table_name, dynamodb)
        table.wait_until_exists()
    return table

def new_item(table_name, p: RCJSON, dynamodb=None):
    dynamodb = get_db_session(dynamodb) if dynamodb is None else dynamodb
    table = dynamodb.Table(table_name)
    response = table.put_item(
       Item={
            'tenant_rc_id': f"{p.tenant_id}" + "_" + f"{p.rc_id}",
            'rc_json':p.rc_json
        }
    )
    return response

def delete_item(tenant_id, rc_id, dynamodb=None, table_name = ''):
    dynamodb = get_db_session(dynamodb) if dynamodb is None else dynamodb
    table = dynamodb.Table(table_name)
    response = table.delete_item(
        Key={
            'tenant_rc_id': f"{tenant_id}" + "_" + f"{rc_id}",
        }
    )
    return response

def get_item(table_name, tenant_id, rc_id, dynamodb=None):
    dynamodb = get_db_session(dynamodb) if dynamodb is None else dynamodb
    table = dynamodb.Table(table_name)
    try:
        response = table.get_item(Key={'tenant_rc_id': f"{tenant_id}"+ "_" + f"{rc_id}"})
        print(response)
    except ClientError as e:
        print(e.response['Error']['Message'])
        return None
    
    else:
        print('hi')
        if 'Item' not in response:
            return None
        tenant_id = response['Item']['tenant_rc_id'].split(":")[0]
        rc_json = response['Item']['rc_json']
        return RCJSON(tenant_id, rc_id, rc_json)
    
def get_all_items(table_name, dynamodb=None):
    dynamodb = get_db_session(dynamodb) if dynamodb is None else dynamodb
    table = dynamodb.Table(table_name)
    try:
        response = table.scan()
        print(response)
    except ClientError as e:
        print(e.response['Error']['Message'])
        return None
    
    else:
        print('hi')
        if 'Items' not in response:
            return None
        items = response['Items']
        
        '''
        rc_jsons_found = process_items(items)

        from lib.models.model import RCJSON_DATAFORMAT
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
            data_found_list.append(rc_json_format)
            print('hi')
        '''
        return items

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


def process_items(items):
    rc_jsons_found = {}
    for item in items:
        tenant_rc_id = item.get('tenant_rc_id')
        rc_json_str = item.get('rc_json')
        rc_id = tenant_rc_id.split('_')[-1]
        rc_json = json.loads(rc_json_str)
        rc_jsons_found[rc_id] = rc_json
            
    return rc_jsons_found

def create_table(table_name= '', dynamodb= None):
    """Create the Processes Table"""
    dynamodb = get_db_session(dynamodb) if dynamodb is None else dynamodb
    from botocore.exceptions import ClientError
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'tenant_rc_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'tenant_rc_id',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
        return True
    except ClientError as ex:
        if ex.response['Error']['Code'] == 'ResourceInUseException':
            return True
        else:
            raise