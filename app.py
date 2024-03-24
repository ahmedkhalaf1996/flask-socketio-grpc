from concurrent import futures
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import grpc
import Notification_pb2
import Notification_pb2_grpc
import threading
from google.protobuf.empty_pb2 import Empty


app = Flask(__name__)
app.config['SECRET_KEY'] = 'justasecretkeythatishouldputhere'

socketio = SocketIO(app)
CORS(app)

class NotificationServicer(Notification_pb2_grpc.NotificationGrpcServiceServicer):
    def SendGrpcNotification(self, request, context):
        print('Sending gRPC notification..')
        query = {"hay": "here"}
        socketio.emit('log', dict(data=str(query)))
        # You can add your logic here to send a notification over SocketIO
        return Empty()

def run_grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Notification_pb2_grpc.add_NotificationGrpcServiceServicer_to_server(NotificationServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print('gRPC server running...')
    server.wait_for_termination()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api')
def api():
    query = {"hay": "here"}
    socketio.emit('log', dict(data=str(query)))
    return False

@socketio.on('connect')
def on_connect():
    payload = dict(data='Connected')
    emit('log', payload)

if __name__ == '__main__':
    grpc_thread = threading.Thread(target=run_grpc_server)
    grpc_thread.start()
    
    socketio.run(app)
