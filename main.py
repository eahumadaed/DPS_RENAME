from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton, QLabel, QComboBox
import sys
import requests
from next_window import NextWindow
import traceback

def log_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    with open("error_log.txt", "w") as f:
        f.write("Ocurrió un error no capturado:\n")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)

    print("Ha ocurrido un error. Revisa el archivo error_log.txt para más detalles.")
    input("Presiona Enter para salir...")

sys.excepthook = log_exception

class UserSelectionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Seleccionar Usuario')
        self.setGeometry(100, 100, 300, 50)
        self.center_window()
        
        self.layout = QVBoxLayout()
        
        self.label = QLabel("Seleccione un usuario:", self)
        self.layout.addWidget(self.label)
        
        self.user_select = QComboBox(self)
        self.layout.addWidget(self.user_select)
        
        self.continue_button = QPushButton("Continuar", self)
        self.continue_button.clicked.connect(self.load_next_interface)
        self.layout.addWidget(self.continue_button)
        
        self.setLayout(self.layout)
        self.load_users()

    def load_users(self):
        try:
            response = requests.get('https://loverman.net/dbase/dga2024/api/api.php?action=getUsers', timeout=10)
            response.raise_for_status()
            users = response.json()
            for user in users:
                user_info = f"{user['name']}"
                self.user_select.addItem(user_info, user['id'])
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener los usuarios: {e}")
            self.label.setText("Error al obtener los usuarios")
        except ValueError as e:
            print(f"Error al interpretar la respuesta: {e}")
            self.label.setText("Error al interpretar la respuesta")

    def load_next_interface(self):
        selected_user_id = self.user_select.currentData()
        print(f"ID del usuario seleccionado: {selected_user_id}")
        self.close()
        self.next_window = NextWindow(selected_user_id)
        self.next_window.showMaximized()

    def center_window(self):
        window_size = self.sizeHint()
        screen = self.screen().geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.setGeometry(x, y, 300, 50)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = UserSelectionWindow()
    main_window.show()
    try:
        sys.exit(app.exec_())
    except Exception as e:
        log_exception(type(e), e, e.__traceback__)
