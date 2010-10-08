import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt



def json_response( json_object ):
    """Returns an HttpResponse object with serialized json
    """
    return HttpResponse( json.dumps(json_object) )


@csrf_exempt
def connect(request):
    # accept all connect requests and assume they are from 'guest'
    return json_response( [ True, {"name":"guest"} ] )


@csrf_exempt
def disconnect(request):
    return json_response( [ True, {} ] )


@csrf_exempt
def create_channel(request):
    # accept all create channel requests. in this example,
    # only one channel is ever created: 'chan1'
    return json_response([ True, { "history_size" : 0, 
                                "reflective" : True, 
                                "presenceful" : True } ])


@csrf_exempt
def subscribe(request):
    return json_response([ True, {} ])


@csrf_exempt
def unsubscribe (self):
    return json_response([ True, {} ])


@csrf_exempt
def publish (self):
    return json_response([ True, {} ])


