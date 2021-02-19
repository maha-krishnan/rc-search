"""
Core logic of the application resides here.
"""
import requests
import logging
import jsonpickle, json
from r2essentials.context import RContext
from r2essentials.fire_and_forget import fire_and_forget
from r2essentials.eventbus.utils import get_bridge
from dict2obj import Dict2Obj
from r2essentials.metrics import end
from r2essentials.config import get_from_env, get_security_protocol, get_ssl_context
from enum import Enum
import configs.config as cfg
from lib.config import cache_session
from lib.models.model import RCJSON
import datetime

TARGET_QUEUE = 'MetricsCreatedQueue'

is_dev, is_test = cfg.mode()

async def process_stream_message(payload, table_name, dynamo_provider, p : RCJSON):
    context = Dict2Obj(payload.context)
    start_time = str(datetime.datetime.now())
    
    fire_and_forget(create_update_rc_search_table,
                        table_name, context, dynamo_provider, p, start_time)

    return

async def create_update_rc_search_table(table_name, context, dynamo_provider, item: RCJSON, start_time=None):
    """
    now we are missings fids that are missing and gids that are missing
    so we register the gid, to get new revenue ids and we will assign
    these revenue ids to fids that are missing
    """
    
    status = dynamo_provider.write_rc_json(table_name, item)
    dynamo_provider.fetch_items(table_name)
    if status:
        logging.info("Data successfully stored in Dynamo DB: " + str(table_name))
    else:
        logging.error("Exception in storing data")

def requests_fetch_url(url_type, url, data={}, files=None, headers={}):
    import requests
    response = requests.request(
        url_type,
        url=url,
        data=data,
        files=files,
        headers=headers,
    )
    return response

def make_header_info(context: RContext, user_roles: str):
    return {'X-R2-USER-ID': context.user_context.user_id, 'x-r2-tenant-id': context.tenant_context.tenant_id, 'x-r2-user-roles': user_roles}
      
def announce(context, rc_json, rc_metrics_json, file_id, start_time=None):
    payload = RCMetricsUpdatedMessage(context, rc_json, rc_metrics_json, file_id)
    rc_guid = rc_json['identifiers']['revenue_contract_guid']
    fire_and_forget(produce_message, context,
                    payload, rc_guid, file_id, start_time)

class RCMetricsUpdatedMessage():
    def __init__(self, context, rc_json, rc_metrics_json, file_id):
        self.context = context
        self.message_rc_json = rc_json
        self.rc_metrics_json = rc_metrics_json
        self.file_id = file_id

async def produce_message(context, payload, rc_guid, file_id, start_time=None):

    from kafka import KafkaProducer
    producer = KafkaProducer(bootstrap_servers=get_bridge('KAFKA_BOOTSTRAP_SERVER'),
                             security_protocol=get_security_protocol(),
                             ssl_context=get_ssl_context(),
                             key_serializer=lambda v: v.encode('utf-8'),
                             value_serializer=lambda v: jsonpickle.encode(v, unpicklable=False).encode('utf-8'))

    producer.send(TARGET_QUEUE, key=rc_guid, value=payload)
    producer.flush()
    end_time = str(datetime.datetime.now())
    notify_elrond(context, payload, "Completed", 1, 0,
                  payload.file_id, start_time, end_time)
    return True


async def send_alert_message(context, message, file_id, err):
    from lib.globals import DOMAIN_CONTEXT, DOMAIN
    from r2essentials.eventbus import alerts
    event_header = alerts.AlertHeader(domain=DOMAIN,
                                      domain_context=DOMAIN_CONTEXT,
                                      severity=alerts.AlertSeverity.FAILED,
                                      source_reference=file_id)

    event = alerts.AlertSchema(header=event_header,
                               simple_description=err,
                               payload=message,
                               corrective_action=err)
    event.send_alert(context=context)


def notify_elrond(context: RContext, message, status, total_records, success_count, file_id, start_time=None, end_time=None):
    input_record = {
        "session_info": {
            "source": "rc_metrics",
            "source_id": file_id,
            "linked_document": f"/external/v1/orders-upload/download/{file_id}",
        },
        "stages": [{
            "status": status,
            "stage": "rc_metrics",
            "measurements": {
                "total_records": total_records,
                "is_rule_associated": success_count,
            },
            "process_time": {
                "start_time": start_time,
                "end_time": end_time
            },
            "aggregators": ["total_records", "is_rule_associated"],
        },
        ],
    }
    from r2essentials.eventbus import process_monitor
    process_monitor.broadcast_progress(context, input_record)

def read_json_from_file(path):
    import os, json
    test_dir = os.path.dirname(__file__)
    test_dir = '/'.join(test_dir.split('/')[:-1])
    abs_file_path = os.path.join(test_dir, path)
    with open(abs_file_path) as file:
        data = json.load(file)
    return data

if __name__ == "__main__":
    pass