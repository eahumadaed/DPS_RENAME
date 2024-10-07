from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFrame, QHBoxLayout, QListWidget, QPushButton, QLabel, QScrollArea, QComboBox, QMessageBox, QListWidgetItem, QSplitter, QShortcut
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QKeySequence
import requests
import sys
from inscripcion_form import Inscripcion

API_BASE_URL = 'https://loverman.net/dbase/dga2024/api/api.php?action='

class NextWindow(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.current_trabajo_id = None
        self.inscripcion_layouts = {} 
        self.isCompraventa = False

        self.setWindowTitle("DPs Formulario")
        self.setGeometry(1, 30, 1980, 1080)
        self.showMaximized()

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
        self.dir_listwidget.setMaximumHeight(150)
        self.dir_listwidget.name = "Por procesar"
        self.dir_listwidget.itemSelectionChanged.connect(self.on_directory_select)
        self.left_layout.addWidget(self.dir_listwidget)
        
        self.dir_finished_label = QLabel("Trabajos terminados", self)
        self.left_layout.addWidget(self.dir_finished_label)
        
        self.dir_finished_listwidget = QListWidget(self)
        self.dir_finished_listwidget.setMaximumHeight(150)
        self.dir_finished_listwidget.name = "Finalizado"
        self.dir_finished_listwidget.itemSelectionChanged.connect(self.on_directory_select)
        self.left_layout.addWidget(self.dir_finished_listwidget)

        self.update_button = QPushButton("Actualizar Lista", self)
        self.update_button.clicked.connect(self.load_trabajos)
        self.left_layout.addWidget(self.update_button)

        self.dir_label = QLabel("Seleccione PDF", self)
        self.left_layout.addWidget(self.dir_label)
        
        self.pdf_listbox = QListWidget(self)
        self.pdf_listbox.itemSelectionChanged.connect(self.on_pdf_select)
        self.left_layout.addWidget(self.pdf_listbox)
        
        self.load_trabajos()

    def load_trabajos(self):
        try:
            self.dir_listwidget.clear()
            self.dir_finished_listwidget.clear()
            response = requests.get(f'{API_BASE_URL}getTrabajosTipo&user_id={self.user_id}')
            response.raise_for_status()
            trabajos = response.json()
            for trabajo in trabajos:
                item = QListWidgetItem(f"{trabajo['numero']} - {trabajo['anio']} ({trabajo['estado']})")
                item.setData(Qt.UserRole, trabajo['id'])
                if trabajo['estado'] == None:
                    self.dir_listwidget.addItem(item)
                else:
                    self.dir_finished_listwidget.addItem(item)
        except requests.RequestException as e:
            self.show_message("Error", "Error al cargar trabajos", str(e))
            
    def on_pdf_select(self):
        selected_items = self.pdf_listbox.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            pdf_index = self.pdf_listbox.row(selected_item)
            if pdf_index < len(self.pdf_paths):
                pdf_path = self.pdf_paths[pdf_index]
                self.load_pdf(pdf_path)
            
    def on_directory_select(self):
        # Decidir si mostrar boton para agregar inscripcion
        self.toggle_add_inscripcion()
        
        # Eliminar inscripciones
        for layout_id in list(self.inscripcion_layouts.keys()): 
            self.remove_inscripcion(layout_id)
            
        self.clear_form()
        
        sender_widget = self.sender()
        widget_name = getattr(sender_widget, 'name', 'Desconocido')
        if widget_name == "Finalizado":
            self.dir_listwidget.clearSelection() 
        if widget_name == "Por procesar":
            self.dir_finished_listwidget.clearSelection() 
            
        selected_items = sender_widget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            selected_trabajo_id = selected_item.data(Qt.UserRole)

            self.current_trabajo_id = selected_trabajo_id

            self.load_tipo(selected_trabajo_id)
            self.load_pdfs(selected_trabajo_id)

            if self.pdf_paths:
                last_index = len(self.pdf_paths) - 1 
                self.pdf_listbox.setCurrentRow(last_index) 
                self.load_pdf(self.pdf_paths[last_index])
                
    def cargar_titulos_anteriores(self):
        #!!!
        #!!! Cargar titulos anteriores desde la api
        
        # Ejemplo de carga
        titulos_anteriores=[
            {
                "f_inscripcion":"12/12/2022",
                "comuna":"Linares",
                "cbr":"LINARES",
                "foja":"123",
                "vta": True,
                "num": "122",
                "anio":"2022"
            },
            {
                "f_inscripcion":"11/11/1998",
                "comuna":"Santiago",
                "cbr":"SANTIAGO",
                "foja":"1",
                "vta": False,
                "num": "1",
                "anio":"1998"
            }
        ]
        
        for titulo in titulos_anteriores:
            inscripcion = self.add_inscripcion()
            inscripcion.set_f_inscripcion(titulo['f_inscripcion'])
            inscripcion.set_comuna(titulo['comuna'])
            inscripcion.set_cbr(titulo['cbr'])
            inscripcion.set_foja(titulo['foja'])
            inscripcion.set_vta(titulo['vta'])
            inscripcion.set_numero(titulo['num'])
            inscripcion.set_anio(titulo['anio'])
        
    
    def load_tipo(self, trabajo_id):
        try:
            response = requests.get(f'{API_BASE_URL}getTipo&trabajo_id={trabajo_id}')
            response.raise_for_status()
            tipo_data = response.json()
            self.fill_tipo(tipo_data)
            if tipo_data['tipo_documento'] == "COMPRAVENTA":
                self.cargar_titulos_anteriores()
                
        except requests.RequestException as e:
            self.show_message("Error", "Error al cargar tipo", str(e))

    def fill_tipo(self, tipo_data):
        self.clear_form()
        if 'tipo_documento' in tipo_data:
            index = self.tipo_combo.findText(tipo_data['tipo_documento'])
            if index >= 0:
                self.tipo_combo.setCurrentIndex(index)

    def create_middle_frame(self):
        self.middle_frame = QFrame(self)
        self.middle_frame.setFrameShape(QFrame.StyledPanel)
        self.middle_frame.setMaximumWidth(700)
        self.middle_frame.setMinimumWidth(600)
        self.layout.addWidget(self.middle_frame)

        self.scroll_area = QScrollArea(self.middle_frame)
        self.scroll_area.setWidgetResizable(True)
        self.middle_layout = QVBoxLayout(self.middle_frame)
        self.middle_layout.addWidget(self.scroll_area)

        self.scroll_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_widget)
        
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_layout.setSpacing(5)

        self.form_label = QLabel("Formulario", self)
        self.scroll_layout.addWidget(self.form_label)

        self.form_widget = QWidget()
        self.scroll_layout.addWidget(self.form_widget)

        self.form_layout = QVBoxLayout(self.form_widget)
        self.form_layout.setAlignment(Qt.AlignTop)

        self.add_section_title("TIPO DE DOCUMENTO")
        
        opciones = ["SENTENCIA", "RESOLUCION DGA", "COMPRAVENTA", "COMUNIDAD DE AGUAS", "OTROS"]
        
        options_label = QLabel("Opciones:", self)
        self.form_layout.addWidget(options_label)
        left_options_layout = QVBoxLayout()
        right_options_layout = QVBoxLayout()
        options_layout = QHBoxLayout()
        mitad_lista = len(opciones)//2 if  len(opciones)%2==0 else len(opciones)//2+1
        for index, item in enumerate(opciones, start=1):
            label = QLabel(f"\t({index}) {item}")
            if index <= mitad_lista:
                left_options_layout.addWidget(label)
            else:
                right_options_layout.addWidget(label)
        options_layout.addLayout(left_options_layout)
        options_layout.addLayout(right_options_layout)
        left_options_layout.setAlignment(Qt.AlignTop)
        right_options_layout.setAlignment(Qt.AlignTop)
        self.form_layout.addLayout(options_layout)
        
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["--"] + opciones)
        self.tipo_combo.currentIndexChanged.connect(self.toggle_add_inscripcion)
        self.form_layout.addWidget(self.tipo_combo)
        

        QShortcut(QKeySequence("1"), self, lambda: self.tipo_combo.setCurrentIndex(1))
        QShortcut(QKeySequence("2"), self, lambda: self.tipo_combo.setCurrentIndex(2))
        QShortcut(QKeySequence("3"), self, lambda: self.tipo_combo.setCurrentIndex(3))
        QShortcut(QKeySequence("4"), self, lambda: self.tipo_combo.setCurrentIndex(4))
        QShortcut(QKeySequence("5"), self, lambda: self.tipo_combo.setCurrentIndex(5))
        QShortcut(QKeySequence("6"), self, lambda: self.tipo_combo.setCurrentIndex(6))
        
        self.save_button = QPushButton("Guardar", self)
        self.middle_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_form)
        
        self.enter_shortcut = QShortcut(QKeySequence(Qt.Key_Return), self)
        self.enter_shortcut.activated.connect(self.handle_enter)
        self.enter_num_shortcut = QShortcut(QKeySequence(Qt.Key_Enter), self)
        self.enter_num_shortcut.activated.connect(self.handle_enter)
        
        self.section_title_2 = QLabel("\nTÍTULO ANTERIOR", self)
        self.section_title_2.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.form_layout.addWidget(self.section_title_2)
        self.add_inscripcion_button = QPushButton("Agregar inscripción", self)
        self.form_layout.addWidget(self.add_inscripcion_button)
        self.add_inscripcion_button.clicked.connect(self.add_inscripcion)
        
        self.section_title_2.hide()
        self.add_inscripcion_button.hide()
    
    def handle_enter(self):
        if self.tipo_combo.currentText() != "COMPRAVENTA":
            self.save_form()
        
    def add_inscripcion(self):
        self.form_layout.removeWidget(self.add_inscripcion_button)
        
        self.new_inscripcion_widget = Inscripcion()
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        
        delete_button = QPushButton('Eliminar')
        
        layout_id = f"inscripcion_{id(self.new_inscripcion_widget)}"
        
        inscripcion_layout = QVBoxLayout()
        inscripcion_layout.addWidget(self.new_inscripcion_widget)
        inscripcion_layout.addWidget(separator)
        inscripcion_layout.addWidget(delete_button)
        
        container_widget = QWidget()
        container_widget.setLayout(inscripcion_layout)
        
        self.form_layout.addWidget(container_widget)
        self.form_layout.addWidget(self.add_inscripcion_button)
        
        self.inscripcion_layouts[layout_id] = container_widget
        
        delete_button.clicked.connect(lambda: self.remove_inscripcion(layout_id))
        
        return self.new_inscripcion_widget
        
    def get_all_inscripciones(self):
        inscripciones = []
        inscripciones_data = []
        
        for layout_id, container_widget in self.inscripcion_layouts.items():
            inscripcion_widget = container_widget.layout().itemAt(0).widget()
            inscripciones.append(inscripcion_widget)
        
        for inscripcion in inscripciones:
            data = {
                "f_inscripcion": inscripcion.f_inscripcion,
                "comuna": inscripcion.comuna,
                "cbr":inscripcion.cbr,
                "foja":inscripcion.foja,
                "vta":inscripcion.vta,
                "num":inscripcion.num,
                "año":inscripcion.anio
            }
            inscripciones_data.append(data)
        
        return inscripciones_data

    def remove_inscripcion(self, layout_id):
        if layout_id in self.inscripcion_layouts:
            inscripcion_layout = self.inscripcion_layouts[layout_id]
            
            self.form_layout.removeWidget(inscripcion_layout)

            while inscripcion_layout.layout().count():
                item = inscripcion_layout.layout().takeAt(0)  
                widget = item.widget() 
                if widget is not None:
                    widget.deleteLater()

            inscripcion_layout.deleteLater()
            self.inscripcion_layouts.pop(layout_id)
            self.form_layout.update()


    def toggle_add_inscripcion(self):
        self.isCompraventa = self.tipo_combo.currentText() == "COMPRAVENTA"
        if self.isCompraventa:
            self.section_title_2.show()
            self.add_inscripcion_button.show()
        else:
            self.section_title_2.hide()
            self.add_inscripcion_button.hide()

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
        except Exception as e:
            self.show_message("Error", "Error al cargar PDF", str(e))

    def clear_form(self):
        self.tipo_combo.setCurrentIndex(0)
    
    def save_form(self):
        if self.current_trabajo_id is not None:
            print(f"TRABAJO ID: {self.current_trabajo_id}")
            
            tipo_documento = self.tipo_combo.currentText()
        
            #!!!
            #!!! NO SE PUEDE GUARDAR CON NONE
            if tipo_documento == "--":
                tipo_documento = None
                
            if tipo_documento == "COMPRAVENTA":
                #!!!
                #!!! GUARDAR TITULOS ANTERIORES EN BD
                titulos_anteriores = self.get_all_inscripciones()
                print(f"TITULOS ANTERIORES: {titulos_anteriores}")
            
            form_data = {'user_id': self.user_id, 'trabajo_id': self.current_trabajo_id, 'tipo_documento': tipo_documento}
            
            print(f"FORM DATA: {form_data}")
            
            try:
                response = requests.post(f'{API_BASE_URL}saveTipo', json=form_data)
                response.raise_for_status()
                self.show_message("Info", "Guardar", "Formulario guardado exitosamente.")
                print("Formulario guardado:", form_data)
                self.load_trabajos()
                self.pdf_listbox.clear()
                self.current_trabajo_id = None
                self.dir_listwidget.setCurrentRow(0)
                
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