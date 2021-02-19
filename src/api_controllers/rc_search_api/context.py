from functools import wraps
from flask import Flask, g, request, redirect, url_for, current_app
from exceptions import errors

HEADER_R2_USER_ID = 'x-r2-user-id'
HEADER_R2_TENANT_ID = 'x-r2-tenant-id'
HEADER_R2_USER_ROLES = 'x-r2-user-roles'

def check_user_id_in_request(request):
    if HEADER_R2_USER_ID not in request.headers:
        raise errors.UserInfoNotProvided(errors.NO_USERINFO_PROVIDED, 401)
    else:
        g.user_id = request.headers[HEADER_R2_USER_ID]

def check_tenant_id_in_request(request):
    if HEADER_R2_TENANT_ID not in request.headers:
        raise errors.TenantInfoNotProvided(errors.NO_TENANTINFO_PROVIDED, 401)
    else:
        g.tenant_id = request.headers[HEADER_R2_TENANT_ID]

def raise_error_when_no_roles_in_header(request):
    if HEADER_R2_USER_ROLES not in request.headers:
        raise errors.UserRolesNotProvided(errors.NO_USERROLES_PROVIDED, 401)

def check_if_user_roles_are_denied(request, allowed_roles, denied_roles):
    if denied_roles is not None:
        for r in denied_roles:
            roles_in_header = request.headers[HEADER_R2_USER_ROLES].replace(' ','').split(",")
            user_has_role = role_match_lists(allowed_roles, roles_in_header)
            if user_has_role:
                raise errors.ExplicitDenialForRole(denied_roles)

def evaluate_user_permission_set(resource_definition, user_permission_set):
    if resource_definition == user_permission_set:
        return True
    if resource_definition.count(":") != user_permission_set.count(":"):
        return False

    resource_definition = resource_definition.split(":")
    user_permission_set = user_permission_set.split(":")
    if len(resource_definition) != len(user_permission_set):
        return False
    match = True
    for i, rd in enumerate(resource_definition):
        us = user_permission_set[i]
        us = "" if us == "*" else us
        if not(rd == us or len(us) == 0): 
            match = False
            break
    return match

def role_match_lists(resource_set, user_set):
    for rd in resource_set:
        for ud in user_set:
            match = evaluate_user_permission_set(rd, ud)
            if match == True:
                return match
    return False

def check_if_user_roles_has_permissions(request, allowed_roles):
    if allowed_roles is not None:
        user_has_role = False
        roles_in_header = request.headers[HEADER_R2_USER_ROLES].replace(' ','').split(",")
        user_has_role = role_match_lists(allowed_roles, roles_in_header)
        # for user_role in roles_in_header:
        #     if user_role in allowed_roles:
        #         user_has_role = True
        #         break
            # check for other nomeclatures
        if user_has_role is False:
            raise errors.UserMissingAuthorization(allowed_roles)
        
def required_authorization(allowed_roles=None, denied_roles=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with current_app.app_context():
                check_user_id_in_request(request)
                check_tenant_id_in_request(request)

                from r2essentials.context import RContext, make_context
                
                g.context = make_context(g.tenant_id, g.user_id, None, request.full_path, request.method)
                
                if allowed_roles is None and denied_roles is None:
                    return func(*args, **kwargs)
                
                raise_error_when_no_roles_in_header(request)
                check_if_user_roles_are_denied(request, allowed_roles, denied_roles)
                check_if_user_roles_has_permissions(request, allowed_roles)

                return func(*args, **kwargs)
        return wrapper
    return decorator
