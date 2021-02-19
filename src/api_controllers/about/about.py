"""
Default Root Route. We will simply show health of the service
"""

from flask import Blueprint
from flask_responses import json_response
import socket
ABOUT_ROUTE = Blueprint('about', __name__)

@ABOUT_ROUTE.route("/healthz")
def about():
    """Returns simple health status"""
    dictionary= {'Service': 'RC-SEARCH', 
        'Host': socket.gethostname()}
    return json_response(data=dictionary, 
        status_code=200)
