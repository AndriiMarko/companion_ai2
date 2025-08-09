import socket
import threading
import json
import struct
import os
import uuid
from ollama_char import OllamaCharacter

# Load settings
with open(os.path.join(os.path.dirname(__file__), '../config/settings.json'), 'r', encoding='utf-8') as f:
    config = json.load(f)

HOST = config.get("HOST", "127.0.0.1")
PORT = config.get("PORT", 55555)
MODEL_NAME = config.get("model_name", "deepseek-r1-14b-q4")
BASE_URL = config.get("base_url", "http://localhost:11434")

# Store all generated UUIDs
uuids = set()

def generate_unique_uid():
    while True:
        new_uid = str(uuid.uuid4())
        if new_uid not in uuids:
            uuids.add(new_uid)
            return new_uid

def handle_client(conn, addr):
    try:
        first_message = True
        character = None
        conversation_id = None
        character_name = None
        while True:
            raw_size = conn.recv(4)
            if not raw_size:
                break
            json_size = struct.unpack('<I', raw_size)[0]
            data = b''
            while len(data) < json_size:
                packet = conn.recv(json_size - len(data))
                if not packet:
                    break
                data += packet
            if not data:
                break
            request = json.loads(data.decode('utf-8'))

            # If first message and conversation_id == 0, generate and send UID
            if first_message and request.get('conversation_id', 0) == 0:
                new_uid = generate_unique_uid()
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
                character = OllamaCharacter(
                    character_name=character_name,
                    conversation_id=conversation_id,
                    model=MODEL_NAME,
                    base_url=BASE_URL
                )
            else:
                user_input = request.get('input', '')

            response = character.respond(user_input)
            response_json = json.dumps(response, ensure_ascii=False).encode('utf-8')
            response_size = struct.pack('<I', len(response_json))
            conn.sendall(response_size + response_json)
            first_message = False
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            print(f"Server listening on {HOST}:{PORT}")
            while True:
                conn, addr = s.accept()
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\nServer stopped by user.")

if __name__ == '__main__':
    main()