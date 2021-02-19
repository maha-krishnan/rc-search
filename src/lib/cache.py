import zlib

class Cache(object):
    def __init__(self, host=None, port=6379,db=0, password=None, socket_timeout=None):
        from r2essentials.config import get_from_env
        self.host = host
        if host is None:
            self.host = get_from_env('REDIS_HOST', 'localhost')
        self.port = port
        self.db = db
        self.password = password
        self.socket_timeout = socket_timeout

    def __session__(self):
        import redis
        client = redis.StrictRedis(host=self.host, port=self.port, password=self.password)
        return client

    def set(self, key, value):
        client = self.__session__()
        import time
        time_to_expire_s=300
        client.set(key, zlib.compress(value.encode('utf-8')), ex=time_to_expire_s)
        return True

    def get(self, key):
        client = self.__session__()
        result = client.get(key)
        if result is None:
            return result
        result = zlib.decompress(result)
        return result.decode('utf-8')

    # def delete(self, key):
    #     client = self.__session__()
    #     result = client.delete(key)
    #     return result == 1

    # def get_values(self, pattern):
    #     client = self.__session__()
    #     keys = client.keys(pattern=pattern)
    #     return [zlib.decompress(client.get(k)).decode('utf-8') for k in keys]

    # def get_keys(self, pattern):
    #     client = self.__session__()
    #     keys = client.keys(pattern=pattern)
    #     return keys

    # def delete_keys(self, pattern):
    #     client = self.__session__()
    #     for key in client.scan_iter(pattern):
    #         client.delete(key)
    #     return True