from concurrent import futures
from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import grpc
import sys 
sys.path.append('protos')
import Notification_pb2
import Notification_pb2_grpc
import threading
from google.protobuf.empty_pb2 import Empty


app = Flask(__name__)
app.config['SECRET_KEY'] = 'justasecretkeythatishouldputhere'

socketio = SocketIO(app)
CORS(app)
user_connections = {}  # Store user connections

# grpc start 
class NotificationServicer(Notification_pb2_grpc.NotificationGrpcServiceServicer):
    def SendGrpcNotification(self, request, context):
        if request.mainuid not in user_connections:
            print(f"User connection not found for mainuid: {request.mainuid}")
            return Empty()


        usersocketconnid = user_connections[request.mainuid]
        print('grpc uconnid', usersocketconnid)
        msg = {
            "_id": request._id,
            "createdAt":request.createdAt,
            "deatils": request.deatils,
            "isreded": request.isreded,
            "mainuid": request.mainuid,
            "targetid": request.targetid,
            "user": {
                "avatar": request.user.avatar,
                "name": request.user.name
            }
        }
        socketio.emit('notification', dict(data=str(msg)), room=usersocketconnid)
        # You can add your logic here to send a notification over SocketIO
        return Empty()

def run_grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Notification_pb2_grpc.add_NotificationGrpcServiceServicer_to_server(NotificationServicer(), server)
    server.add_insecure_port('[::]:8090')
    server.start()
    print('gRPC server running...')
    server.wait_for_termination()

# grpc end 

@socketio.on('connect')
def on_connect():
    print("user Connected")


@socketio.on('setUserId')
def handle_set_user_id(user_id):
    if user_id:
        try:
            user_connections[user_id] = request.sid
            print(f'User {user_id} connected with socket id {request.sid}')

            return 'User ID set successfully'

        except Exception as e:
            print(f"Error setting user ID: {e}")

    return 'Failed to set user ID'

@socketio.on('disconnect')
def handle_disconnect():
    user_id = next((uid for uid, sid in user_connections.items() if sid == request.sid), None)
    if user_id:
        print(f"User disconnected: {user_id}")  # Print user ID before deletion
        if user_id in user_connections:
            del user_connections[user_id]  # Remove user ID from dictionary
    else:
        print('An unidentified user disconnected')


if __name__ == '__main__':
    grpc_thread = threading.Thread(target=run_grpc_server)
    grpc_thread.start()
    
    socketio.run(app,  port=8088)
