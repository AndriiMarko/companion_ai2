import socket
import threading
import json
import struct
import os
import uuid
import logging
import signal
from ollama_char import OllamaCharacter

server_stop = False

# Load settings
with open(os.path.join(os.path.dirname(__file__), '../config/settings.json'), 'r', encoding='utf-8') as f:
    config = json.load(f)

HOST = config.get("HOST", "127.0.0.1")
PORT = config.get("PORT", 55555)
MODEL_NAME = config.get("model_name", "deepseek-r1-14b-q4")
BASE_URL = config.get("base_url", "http://localhost:11434")

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# Store all generated UUIDs
uuids = set()

def generate_unique_uid():
    while True:
        new_uid = str(uuid.uuid4())
        if new_uid not in uuids:
            uuids.add(new_uid)
            return new_uid

def handle_client(conn, addr):
    global server_stop
    logging.info(f"Connection from {addr}")
    try:
        first_message = True
        character = None
        conversation_id = None
        character_name = None
        while not server_stop:
            raw_size = conn.recv(4)
            if not raw_size:
                logging.info(f"Connection closed by {addr}")
                break
            json_size = struct.unpack('<I', raw_size)[0]
            data = b''
            while len(data) < json_size:
                packet = conn.recv(json_size - len(data))
                if not packet:
                    break
                data += packet
            if not data:
                logging.info(f"No data received from {addr}")
                break
            request = json.loads(data.decode('utf-8'))
            print(request)

            # If first message and conversation_id == 0, generate and send UID
            if first_message and request.get('conversation_id', 0) == 0:
                new_uid = generate_unique_uid()
                logging.info(f"Generated new UID {new_uid} for {addr}")
                response = {"uid": new_uid}
                response_json = json.dumps(response, ensure_ascii=False).encode('utf-8')
                response_size = struct.pack('<I', len(response_json))
                conn.sendall(response_size + response_json)
                first_message = False
                continue

            # On first real chat message, create OllamaCharacter
            if character is None:
                user_input = request.get('input', '')
                conversation_id = request.get('conversation_id', 0)
                character_name = request.get('character_name', 'Clara')
                logging.info(f"Creating OllamaCharacter for {character_name} (conversation_id={conversation_id})")
                character = OllamaCharacter(
                    character_name=character_name,
                    conversation_id=conversation_id,
                    model=MODEL_NAME,
                    base_url=BASE_URL
                )
            else:
                user_input = request.get('input', '')

            logging.info(f"Received input from {addr}: {user_input}")
            response = character.respond(user_input)
            response_json = json.dumps(response, ensure_ascii=False).encode('utf-8')
            response_size = struct.pack('<I', len(response_json))
            conn.sendall(response_size + response_json)
            first_message = False
    except Exception as e:
        logging.error(f"Error handling client {addr}: {e}")
    finally:
        conn.close()
        logging.info(f"Connection with {addr} closed.")

def sigint_handler(signum, frame):
    logging.info("SIGINT received, shutting down server.")
    server_stop = True
    exit(0)

signal.signal(signal.SIGINT, sigint_handler)

def main():
    global server_stop
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            logging.info(f"Server listening on {HOST}:{PORT}")
            while not server_stop:
                conn, addr = s.accept()
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        logging.info("Server stopped by user (Ctrl+C).")

if __name__ == '__main__':
    main()