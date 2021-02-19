from lib.provider.dynamodb import data_persistance
from lib.models.model import RCJSON
from lib.provider.interface import IProvider
import jsonpickle
from r2essentials.context import RContext
import typing


class DynamoDBProvider(IProvider):
    def __init__(self, connection, context: RContext):
        self.connection = connection
        self.context = context

    def __common__reader__(self, result, raise_error):
        if result is None:
            raise raise_error
        return result

    def write_rc_json(self, table_name, source: RCJSON):
        """Writes rc currency information to grouping_id partition"""

        table_obj = data_persistance.get_table(table_name)
        status = data_persistance.new_item(table_name, source, self.connection)
        #source2 = RCJSON(source.tenant_id, "RC-3", source.rc_json)
        #status = data_persistance.new_item(table_name, source2, self.connection)
        return 200 == status['ResponseMetadata']['HTTPStatusCode']

    def fetch_items(self, table_name):
        #data_persistance.get_item(table_name, 'fbook', 'RC-2')
        status = data_persistance.get_table(table_name)
        if not status:
            return {}
        return data_persistance.get_all_items(table_name)
