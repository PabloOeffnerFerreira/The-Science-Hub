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

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODELS = [
    "qwen3:14b",
    "gemma3:12b",
    "deepseek-r1:14b",
    "mistral-small3.1",
    "qwen3:8b",
    "gemma3:4b"
]

MODE_PROMPTS = [
    "Please explain your reasoning and steps like a helpful teacher.",
    "Just give the direct answer, no explanation.",
    ""
]

def load_tool_knowledge():
    try:
        with open("tool_knowledge.json", "r", encoding="utf-8") as f:
            tools = json.load(f)
            summary = "\n".join(f"- {k}: {v}" for k, v in tools.items())
            return (
                "You're a helpful assistant integrated into Science Hub.\n"
                "The following tools are available:\n" + summary +
                "\nSuggest them when relevant. Never invent tools. Always keep your answers concise and helpful."
            )
    except Exception as e:
        return "You're a helpful assistant inside Science Hub."

class OllamaWorker(QThread):
    response_ready = pyqtSignal(str)
    error = pyqtSignal(str)
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
            resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
            resp.raise_for_status()
            # Parse every line of the streamed JSON response and join all content
            content = resp.content.decode("utf-8").strip()
            import json  # make sure this is at the top of your file too
            lines = content.splitlines()
            reply_chunks = []
            for line in lines:
                if line.strip():
                    data = json.loads(line)
                    part = data.get("message", {}).get("content", "")
                    reply_chunks.append(part)
            reply = "".join(reply_chunks).strip() or "No response."
            self.response_ready.emit(reply)
        except Exception as e:
            self.error.emit(f"JSON Parse Error: {e}\nRaw response: {resp.text[:200]}")


class AIAssistantWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Assistant (Ollama)")
        self.setMinimumSize(700, 540)
        self.messages = []

        main_layout = QVBoxLayout(self)

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        # Top: Model picker, mode selector, save, and clear
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Model:"))
        self.model_picker = QComboBox()
        self.model_picker.addItems(OLLAMA_MODELS)
        self.model_picker.setCurrentText("gemma3:12b")
        self.model_picker.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        top_layout.addWidget(self.model_picker)

        # Add three-mode selector
        self.mode_selector = QComboBox()
        self.mode_selector.addItems([
            "Learn (explanation, teacher mode)",
            "Use (just answer)",
            "Casual (Assistant)"
        ])
        self.mode_selector.setCurrentIndex(2)
        top_layout.addWidget(self.mode_selector)

        # Save log button
        self.save_btn = QPushButton("Save Chat")
        self.save_btn.clicked.connect(self.save_chat)
        top_layout.addWidget(self.save_btn)

        # Clear chat button
        self.clear_btn = QPushButton("Clear Chat")
        self.clear_btn.clicked.connect(self.clear_chat)
        top_layout.addWidget(self.clear_btn)

        main_layout.addLayout(top_layout)

        # Chat display
        from PyQt6.QtWidgets import QTextBrowser
        self.chatbox = QTextBrowser()
        self.chatbox.setReadOnly(True)
        main_layout.addWidget(self.chatbox)


        # Input and send button
        input_layout = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type your question here and press Enter...")
        self.input.returnPressed.connect(self.send)
        input_layout.addWidget(self.input)
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send)
        input_layout.addWidget(self.send_btn)
        main_layout.addLayout(input_layout)

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
        self.worker.response_ready.connect(self.receive)
        self.worker.error.connect(self.handle_error)
        self.worker.start()
    
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

    def save_chat(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Chat Log", "", "Text Files (*.txt)")
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                for who, msg in self.messages:
                    prefix = "You:" if who == "user" else "AI:"
                    f.write(f"{prefix}\n{msg}\n\n")

    def clear_chat(self):
        self.messages = []
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