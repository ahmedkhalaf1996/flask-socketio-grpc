from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import threading
from grpc_se.grpc_server import run_grpc_server, set_user_connections, set_socketio

app = Flask(__name__)
app.config['SECRET_KEY'] = 'justasecretkeythatishouldputhere'

socketio = SocketIO(app,  debug=False)
CORS(app)
user_connections = {}  # Define user_connections dictionary

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
    set_user_connections(user_connections)  # Set the user_connections dictionary in the server module
    set_socketio(socketio)  # Set the socketio object in the server module
    grpc_thread = threading.Thread(target=run_grpc_server)
    grpc_thread.start()

    socketio.run(app, port=8088)
