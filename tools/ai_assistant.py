import sys
import requests
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QPushButton,
    QComboBox, QApplication, QLabel, QSizePolicy, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import re
import markdown2
import json
import os
from PyQt6.QtGui import QTextCursor
from tools.utilities import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path, ai_chatlogs_dir
)


OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODELS = [
    "qwen3:14b",
    "gemma3:12b",
    "deepseek-r1:14b",
    "mistral-small3.1",
    "qwen3:8b",
    "gemma3:4b",
    "phi4-mini:3.8b",
    "gemma3:2b",
    "tinyllama:1.1b",
    "phi4:14b",
    "phi4-reasoning:14b",
    "mathstral:7b",
    "deepseek-r1:7b",
    "codegemma:2b",
    "codegemma:7b",
    "dolphin3:8b"
]

MODEL_TOOLTIPS = {
    "qwen3:14b": "Very smart, very slow. Only use if you have lots of RAM.",
    "gemma3:12b": "Accurate but heavy. Best for deep analysis.",
    "deepseek-r1:14b": "Logic-oriented. High memory use.",
    "mistral-small3.1": "Fast, fluent, long context. Good fallback.",
    "qwen3:8b": "Balanced power and speed. Good for detailed answers.",
    "gemma3:4b": "Compact and quick. Reliable across tasks.",
    "phi4-mini:3.8b": "Very fast, good for basic reasoning.",
    "gemma3:2b": "Tiny and fast. Best for short replies.",
    "tinyllama:1.1b": "Ultra light. Works on very weak machines.",
    "phi4:14b": "Excellent logic, good for Learn mode.",
    "phi4-reasoning:14b": "Great at reasoning. Slow but smart.",
    "mathstral:7b": "Math specialist. Best for calculations and logic.",
    "deepseek-r1:7b": "Smaller reasoning model. Good tradeoff.",
    "codegemma:2b": "Fast coding assistant. For quick help.",
    "codegemma:7b": "Stronger code helper. Slightly slower.",
    "dolphin3:8b": "Balanced for all tasks. Recommended default."
}

MODE_PROMPTS = [
    "Please explain your reasoning and steps like a helpful teacher.",
    "Just give the direct answer, no explanation.",
    ""
]

import tiktoken

def estimate_tokens(messages, model="gpt-3.5-turbo"):  # Works with GPT-style models
    enc = tiktoken.encoding_for_model(model)
    total = 0
    for role, msg in messages:
        total += len(enc.encode(role)) + len(enc.encode(msg)) + 4
    return total

def load_tool_knowledge():
    try:
        from utilities import knowledge_path
        with open(knowledge_path, "r", encoding="utf-8") as f:

            knowledge = json.load(f)
            about = knowledge.get("about", {})
            tools = knowledge.get("tools", {})

            intro = (
                f"You are the local AI assistant for Science Hub, a modular offline science platform created by {about.get('creator', 'Pablo Oeffner Ferreira')}.\n"
                f"Do not describe the app or its tools unless the user directly asks about them.\n"
                f"Do not advertise, explain, or summarize Science Hub unless prompted.\n"
                f"Your job is to assist with science, coding, and reasoning. If a tool could help with a user’s question, you may briefly mention it by name—but only when clearly relevant.\n\n"
                f"If the user just says hello or greets you casually, respond briefly and do not explain anything unless asked.\n\n"
                f"The following tools are registered in Science Hub (you may refer to them *only when necessary*):\n"
            )

            tool_summary = "\n".join(f"- {name}: {desc}" for name, desc in tools.items())

            return intro + tool_summary
    except Exception as e:
        return "You are the AI assistant for Science Hub. Tool knowledge is unavailable."

