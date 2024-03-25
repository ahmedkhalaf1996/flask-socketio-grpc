from concurrent import futures
import grpc
from google.protobuf.empty_pb2 import Empty
import sys

sys.path.append('protos')
import Notification_pb2
import Notification_pb2_grpc

user_connections = {}  # Define user_connections dictionary
socketio = None  # Define socketio object

class NotificationServicer(Notification_pb2_grpc.NotificationGrpcServiceServicer):
    def SendGrpcNotification(self, request, context):
        if request.mainuid not in user_connections:
            print(f"User connection not found for mainuid: {request.mainuid}")
            return Empty()

        usersocketconnid = user_connections[request.mainuid]
        print('grpc uconnid', usersocketconnid)
        msg = {
            "_id": request._id,
            "createdAt": request.createdAt,
            "deatils": request.deatils,
            "isreded": request.isreded,
            "mainuid": request.mainuid,
            "targetid": request.targetid,
            "user": {
                "avatar": request.user.avatar,
                "name": request.user.name
            }
        }
        if socketio and usersocketconnid:
            socketio.emit('notification', dict(data=str(msg)), room=usersocketconnid)
        else:
            print("SocketIO not initialized. Notification not sent.")
        # You can add your logic here to send a notification over SocketIO
        return Empty()

def run_grpc_server():
    global user_connections, socketio
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Notification_pb2_grpc.add_NotificationGrpcServiceServicer_to_server(NotificationServicer(), server)
    server.add_insecure_port('[::]:8090')
    server.start()
    print('gRPC server running...')
    server.wait_for_termination()

def set_user_connections(connections):
    global user_connections
    user_connections = connections

def set_socketio(io):
    global socketio
    socketio = io
