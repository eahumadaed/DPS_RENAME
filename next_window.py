from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFrame, QHBoxLayout, QListWidget, QPushButton, QLabel, QScrollArea, QSizePolicy, QComboBox, QMessageBox, QListWidgetItem, QSplitter, QShortcut
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QKeySequence
import requests
import sys

API_BASE_URL = 'https://loverman.net/dbase/dga2024/api/api.php?action='

class NextWindow(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.current_trabajo_id = None
        self.current_formulario_id = None
        self.modal_abierto = False

        self.setWindowTitle("DPs Formulario")
        self.setGeometry(1, 30, 1980, 1080)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        self.pdf_paths = []
        self.entries = []

        self.create_left_frame()
        self.create_middle_frame()
        self.create_right_frame()

    def create_left_frame(self):
        self.left_frame = QFrame(self)
        self.left_frame.setFrameShape(QFrame.StyledPanel)
        self.left_frame.setMaximumWidth(300)
        self.layout.addWidget(self.left_frame)

        self.left_layout = QVBoxLayout(self.left_frame)

        self.dir_label = QLabel("Seleccione trabajo", self)
        self.left_layout.addWidget(self.dir_label)

        self.dir_listwidget = QListWidget(self)
        self.dir_listwidget.setMaximumHeight(300)
        self.dir_listwidget.itemSelectionChanged.connect(self.on_directory_select)
        self.left_layout.addWidget(self.dir_listwidget)

        self.update_button = QPushButton("Actualizar Lista", self)
        self.update_button.clicked.connect(self.load_trabajos)
        self.left_layout.addWidget(self.update_button)

        self.dir_label = QLabel("Seleccione PDF", self)
        self.left_layout.addWidget(self.dir_label)
        self.pdf_listbox = QListWidget(self)
        self.left_layout.addWidget(self.pdf_listbox)
        
        self.load_trabajos()

    def load_trabajos(self):
        try:
            self.dir_listwidget.clear()
            response = requests.get(f'{API_BASE_URL}getTrabajosTipo&user_id={self.user_id}')
            response.raise_for_status()
            trabajos = response.json()
            for trabajo in trabajos:
                item = QListWidgetItem(f"{trabajo['numero']} - {trabajo['anio']} ({trabajo['estado']})")
                item.setData(Qt.UserRole, trabajo['id'])
                self.dir_listwidget.addItem(item)
        except requests.RequestException as e:
            self.show_message("Error", "Error al cargar trabajos", str(e))

    def on_directory_select(self):
        selected_items = self.dir_listwidget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            selected_trabajo_id = selected_item.data(Qt.UserRole)

            self.current_trabajo_id = selected_trabajo_id
            print(f"Trabajo seleccionado: {selected_trabajo_id}")

            self.load_tipo(selected_trabajo_id)
            self.load_pdfs(selected_trabajo_id)

            if self.pdf_paths:
                self.load_pdf(self.pdf_paths[0])

    def load_tipo(self, trabajo_id):
        try:
            response = requests.get(f'{API_BASE_URL}getTipo&trabajo_id={trabajo_id}')
            response.raise_for_status()
            tipo_data = response.json()
            self.fill_tipo(tipo_data)
            print(tipo_data)
        except requests.RequestException as e:
            self.show_message("Error", "Error al cargar tipo", str(e))

    def fill_tipo(self, tipo_data):
        self.clear_form()
        if 'tipo_documento' in tipo_data:
            index = self.tipo_combo.findText(tipo_data['tipo_documento'])
            if index >= 0:
                self.tipo_combo.setCurrentIndex(index)
        print("Tipo cargado:", tipo_data)

    def create_middle_frame(self):
        self.middle_frame = QFrame(self)
        self.middle_frame.setFrameShape(QFrame.StyledPanel)
        self.middle_frame.setMaximumWidth(700)
        self.middle_frame.setMinimumWidth(600)
        self.layout.addWidget(self.middle_frame)

        self.middle_layout = QVBoxLayout(self.middle_frame)
        self.middle_layout.setSpacing(5)

        self.form_label = QLabel("Formulario", self)
        self.middle_layout.addWidget(self.form_label)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.middle_layout.addWidget(self.scroll_area)

        self.form_widget = QWidget()
        self.scroll_area.setWidget(self.form_widget)

        self.form_layout = QVBoxLayout(self.form_widget)
        self.form_layout.setAlignment(Qt.AlignTop)

        self.add_section_title("TIPO DE DOCUMENTO")
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["--", "COMPRAVENTA", "COMUNIDAD", "OTROS"])
        self.form_layout.addWidget(self.tipo_combo)

        QShortcut(QKeySequence("1"), self, lambda: self.tipo_combo.setCurrentIndex(1))
        QShortcut(QKeySequence("2"), self, lambda: self.tipo_combo.setCurrentIndex(2))
        QShortcut(QKeySequence("3"), self, lambda: self.tipo_combo.setCurrentIndex(3))

        self.save_button = QPushButton("Guardar", self)
        self.save_button.clicked.connect(self.save_form)
        self.middle_layout.addWidget(self.save_button)

        QShortcut(QKeySequence(Qt.Key_Return), self, self.save_form)

    def add_section_title(self, title):
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 10px;")
        self.form_layout.addWidget(title_label)

    def create_right_frame(self):
        self.right_frame = QFrame(self)
        self.right_frame.setFrameShape(QFrame.StyledPanel)
        self.layout.addWidget(self.right_frame, stretch=1)

        self.right_layout = QVBoxLayout(self.right_frame)
        self.splitter = QSplitter(Qt.Vertical)
        self.right_layout.addWidget(self.splitter, stretch=1)

        self.browser = QWebEngineView()
        self.splitter.addWidget(self.browser)

        self.splitter.setSizes([800, 400])

    def load_pdfs(self, trabajo_id):
        try:
            response = requests.get(f'{API_BASE_URL}getPDFs&trabajo_id={trabajo_id}')
            response.raise_for_status()
            pdfs = response.json()
            self.pdf_listbox.clear()
            self.pdf_paths = []
            for pdf in pdfs:
                self.pdf_listbox.addItem(pdf['nombre'])
                self.pdf_paths.append(pdf['ruta'])
        except requests.RequestException as e:
            self.show_message("Error", "Error al cargar PDFs", str(e))

    def load_pdf(self, encoded_pdf_path):
        try:
            pdf_url = f"https://loverman.net/dbase/dga2024/viewer.html?file={encoded_pdf_path}#page=1"
            self.browser.load(QUrl(pdf_url))
            print(f"Mostrando PDF desde URL: {pdf_url}")
        except Exception as e:
            self.show_message("Error", "Error al cargar PDF", str(e))

    def clear_form(self):
        self.tipo_combo.setCurrentIndex(0)
        print("Formulario limpiado")

    def save_form(self):
        form_data = {'user_id': self.user_id, 'trabajo_id': self.current_trabajo_id, 'tipo_documento': self.tipo_combo.currentText()}
        try:
            response = requests.post(f'{API_BASE_URL}saveTipo', json=form_data)
            response.raise_for_status()
            self.show_message("Info", "Guardar", "Formulario guardado exitosamente.")
            print("Formulario guardado:", form_data)
        except requests.RequestException as e:
            self.show_message("Error", "Error al guardar formulario", str(e))

    def show_message(self, message_type, title, message):
        msg_box = QMessageBox()
        if message_type == "Error":
            msg_box.setIcon(QMessageBox.Critical)
        elif message_type == "Info":
            msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = NextWindow(user_id=1)
    main_window.show()
    sys.exit(app.exec_())