class OllamaWorker(QThread):
    response_ready = pyqtSignal(str)
    error = pyqtSignal(str)
    model_missing = pyqtSignal(str)
    partial_response = pyqtSignal(str)  # new signal for live typing output

    def __init__(self, messages, model, mode_idx):
        super().__init__()
        self.messages = messages
        self.model = model
        self.mode_idx = mode_idx

    def run(self):
        ollama_messages = []
        if self.mode_idx == 2:
            system_prompt = load_tool_knowledge()
        else:
            system_prompt = MODE_PROMPTS[self.mode_idx]

        if system_prompt.strip():
            ollama_messages.append({"role": "system", "content": system_prompt})
        for who, msg in self.messages:
            if who == "user":
                ollama_messages.append({"role": "user", "content": msg})
            else:
                ollama_messages.append({"role": "assistant", "content": msg})

        payload = {"model": self.model, "messages": ollama_messages}
        try:
            resp = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=120)
            resp.raise_for_status()

            reply_chunks = []
            for line in resp.iter_lines(decode_unicode=True):
                if line.strip():
                    try:
                        data = json.loads(line)
                        part = data.get("message", {}).get("content", "")
                        if part:
                            self.partial_response.emit(part)
                            reply_chunks.append(part)
                    except json.JSONDecodeError:
                        continue  # skip malformed chunks

            full_reply = "".join(reply_chunks).strip() or "No response."
            self.response_ready.emit(full_reply)

        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                try:
                    err_msg = e.response.text.lower()
                    if "not found" in err_msg and "model" in err_msg:
                        self.model_missing.emit(self.model)
                        return
                    short = err_msg[:200]
                except Exception:
                    short = "<unable to read error text>"
            else:
                short = "<no response object>"
            self.error.emit(f"HTTP Error: {e}\nServer said: {short}")

        except Exception as e:
            self.error.emit(f"Unhandled error: {e}")

class AIAssistantWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Assistant (Ollama)")
        self.setMinimumSize(700, 540)
        self.messages = []

        main_layout = QVBoxLayout(self)

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Model:"))
        self.model_picker = QComboBox()
        self.model_picker.addItems(OLLAMA_MODELS)
        for i in range(self.model_picker.count()):
            model_name = self.model_picker.itemText(i)
            tooltip = MODEL_TOOLTIPS.get(model_name, "No description available.")
            self.model_picker.setItemData(i, tooltip, Qt.ItemDataRole.ToolTipRole)
        self.model_picker.setCurrentText("dolphin3:8b")
        self.model_picker.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        top_layout.addWidget(self.model_picker)

        self.mode_selector = QComboBox()
        self.mode_selector.addItems([
            "Learn (explanation, teacher mode)",
            "Use (just answer)",
            "Casual (Assistant)"
        ])
        self.mode_selector.setCurrentIndex(2)
        top_layout.addWidget(self.mode_selector)

        self.save_btn = QPushButton("Save Chat")
        self.save_btn.clicked.connect(self.save_chat)
        top_layout.addWidget(self.save_btn)

        self.clear_btn = QPushButton("Clear Chat")
        self.clear_btn.clicked.connect(self.clear_chat)
        top_layout.addWidget(self.clear_btn)

        main_layout.addLayout(top_layout)

        self.load_btn = QPushButton("Load Chat")
        self.load_btn.clicked.connect(self.load_chat)
        top_layout.addWidget(self.load_btn)

        self.token_label = QLabel("Tokens: 0")
        self.token_label.setStyleSheet("font-size: 12px;")
        main_layout.addWidget(self.token_label)

        input_layout = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type your question here and press Enter...")
        self.input.returnPressed.connect(self.send)
        input_layout.addWidget(self.input)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send)
        input_layout.addWidget(self.send_btn)

        main_layout.addLayout(input_layout)

        
        from PyQt6.QtWidgets import QTextBrowser
        self.chatbox = QTextBrowser()
        self.chatbox.setReadOnly(True)
        main_layout.addWidget(self.chatbox)

    def prompt_model_download(self, model_name):
        reply = QMessageBox.question(
            self,
            "Model Not Found",
            f"The model '{model_name}' is not installed.\nDo you want to download it now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            import subprocess
            subprocess.run(["ollama", "pull", model_name])
            QMessageBox.information(self, "Download Complete", f"Model '{model_name}' installed.\nTry again.")
        else:
            self.handle_error(f"Model '{model_name}' not installed.")

    def send(self):
        user_msg = self.input.text().strip()
        if not user_msg:
            return
        self.input.clear()
        self.messages.append(("user", user_msg))
        self.update_chat()
        self.send_btn.setDisabled(True)
        self.input.setDisabled(True)

        self.worker = OllamaWorker(
            self.messages,
            self.model_picker.currentText(),
            self.mode_selector.currentIndex()
        )
        self.worker.partial_response.connect(self.append_partial)  # move it here!
        self.worker.response_ready.connect(self.receive)
        self.worker.error.connect(self.handle_error)
        self.worker.model_missing.connect(self.prompt_model_download)
        self.worker.start()
            
    def append_partial(self, chunk):
        cursor = self.chatbox.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(chunk)
        self.chatbox.setTextCursor(cursor)

    
    @staticmethod
    def remove_emojis(text):
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002700-\U000027BF"  # dingbats
            "\U0001F900-\U0001F9FF"  # supplemental symbols
            "\U00002600-\U000026FF"  # miscellaneous
            "]+", flags=re.UNICODE
        )
        return emoji_pattern.sub("", text)

    def receive(self, ai_msg):
        ai_msg_clean = self.remove_emojis(ai_msg)
        self.messages.append(("ai", ai_msg_clean))
        self.update_chat()
        self.send_btn.setDisabled(False)
        self.input.setDisabled(False)
        self.input.setFocus()


    def handle_error(self, error_msg):
        QMessageBox.critical(self, "Ollama Error", error_msg)
        self.send_btn.setDisabled(False)
        self.input.setDisabled(False)

    def update_chat(self):
        html = ""
        for who, msg in self.messages:
            prefix = "<b>You:</b>" if who == "user" else "<b>AI:</b>"
            body = markdown2.markdown(msg)
            html += f"{prefix}<br>{body}<br><br>"
        self.chatbox.setHtml(html)
        self.chatbox.setStyleSheet("QTextBrowser { padding: 8px; font-size: 12pt; }")


        self.chatbox.verticalScrollBar().setValue(self.chatbox.verticalScrollBar().maximum())
        tokens = estimate_tokens(self.messages)
        self.token_label.setText(f"Tokens: {tokens}")

        if tokens > 7000:
            self.token_label.setStyleSheet("color: red; font-size: 12px;")
        elif tokens > 3500:
            self.token_label.setStyleSheet("color: orange; font-size: 12px;")
        else:
            self.token_label.setStyleSheet("color: black; font-size: 12px;")



    def save_chat(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Chat Log", 
            ai_chatlogs_dir,  # <-- default location
            "Text Files (*.txt)"
        )
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                for who, msg in self.messages:
                    prefix = "You:" if who == "user" else "AI:"
                    f.write(f"{prefix}\n{msg}\n\n")

    def clear_chat(self):
        self.messages = []
        self.update_chat()

    def load_chat(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, 
            "Load Chat Log", 
            ai_chatlogs_dir,  # <-- default location
            "Text Files (*.txt)"
        )
        if filename:
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
            messages = []
            current_role = None
            buffer = []
            for line in lines:
                line = line.strip()
                if line == "You:":
                    if buffer and current_role:
                        messages.append((current_role, "\n".join(buffer)))
                    current_role = "user"
                    buffer = []
                elif line == "AI:":
                    if buffer and current_role:
                        messages.append((current_role, "\n".join(buffer)))
                    current_role = "ai"
                    buffer = []
                else:
                    buffer.append(line)

            if buffer and current_role:
                messages.append((current_role, "\n".join(buffer)))

            self.messages = messages
            self.update_chat()

def open_ai_assistant(parent=None):
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        window = AIAssistantWindow()
        window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        window.show()
        sys.exit(app.exec())
    else:
        window = AIAssistantWindow(parent=parent)
        window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        window.show()