from exceptions import errors

class IProvider():
  def __init__(self, connection, context):
    self.connection = connection
    self.context = context