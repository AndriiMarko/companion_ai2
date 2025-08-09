import socket
import threading
import json
import struct
import os
from ollama_char import OllamaCharacter

# Load settings
with open(os.path.join(os.path.dirname(__file__), '../config/settings.json'), 'r', encoding='utf-8') as f:
    config = json.load(f)

HOST = config.get("HOST", "127.0.0.1")
PORT = config.get("PORT", 55555)
MODEL_NAME = config.get("model_name", "deepseek-r1-14b-q4")
BASE_URL = config.get("base_url", "http://localhost:11434")

# You can manage multiple conversations by storing them in a dict
characters = {}

def handle_client(conn, addr):
    try:
        # Receive the first message to get conversation_id and character_name
        raw_size = conn.recv(4)
        if not raw_size:
            conn.close()
            return
        json_size = struct.unpack('<I', raw_size)[0]
        data = b''
        while len(data) < json_size:
            packet = conn.recv(json_size - len(data))
            if not packet:
                conn.close()
                return
            data += packet
        if not data:
            conn.close()
            return
        request = json.loads(data.decode('utf-8'))
        user_input = request.get('input', '')
        conversation_id = request.get('conversation_id', 0)
        character_name = request.get('character_name', 'Clara')

        # Create OllamaCharacter instance for this connection
        character = OllamaCharacter(
            character_name=character_name,
            conversation_id=conversation_id,
            model=MODEL_NAME,
            base_url=BASE_URL
        )

        # Respond to the first message
        response = character.respond(user_input)
        response_json = json.dumps(response, ensure_ascii=False).encode('utf-8')
        response_size = struct.pack('<I', len(response_json))
        conn.sendall(response_size + response_json)

        # Handle subsequent messages
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
            user_input = request.get('input', '')
            # Only call respond, do not recreate character
            response = character.respond(user_input)
            response_json = json.dumps(response, ensure_ascii=False).encode('utf-8')
            response_size = struct.pack('<I', len(response_json))
            conn.sendall(response_size + response_json)
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