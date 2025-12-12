import sys
import asyncio
import sonora.aio
from test_utils.boot_django import BASE_DIR, FAKE_APP_DIR

sys.path.append(BASE_DIR)
sys.path.append(FAKE_APP_DIR)

from fakeapp.grpc import fakeapp_pb2
from fakeapp.grpc import fakeapp_pb2_grpc
from google.protobuf import empty_pb2

async def run_client():
    print("Connecting to http://localhost:8008")
    # Create a Sonora channel
    async with sonora.aio.insecure_web_channel("http://localhost:8008") as channel:
        stub = fakeapp_pb2_grpc.BasicControllerStub(channel)
        
        print("Sending request...")
        try:
            response = await stub.FetchDataForUser(
                fakeapp_pb2.BasicFetchDataForUserRequest(user_name="sonora_user")
            )
            
            print("Received response:")
            print(response)
            
            assert response.user_name == "sonora_user"
            print("Unary Test passed!")

            print("Sending streaming request...")
            async for response in stub.StreamExample(empty_pb2.Empty()):
                print(f"Received stream response: {response.name}")
            
            print("Streaming Test passed!")

        except Exception as e:
            print(f"Request failed: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(run_client())
