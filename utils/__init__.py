import json
from django.http import HttpResponse, Http404

from authtokens.models import Token


def json_response(data, status=200):
    data = json.dumps(data)
    response = HttpResponse(data, content_type="application/json", status=status)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


def token_required(func):
    def inner(request, *args, **kwargs):
        if request.method == 'OPTIONS':
            return func(request, *args, **kwargs)
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if auth_header is not None:
            tokens = auth_header.split(' ')
            if len(tokens) == 2 and tokens[0] == 'Token':
                token = tokens[1]
                try:
                    request.token = Token.objects.get(token=token)
                    request.user = request.token.user
                    return func(request, *args, **kwargs)
                except Token.DoesNotExist:
                    return json_response({
                        'error': 'Token not found'
                    }, status=401)
                except Http404:
                    return json_response({
                        'error': 'Not Found'
                    }, status=404)
        return json_response({
            'error': 'Invalid Header'
        }, status=401)

    return inner


def endpoint(func):
    def inner(request, *args, **kwargs):
        if request.method == 'OPTIONS':
            return json_response({})

        response = func(request, *args, **kwargs)

        if response is None:
            return json_response({'error': "Bad Request"}, status=400)

        else:
            return response

    return inner
