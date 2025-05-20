import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QHBoxLayout, QDialog, QDialogButtonBox,
    QListWidget, QListWidgetItem, QTextBrowser, QSplitter
)
from PyQt6.QtCore import Qt
from pyalex import Works, config
from tools.utilities import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path
)


class EmailDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Set OpenAlex Email")
        self.setModal(True)
        self.resize(300, 100)

        layout = QVBoxLayout()

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email for polite pool access")
        layout.addWidget(self.email_input)

        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

    def get_email(self):
        return self.email_input.text()


class WorkViewer(QTextBrowser):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setOpenExternalLinks(True)
        self.setStyleSheet("background-color: #1e1e1e; color: #dddddd; font-family: Consolas, monospace;")

    def show_work(self, work):
        title = work.get("display_name", "(No Title)")
        authors = work.get("authorships", [])
        author_names = ", ".join(a['author']['display_name'] for a in authors if 'author' in a)
        year = work.get("publication_year", "N/A")
        abstract = work.get("abstract_inverted_index")
        url = work.get("id", "")
        doi = work.get("doi", "")

        # Try to fetch full text URL from open access data
        oa_data = work.get("open_access", {})
        fulltext_url = oa_data.get("oa_url") or url

        abstract_text = ""
        if abstract:
            words = ["" for _ in range(max(i for word in abstract for i in abstract[word]) + 1)]
            for word, indices in abstract.items():
                for i in indices:
                    words[i] = word
            abstract_text = " ".join(words)

        html = f"""
        <h2 style='color:#ffffff;'>{title}</h2>
        <p><b>Authors:</b> {author_names}</p>
        <p><b>Year:</b> {year}</p>
        <p><b>DOI:</b> {doi}</p>
        <p><b>Full Text:</b> <a href='{fulltext_url}' style='color:#6fa8dc'>{fulltext_url}</a></p>
        <hr>
        <p>{abstract_text}</p>
        """
        self.setHtml(html)


class OpenAlexBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenAlex Library Browser")
        self.resize(1000, 600)
        self.setStyleSheet("background-color: #121212; color: #dddddd;")

        layout = QVBoxLayout()

        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for scientific works...")
        self.search_input.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")
        self.search_button = QPushButton("Search")
        self.search_button.setStyleSheet("background-color: #2e2e2e; color: #ffffff;")
        self.search_button.clicked.connect(self.perform_search)
        self.email_button = QPushButton("Set Email (Optional)")
        self.email_button.setStyleSheet("background-color: #2e2e2e; color: #ffffff;")
        self.email_button.clicked.connect(self.set_email)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.email_button)
        layout.addLayout(search_layout)

        # Result list and viewer
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.results_list = QListWidget()
        self.results_list.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")
        self.results_list.itemClicked.connect(self.display_work)
        splitter.addWidget(self.results_list)

        self.viewer = WorkViewer()
        splitter.addWidget(self.viewer)

        splitter.setSizes([300, 700])
        layout.addWidget(splitter)
        self.setLayout(layout)

        self.work_data = []

    def set_email(self):
        dialog = EmailDialog()
        if dialog.exec():
            email = dialog.get_email().strip()
            if email:
                config.email = email

    def perform_search(self):
        query = self.search_input.text().strip()
        if not query:
            self.results_list.clear()
            self.viewer.setPlainText("Please enter a search term.")
            return

        self.results_list.clear()
        self.viewer.setPlainText("Searching OpenAlex...")
        self.work_data = []

        try:
            works = Works().search(query).get()
            self.work_data = works[:20]  # limit results

            for work in self.work_data:
                title = work.get("display_name", "(No Title)")
                item = QListWidgetItem(title)
                self.results_list.addItem(item)

            self.viewer.setPlainText("Select a result to view details.")

        except Exception as e:
            self.viewer.setPlainText(f"Error: {str(e)}")

    def display_work(self, item):
        index = self.results_list.row(item)
        if 0 <= index < len(self.work_data):
            work = self.work_data[index]
            self.viewer.show_work(work)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OpenAlexBrowser()
    window.show()
    sys.exit(app.exec())