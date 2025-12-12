import sys
import os
from django.core.asgi import get_asgi_application
from test_utils.boot_django import boot_django, BASE_DIR, FAKE_APP_DIR

sys.path.append(BASE_DIR)
sys.path.append(FAKE_APP_DIR)

boot_django()

from django.conf import settings
from django_socio_grpc.settings import grpc_settings

# Enable Async mode for gRPC
settings.GRPC_FRAMEWORK["GRPC_ASYNC"] = True
grpc_settings.reload()

from django_socio_grpc.grpc_web import grpcASGI
from fakeapp.handlers import grpc_handlers

application = grpcASGI(get_asgi_application())

async def debug_application(scope, receive, send):
    print(f"Request received: {scope['type']} {scope.get('path', '')}")
    await application(scope, receive, send)

grpc_handlers(application)
# Use the debug wrapper
final_application = debug_application
