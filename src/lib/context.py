
class RequestContext():
    def __init__(self, request_id: str, resource: str, command: str):
        self.request_id = request_id
        self.resource = resource
        self.command = command

class TenantContext():
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

class UserContext():
    def __init__(self, user_id: str,
        user_email: str, user_token: str, 
        user_session: str):
        if user_id is not None:
            self.user_id = user_id
        else:
            self.user_id = user_email
        self.user_email = user_email
        self.user_token = user_token
        self.user_session = user_session

class RContext():
    def __init__(self, tenant_context: TenantContext=None, 
        user_context: UserContext=None, request_context=None):
        self.tenant_context = tenant_context
        self.user_context = user_context
        self.request_context = request_context

def make_context(tenant_id, user_id, session_id, resource, command) -> RContext:
    t_context = TenantContext(tenant_id=tenant_id)
    u_context = UserContext(user_id=user_id, user_email=None, user_token=None, user_session=session_id)
    import uuid
    r_context = RequestContext(request_id=str(uuid.uuid4()), resource=resource, command=command)
    return RContext(tenant_context=t_context, user_context=u_context, request_context=r_context)
