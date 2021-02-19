"""
Definitions of several objects that this application uses
"""
from enum import Enum
import time

class RCJSON():
  def __init__(self, tenant_id, rc_id, rc_json):
    self.tenant_id = f"{tenant_id}"
    self.rc_id = rc_id
    self.rc_json = rc_json

class RCJSON_DATAFORMAT():
  def __init__(self, name, version, isonhold, customer, value, transactional_currency_code, billed, recognized, scheduled, created_period, modified_period):
    self.name = name
    self.version = version
    self.isonhold = isonhold
    self.customer = customer
    self.value = value
    self.transactional_currency_code = transactional_currency_code
    self.billed = billed
    self.recognized = recognized
    self.scheduled = scheduled
    self.created_period = created_period
    self.modified_period = modified_period
