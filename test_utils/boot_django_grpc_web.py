import sys
import json
import asyncio
from django.core.asgi import get_asgi_application
from test_utils.boot_django import boot_django, BASE_DIR, FAKE_APP_DIR
from asgiref.testing import ApplicationCommunicator

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
grpc_handlers(application)

async def run_test():
    print("Starting test...")
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/myproject.fakeapp.BasicController/FetchDataForUser",
        "headers": [
            (b"content-type", b"application/json"),
        ],
    }
    communicator = ApplicationCommunicator(application, scope)
    await communicator.send_input({
        "type": "http.request",
        "body": json.dumps({"user_name": "testuser"}).encode("utf-8"),
    })
    
    print("Waiting for response...")
    response_start = await communicator.receive_output(timeout=5)
    print(f"Response start: {response_start}")
    assert response_start["type"] == "http.response.start"
    assert response_start["status"] == 200
    
    response_body = await communicator.receive_output(timeout=5)
    print(f"Response body: {response_body}")
    assert response_body["type"] == "http.response.body"
    
    body = json.loads(response_body["body"])
    print(f"Decoded body: {body}")
    
    # Verify content
    if "userName" in body:
        assert body["userName"] == "testuser"
    else:
        assert body["user_name"] == "testuser"
        
    print("Test passed!")

if __name__ == "__main__":
    asyncio.run(run_test())
