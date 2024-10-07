from PyQt5.QtWidgets import QCheckBox, QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QLineEdit, QComboBox
from PyQt5.QtCore import Qt
import sys
import re

class Inscripcion(QWidget):
    def __init__(self):
        super().__init__() 
        self.f_inscripcion = ""
        self.comuna = ""
        self.cbr =  ""
        self.foja = ""
        self.vta = False
        self.num = ""
        self.anio = ""
        
        
        self.inicializar_ui()
        
    def inicializar_ui(self):
        self.layout_f_inscripcion = QHBoxLayout()
        self.label_f_inscripcion = QLabel("F_INSCRIPCION")
        self.input_f_inscripcion = QLineEdit()
        self.input_f_inscripcion.setPlaceholderText("--/--/----")
        self.layout_f_inscripcion.addWidget(self.label_f_inscripcion)
        self.layout_f_inscripcion.addWidget(self.input_f_inscripcion)
        self.input_f_inscripcion.textChanged.connect(self.format_date_input)
        
        self.layout_comuna = QHBoxLayout()
        self.label_comuna = QLabel("COMUNA")
        self.comuna_combo = QComboBox()
        self.comuna_combo.addItems(["--", "Linares", "Santiago", "Doñihue"])
        self.layout_comuna.addWidget(self.label_comuna)
        self.layout_comuna.addWidget(self.comuna_combo)
        self.comuna_combo.currentIndexChanged.connect(self.capturar_opcion_comuna)
        
        self.layout_cbr = QHBoxLayout()
        self.label_cbr =  QLabel("CBR")
        self.input_cbr = QLineEdit()
        self.layout_cbr.addWidget(self.label_cbr)
        self.layout_cbr.addWidget(self.input_cbr)
        self.input_cbr.textChanged.connect(self.capture_cbr)
        
        self.layout_foja = QHBoxLayout()
        self.label_foja = QLabel("FOJA")
        self.input_foja = QLineEdit()
        self.layout_foja.addWidget(self.label_foja)
        self.layout_foja.addWidget(self.input_foja)
        self.input_foja.textChanged.connect(self.allow_only_numbers)
        
        self.layout_vta_num_anio = QHBoxLayout()
        self.label_vta = QLabel("V")
        self.checkbox_vta = QCheckBox()
        self.layout_vta_num_anio.addWidget(self.label_vta)
        self.layout_vta_num_anio.addWidget(self.checkbox_vta)
        self.checkbox_vta.stateChanged.connect(self.capturar_estado_vta)
        
        self.label_num = QLabel("N°")
        self.input_num = QLineEdit()
        self.layout_vta_num_anio.addWidget(self.label_num)
        self.layout_vta_num_anio.addWidget(self.input_num)
        self.input_num.textChanged.connect(self.allow_only_numbers)
        
        self.label_anio = QLabel("AÑO")
        self.input_anio = QLineEdit()
        self.layout_vta_num_anio.addWidget(self.label_anio)
        self.layout_vta_num_anio.addWidget(self.input_anio)
        self.input_anio.textChanged.connect(self.allow_only_four_digits)
        
        self.vLayout = QVBoxLayout()
        self.vLayout.addLayout(self.layout_f_inscripcion)
        self.vLayout.addLayout(self.layout_comuna)
        self.vLayout.addLayout(self.layout_cbr)
        self.vLayout.addLayout(self.layout_foja)
        
        self.layoutContainer = QWidget()
        self.layoutContainer.setLayout(self.vLayout)
        
        self.layoutContainer1 = QWidget()
        self.layout_vta_num_anio.setAlignment(Qt.AlignBottom)
        self.layoutContainer1.setLayout(self.layout_vta_num_anio)

        self.layoutContainer.setMinimumWidth(220)
        self.layoutContainer.setMaximumWidth(280)
        
        self.inscripcion_layout = QHBoxLayout()
        self.inscripcion_layout.addWidget(self.layoutContainer)
        self.inscripcion_layout.addWidget(self.layoutContainer1)
    
        self.setLayout(self.inscripcion_layout)
        
    def on_delete(self):
        None
        
    def capturar_estado_vta(self, state):
        self.vta = (state == Qt.Checked)  
        
    def capturar_opcion_comuna(self, index):
        self.comuna = self.comuna_combo.currentText() 
        
    def capture_cbr(self, text):
        cleaned_text = text.upper()
        self.cbr = cleaned_text

    def format_date_input(self, text):
        cleaned_text = re.sub(r'\D', '', text)

        if len(cleaned_text) >= 6:
            formatted_date = f"{cleaned_text[:2]}/{cleaned_text[2:4]}/{cleaned_text[4:8]}"
        elif len(cleaned_text) >= 4:
            formatted_date = f"{cleaned_text[:2]}/{cleaned_text[2:4]}/{cleaned_text[4:]}"
        elif len(cleaned_text) >= 2:
            formatted_date = f"{cleaned_text[:2]}/{cleaned_text[2:]}"
        else:
            formatted_date = cleaned_text
            
        self.f_inscripcion = formatted_date

        self.input_f_inscripcion.blockSignals(True)
        self.input_f_inscripcion.setText(formatted_date)
        self.input_f_inscripcion.blockSignals(False)

    def allow_only_numbers(self, text):
        cleaned_text = re.sub(r'\D', '', text)

        sender = self.sender()
        if sender == self.input_foja:
            self.foja = cleaned_text 
        
            
        if sender == self.input_num:
            self.num = cleaned_text 
        
        sender.blockSignals(True)
        sender.setText(cleaned_text)
        sender.blockSignals(False)
        
    def allow_only_four_digits(self, text):
        cleaned_text = re.sub(r'\D', '', text)

        if len(cleaned_text) > 4:
            cleaned_text = cleaned_text[:4]

        self.anio = cleaned_text
        
        self.input_anio.blockSignals(True)
        self.input_anio.setText(cleaned_text)
        self.input_anio.blockSignals(False)
        
    def set_f_inscripcion(self, text):
        self.input_f_inscripcion.setText(text)
        
    def set_comuna(self, text):
        self.comuna_combo.setCurrentText(text)
    
    def set_cbr(self, text):
        self.input_cbr.setText(text)
        
    def set_foja(self, text):
        self.input_foja.setText(text)
        
    def set_vta(self, valor):
        self.checkbox_vta.setChecked(valor)
        
    def set_numero(self, text):
        self.input_num.setText(text)
        
    def set_anio(self, text):
        self.input_anio.setText(text)
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)  
    main_window = QMainWindow()  
    inscripcion_widget = Inscripcion()
    main_window.setCentralWidget(inscripcion_widget)  
    main_window.setWindowTitle("Formulario de Inscripción")  
    main_window.show()  
    sys.exit(app.exec_())
