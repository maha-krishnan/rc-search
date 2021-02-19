import time
import logging
from flask import Flask, jsonify, g, request
from exceptions import errors
import json
import click
import datetime, sys, json_logging

APP = Flask(__name__)

json_logging.init_flask(enable_json=True)
json_logging.init_request_instrument(APP)

# init the logger as usual
logger = logging.getLogger("rcmetrics-rest")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))


def register_blueprints():
    """We will register flask blueprints here"""
    from api_controllers.rc_search_api.rc_search_rest import RC_SEARCH_ROUTE
    APP.register_blueprint(RC_SEARCH_ROUTE)

register_blueprints()

def context():
    from functools import wraps
    from flask import Flask, g, request, redirect, url_for, current_app
    from exceptions import errors

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with APP.app_context():
                if 'x-r2-user-id' not in request.headers:
                    raise errors.UserInfoNotProvided(errors.NO_USERINFO_PROVIDED, 401)
                else:
                    g.user_id = request.headers['x-r2-user-id']
                
                if 'x-r2-tenant-id' not in request.headers:
                    raise errors.TenantInfoNotProvided(errors.NO_TENANTINFO_PROVIDED, 401)
                else:
                    g.tenant_id = request.headers['x-r2-tenant-id']
                from r2essentials.context import RContext, make_context
                g.context = make_context(g.tenant_id, g.user_id, None, request.full_path, request.method)
                return func(*args, **kwargs)
        return wrapper
    return decorator


@APP.errorhandler(errors.TenantInfoNotProvided)
@APP.errorhandler(errors.UserInfoNotProvided)
@APP.errorhandler(errors.UserRolesNotProvided)
@APP.errorhandler(errors.ExplicitDenialForRole)
@APP.errorhandler(errors.UserMissingAuthorization)
def context_error_handler(error):
    """R2Context error handler"""
    error = error.__dict__
    import json
    response = jsonify(message=error['error_message'])
    response.status_code = error['response_code']
    return response
