# Save as chat_client.py
import socket
import struct
import json
import tkinter as tk
from tkinter import scrolledtext
import threading
import os

# Load settings
with open(os.path.join(os.path.dirname(__file__), '../config/settings.json'), 'r', encoding='utf-8') as f:
    config = json.load(f)

HOST = config.get("HOST", "127.0.0.1")
PORT = config.get("PORT", 55555)
MODEL_NAME = config.get("model_name", "deepseek-r1-14b-q4")
BASE_URL = config.get("base_url", "http://localhost:11434")

class ChatClient:
    def __init__(self, master):
        self.master = master
        master.title("Ollama Character Chat")

        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, state='disabled', width=60, height=20)
        self.text_area.pack(padx=10, pady=10)

        self.entry = tk.Entry(master, width=50)
        self.entry.pack(side=tk.LEFT, padx=(10,0), pady=(0,10))
        self.entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(master, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=(5,10), pady=(0,10))

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.character_name = "Clara"

        # Load or request conversation_id (uid)
        save_path = os.path.join(os.path.dirname(__file__), "../client_saves/save.txt")
        if os.path.exists(save_path):
            try:
                with open(save_path, "r", encoding="utf-8") as f:
                    self.conversation_id = f.read().strip()
            except Exception:
                self.conversation_id = "0"
        else:
            self.conversation_id = "0"

        if self.conversation_id == "0" or not self.conversation_id:
            # Request UID from server
            request = {"conversation_id": 0}
            data = json.dumps(request, ensure_ascii=False).encode('utf-8')
            size = struct.pack('<I', len(data))
            self.sock.sendall(size + data)
            raw_size = self.sock.recv(4)
            if raw_size:
                resp_size = struct.unpack('<I', raw_size)[0]
                resp_data = b''
                while len(resp_data) < resp_size:
                    packet = self.sock.recv(resp_size - len(resp_data))
                    if not packet:
                        break
                    resp_data += packet
                if resp_data:
                    response = json.loads(resp_data.decode('utf-8'))
                    self.conversation_id = response.get("uid", "0")
                    # Save UID to file
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(self.conversation_id)

    def send_message(self, event=None):
        user_input = self.entry.get()
        if not user_input.strip():
            return
        self.display_message(f"You: {user_input}")
        self.entry.delete(0, tk.END)
        # Start a new thread for network communication
        threading.Thread(target=self.send_and_receive, args=(user_input,), daemon=True).start()

    def send_and_receive(self, user_input):
        try:
            request = {
                "input": user_input,
                "conversation_id": self.conversation_id,
                "character_name": self.character_name
            }
            data = json.dumps(request, ensure_ascii=False).encode('utf-8')
            size = struct.pack('<I', len(data))
            self.sock.sendall(size + data)

            # Receive response
            raw_size = self.sock.recv(4)
            if not raw_size:
                self.display_message("Disconnected from server.")
                return
            resp_size = struct.unpack('<I', raw_size)[0]
            resp_data = b''
            while len(resp_data) < resp_size:
                packet = self.sock.recv(resp_size - len(resp_data))
                if not packet:
                    break
                resp_data += packet
            if not resp_data:
                self.display_message("Disconnected from server.")
                return
            response = json.loads(resp_data.decode('utf-8'))
            answer = response.get('answer', '')
            # Use after() to safely update the UI from the thread
            self.master.after(0, lambda: self.display_message(f"{self.character_name}: {answer}"))
        except Exception as e:
            self.master.after(0, lambda: self.display_message(f"Error: {e}"))

    def display_message(self, message):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state='disabled')

    def close(self):
        self.sock.close()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.protocol("WM_DELETE_WINDOW", client.close)
    root.mainloop()