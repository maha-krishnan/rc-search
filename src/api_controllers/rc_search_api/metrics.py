from json import JSONEncoder
import time
import psutil
class Metrics(JSONEncoder):
    def __init__(self, start_time, end_time, duration, route, response_code, response_length, request_length):
        self.start_time = start_time
        self.end_time = end_time
        self.route = route
        self.response_code = response_code
        self.duration = float(duration)
        self.request_length = request_length
        self.response_length = response_length
        self.memory_percent=psutil.virtual_memory().percent
        self.memory_free = psutil.virtual_memory().free
        self.memory_used = psutil.virtual_memory().used
        self.memory_active = psutil.virtual_memory().active
        self.cpu = psutil.cpu_percent(interval=None, percpu=False)
 
def before_request(request):
    """We will track metrics here"""
    # with APP.app_context():
    from flask import g
    from api_controllers.rc_search_api.context import check_user_id_in_request, check_tenant_id_in_request

    check_user_id_in_request(request)
    check_tenant_id_in_request(request)
    from r2essentials.context import make_context            
    g.context = make_context(g.tenant_id, g.user_id, None, request.full_path, request.method)
    
    g.request_length = request.content_length
    g.start_time = time.time_ns()
    g.route = request.full_path

def after_request(response):
    """We will conclude metrics and add some headers as required"""
    from flask import g
    response.headers["service-agency"] = "oingest"
    if 'start_time' in g:
        g.end_time = time.time_ns()
        g.duration = float(g.end_time - g.start_time)
        g.content_length = response.calculate_content_length()
        ctx = None
        
        metric = Metrics(start_time=g.start_time, end_time=g.end_time,
            duration=float(g.duration),
            request_length=g.request_length,
            response_length=g.content_length, route=g.route, response_code=response.status_code)

        if 'context' in g:
            response.headers["request-id"] = g.context.request_context.request_id
            ctx = g.context
        from r2essentials.eventbus.metrics import send_metrics
        send_metrics(context=ctx, metric=metric)

    return response
