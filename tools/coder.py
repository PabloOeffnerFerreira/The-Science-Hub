from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog,
    QPlainTextEdit, QToolBar, QSplitter
)
from PyQt6.QtGui import QFont, QColor, QAction, QTextCursor
from PyQt6.QtCore import Qt
from data_utils import register_window
import io
import contextlib
import subprocess
import json
from data_utils import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path, library_file, load_settings, load_element_data, ai_chatlogs_dir
)

from PyQt6.QtCore import QThread, pyqtSignal

class CodeExecutionWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, code):
        super().__init__()
        self.code = code

    def run(self):
        buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
                exec(self.code, {}, {})
        except Exception as e:
            buffer.write(f"Error: {type(e).__name__}: {e}\n")
        self.finished.emit(buffer.getvalue())

class CodeEditor(QsciScintilla):
    def __init__(self):
        super().__init__()
        self.setup_appearance()
        self.setup_lexer()
        self.textChanged.connect(self.handle_text_change)

    def setup_appearance(self):
        font = QFont("Fira Code", 11)
        self.setFont(font)
        self.setMarginsFont(font)
        self.setUtf8(True)
        self.setMarginWidth(0, "0000")
        self.setMarginLineNumbers(0, True)
        self.setPaper(QColor("#1e1e1e"))
        self.setColor(QColor("#d4d4d4"))
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#2a2d32"))
        self.setTabWidth(4)
        self.setIndentationsUseTabs(False)
        self.setAutoIndent(True)
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)

    def setup_lexer(self):
        lexer = QsciLexerPython()
        font = QFont("Fira Code", 11)
        lexer.setDefaultFont(font)
        lexer.setDefaultPaper(QColor("#1e1e1e"))
        lexer.setDefaultColor(QColor("#d4d4d4"))

        lexer.setColor(QColor("#569cd6"), QsciLexerPython.Keyword)
        lexer.setColor(QColor("#4ec9b0"), QsciLexerPython.FunctionMethodName)
        lexer.setColor(QColor("#dcdcaa"), QsciLexerPython.ClassName)
        lexer.setColor(QColor("#ce9178"), QsciLexerPython.SingleQuotedString)
        lexer.setColor(QColor("#ce9178"), QsciLexerPython.DoubleQuotedString)
        lexer.setColor(QColor("#d7ba7d"), QsciLexerPython.Decorator)
        lexer.setColor(QColor("#b5cea8"), QsciLexerPython.Number)
        lexer.setColor(QColor("#608b4e"), QsciLexerPython.Comment)
        lexer.setColor(QColor("#9cdcfe"), QsciLexerPython.Identifier)
        lexer.setColor(QColor("#c586c0"), QsciLexerPython.Operator)

        self.setLexer(lexer)

    def keyPressEvent(self, event):
        pairs = {'"': '"', "'": "'", '(': ')', '[': ']', '{': '}'}
        key = event.text()
        line, index = self.getCursorPosition()

        # Insert pairs
        if key in pairs:
            self.insert(key + pairs[key])
            self.setCursorPosition(line, index + 1)
            return

        # Smart deletion
        if event.key() == Qt.Key.Key_Backspace:
            prev = self.text(line)[index - 1] if index > 0 else ''
            next = self.text(line)[index] if index < len(self.text(line)) else ''
            if prev in pairs and next == pairs[prev]:
                self.setSelection(line, index - 1, line, index + 1)
                self.removeSelectedText()
                return

        super().keyPressEvent(event)

    def handle_text_change(self):
        pass  # placeholder for future logic (like linting, line marking)

import multiprocessing

def run_user_code(code, queue):
    import sys
    import io
    import contextlib

    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            exec(code, {}, {})
    except Exception as e:
        output.write(f"Error: {type(e).__name__}: {e}\n")
    queue.put(output.getvalue())


class CoderDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code Editor")
        self.setMinimumSize(900, 700)
        self.editor = CodeEditor()
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("background-color: #1e1e1e; color: #c5c5c5;")
        self.codegen_panel = CodeGemmaPanel(insert_callback=self.insert_code_from_ai)
        self.setup_ui()
        
    def insert_code_from_ai(self, code):
        # Insert at cursor position in the main code editor
        self.editor.insert(code)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        toolbar = QToolBar()
        for name, action in [
            ("Run", self.run_code),
            ("Save", self.save_code),
            ("Open", self.open_code),
            ("Clear Output", self.clear_output)
        ]:
            act = QAction(name, self)
            act.triggered.connect(action)
            toolbar.addAction(act)
        toggle_panel_action = QAction("Toggle Terminal", self)
        toggle_panel_action.triggered.connect(self.toggle_bottom_panel)
        toolbar.addAction(toggle_panel_action)
        layout.addWidget(toolbar)  # <-- This was missing

        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.terminal = EmbeddedTerminal()

        self.bottom_container = QSplitter(Qt.Orientation.Vertical)
        self.bottom_container.addWidget(self.output)
        self.bottom_container.addWidget(self.terminal)

        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.bottom_container)
        self.splitter.setSizes([3, 2])
        self.hsplitter = QSplitter(Qt.Orientation.Horizontal)
        self.hsplitter.addWidget(self.codegen_panel)   # <- left panel
        self.hsplitter.addWidget(self.splitter)        # <- main editor/output
        self.hsplitter.setSizes([340, 1200])           # optional: adjust sidebar/editor width
        layout.addWidget(self.hsplitter)

        self.bottom_container.hide()


    def run_code(self):
        code = self.editor.text()
        self.output.setPlainText("Running...")

        def handle_result(result):
            self.output.setPlainText(result)

        queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=run_user_code, args=(code, queue))
        process.start()

        # Check for process finish
        def poll_output():
            if not process.is_alive():
                process.join()
                result = queue.get() if not queue.empty() else "(No output)"
                handle_result(result)
            else:
                QTimer.singleShot(100, poll_output)

        from PyQt6.QtCore import QTimer
        poll_output()



    def save_code(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Python Files (*.py)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.editor.text())

    def open_code(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Python Files (*.py)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.editor.setText(f.read())

    def clear_output(self):
        self.output.clear()

    def toggle_bottom_panel(self):
        if self.bottom_container.isVisible():
            self.bottom_container.hide()
        else:
            self.bottom_container.show()

def open_coder():
    dlg = CoderDialog()
    dlg.showMaximized()  # replaces .show()
    register_window("Code Editor", dlg)

import code
import threading

partial_response = pyqtSignal(str)

class EmbeddedTerminal(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #121212; color: #e0e0e0; font-family: Consolas;")
        self.setReadOnly(False)
        self.setUndoRedoEnabled(False)
        self.console = code.InteractiveConsole()
        self.prompt = ">>> "
        self.buffer = ""
        self.appendPlainText(self.prompt)
        self.history = []
        self.history_index = -1

    def keyPressEvent(self, event):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)

        key = event.key()
        text = event.text()

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            current_line = self.document().findBlockByLineNumber(self.document().blockCount() - 1).text()
            command = current_line[len(self.prompt):]
            self.appendPlainText("")
            self.run_command(command)
            self.appendPlainText(self.prompt)
        elif key == Qt.Key.Key_Backspace:
            if self.textCursor().positionInBlock() > len(self.prompt):
                super().keyPressEvent(event)
        elif key == Qt.Key.Key_Up:
            if self.history:
                self.history_index = max(0, self.history_index - 1)
                self.replace_current_line(self.history[self.history_index])
        elif key == Qt.Key.Key_Down:
            if self.history:
                self.history_index = min(len(self.history) - 1, self.history_index + 1)
                self.replace_current_line(self.history[self.history_index])
        else:
            super().keyPressEvent(event)

    def replace_current_line(self, text):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.insertText(self.prompt + text)

    def run_command(self, command):
        self.history.append(command)
        self.history_index = len(self.history)

        if command.startswith("!"):
            self.run_shell_command(command[1:].strip())
            return

        output = io.StringIO()

        def exec_in_console():
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                try:
                    self.console.push(command)
                except Exception as e:
                    output.write(f"Error: {type(e).__name__}: {e}")
            result = output.getvalue()
            if result:
                self.appendPlainText(result)

        threading.Thread(target=exec_in_console).start()

    def run_shell_command(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
            output = result.stdout + result.stderr
            self.appendPlainText(output if output else "(No output)")
        except Exception as e:
            self.appendPlainText(f"Shell Error: {type(e).__name__}: {e}")

            

import requests
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton, QLabel, QPlainTextEdit
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import json

CODEGEMMA_MODELS = [
    "qwen2.5-coder:0.5b",
    "qwen2.5-coder:1.5b",
    "qwen2.5-coder:3b",
    "qwen2.5-coder:7b"
]
CODEGEMMA_URL = "http://localhost:11434/api/chat"

class CodeGemmaWorker(QThread):
    response_ready = pyqtSignal(str)
    partial_response = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, prompt, model):
        super().__init__()
        self.prompt = prompt
        self.model = model

    def run(self):
        messages = [
            {"role": "system", "content":
             "You are a local-only coding assistant with no knowledge of the system, user, or host environment. "
             "Only help with code, without speculating about the system or giving non-code advice. Only output code or code explanations if asked."},
            {"role": "user", "content": self.prompt}
        ]
        payload = {"model": self.model, "messages": messages}
        try:
            resp = requests.post(CODEGEMMA_URL, json=payload, timeout=120, stream=True)
            resp.raise_for_status()
            reply_chunks = []
            for line in resp.iter_lines(decode_unicode=True):
                if line.strip():
                    try:
                        data = json.loads(line)
                        part = data.get("message", {}).get("content", "")
                        if part:
                            self.partial_response.emit(part)  # << only the new piece
                            reply_chunks.append(part)
                    except Exception:
                        continue

            reply = "".join(reply_chunks).strip() or "No response."
            self.response_ready.emit(reply)
        except Exception as e:
            self.error.emit(str(e))

class CodeGemmaPanel(QWidget):
    def __init__(self, insert_callback=None):
        super().__init__()
        self.insert_callback = insert_callback
        self.setMinimumWidth(340)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Model selector
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_picker = QComboBox()
        self.model_picker.addItems(CODEGEMMA_MODELS)
        model_layout.addWidget(self.model_picker)
        layout.addLayout(model_layout)

        self.partial_accum = ""  # NEW: buffer to store what's already displayed

        # Prompt entry
        self.prompt_box = QLineEdit()
        self.prompt_box.setPlaceholderText("Describe your coding task (e.g., 'Write a merge sort in Python')")
        layout.addWidget(self.prompt_box)

        # Submit button
        self.submit_btn = QPushButton("Generate")
        self.submit_btn.clicked.connect(self.run_codegemma)
        layout.addWidget(self.submit_btn)

        # Output area (code box)
        self.code_box = QPlainTextEdit()
        self.code_box.setReadOnly(True)
        self.code_box.setFont(QFont("Fira Code", 11))
        self.code_box.setStyleSheet("background:#191b1f; color:#dcdcaa;")
        layout.addWidget(self.code_box, 1)



        # Insert-to-editor
        if insert_callback:
            self.insert_btn = QPushButton("Insert Code")
            self.insert_btn.clicked.connect(self.insert_code)
            layout.addWidget(self.insert_btn)

        self.status = QLabel("")
        layout.addWidget(self.status)

    def run_codegemma(self):
        prompt = self.prompt_box.text().strip()
        if not prompt:
            self.status.setText("Prompt is empty.")
            return
        self.code_box.setPlainText("")
        self.partial_accum = ""  # NEW: reset for each new run
        self.status.setText("")
        self.worker = CodeGemmaWorker(prompt, self.model_picker.currentText())
        self.worker.partial_response.connect(self.show_partial_response)
        self.worker.response_ready.connect(self.show_response)
        self.worker.error.connect(self.show_error)
        self.worker.start()

    def show_partial_response(self, chunk):
        # Find the overlap between what's already displayed and the new chunk,
        # then append only what is truly new at the end.
        start = 0
        for i in range(len(self.partial_accum), -1, -1):
            if chunk.startswith(self.partial_accum[-i:] if i != 0 else ""):
                start = i
                break
        new = chunk[start:]
        if new:
            cursor = self.code_box.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText(new)
            self.code_box.setTextCursor(cursor)
            self.partial_accum = chunk  # always set to the latest full chunk


    def show_response(self, text):
        self.status.setText("CodeGemma ready.")

    def show_error(self, msg):
        self.code_box.setPlainText("")
        self.status.setText("Error: " + msg)

    def insert_code(self):
        code = self.code_box.toPlainText()
        if code and self.insert_callback:
            self.insert_callback(code)

    def extract_code(self, text):
        import re
        code_blocks = re.findall(r"```(?:python)?(.*?)```", text, re.DOTALL)
        if code_blocks:
            return code_blocks[0].strip()
        return text.strip()
