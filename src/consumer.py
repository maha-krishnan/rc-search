import faust
import jsonpickle
import os   
import logging
import datetime

from elasticsearch import Elasticsearch, AuthenticationException
from r2essentials.context import RContext
from r2essentials.config import (get_from_env,
                                  get_bootstrap_server,
                                  get_broker_urls,
                                  get_ssl_context)
from r2essentials.fire_and_forget import fire_and_forget
from lib.workbench_process import process_stream_message
from dict2obj import Dict2Obj
from lib.config import Config, cache_session
from lib.models.model import (RCJSON)

from lib.provider.dynamo_provider import DynamoDBProvider

TOPIC = 'EndOfContractProcessing'

def get_topic():
    return get_from_env('KAFKA_TOPIC',TOPIC)

def get_group_id():
    return get_from_env('KAFKA_GROUP_ID','rcworkbench-group-id')

class RCDESKMESSAGE(faust.Record):
    context : RContext
    message: dict
    file_id: str
    goal: int
    component: str
    
app = faust.App(
    get_group_id(),
    broker=get_broker_urls(),
    broker_credentials=get_ssl_context(),
    store='rocksdb://',)

logging.info(f'Establishing Session.')
logging.info(f'Topic: {get_topic()}')
logging.info(f'Group_ID: {get_group_id()}')
logging.info(f'Bootstrap Servers: {get_bootstrap_server()}')

topic = app.topic(get_topic(), value_type=RCDESKMESSAGE)

@app.agent(topic)
async def process_message_queue(metrics_stream):
    async for payloads in metrics_stream.take(100, within=2):
        import sys
        for payload in payloads:
            print("collected:", payload)
            context = Dict2Obj(payload.context)
            metric = Dict2Obj(payload.message)
            tenant_id = f"{context.tenant_context.tenant_id}"
            table_name = "tenant_" + tenant_id[0] + "_rc_search"
            rc_id = metric.identifiers.revenue_contract_id
            jsonified = jsonpickle.encode(metric, unpicklable=False)
            item = RCJSON(tenant_id, rc_id, jsonified)
            dynamo_provider = DynamoDBProvider(connection=None, context=context)
            fire_and_forget (process_stream_message, payload, table_name, dynamo_provider, item)

if __name__ == '__main__':
    app.main()