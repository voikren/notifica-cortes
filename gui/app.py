import tkinter as tk
from tkinter import filedialog, scrolledtext
from pathlib import Path
import threading
import pandas as pd

from config.settings import settings
from core.lector import cargar_grupos
from core.generador import generar_correo_html
from core.correo import enviar_correo
from core.limpieza import eliminar_filas


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Notifica Cortes")
        self.geometry("600x400")
        self.resizable(False, False)
        self.ruta_archivo = None
        self._construir_ui()

    def _construir_ui(self):
        # Header
        tk.Label(
            self,
            text="Notificación de Cortes",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        # Frame de selección de archivo
        frame_archivo = tk.Frame(self)
        frame_archivo.pack(padx=20, fill="x")

        self.lbl_archivo = tk.Label(
            frame_archivo,
            text="Ningún archivo seleccionado",
            fg="gray",
            font=("Arial", 10)
        )
        self.lbl_archivo.pack(side="left", expand=True, fill="x")

        tk.Button(
            frame_archivo,
            text="Seleccionar archivo",
            command=self._seleccionar_archivo
        ).pack(side="right")

        # Área de logs
        self.log_area = scrolledtext.ScrolledText(
            self,
            state="disabled",
            height=15,
            font=("Courier", 9)
        )
        self.log_area.pack(padx=20, pady=10, fill="both", expand=True)

        # Botón enviar
        self.btn_enviar = tk.Button(
            self,
            text="Enviar",
            command=self._iniciar_envio,
            state="disabled",
            bg="#181919",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=5
        )
        self.btn_enviar.pack(pady=10)

    def _seleccionar_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("Archivos Excel", "*.xlsx")]
        )
        if ruta:
            self.ruta_archivo = Path(ruta)
            self.lbl_archivo.config(
                text=self.ruta_archivo.name,
                fg="black"
            )
            self.btn_enviar.config(state="normal")

    def _log(self, mensaje: str):
        self.log_area.config(state="normal")
        self.log_area.insert("end", f"{mensaje}\n")
        self.log_area.see("end")
        self.log_area.config(state="disabled")

    def _iniciar_envio(self):
        self.btn_enviar.config(state="disabled")
        self._log("Iniciando proceso...")
        threading.Thread(target=self._procesar, daemon=True).start()

    def _procesar(self):
        try:
            df = pd.read_excel(self.ruta_archivo, sheet_name=settings.NOMBRE_HOJA)
            grupos = cargar_grupos(self.ruta_archivo)

            if not grupos:
                self._log("[!] El archivo no tiene datos para procesar.")
                self.btn_enviar.config(state="normal")
                return

            for sucursal_id, contenido in grupos.items():
                correo_html = generar_correo_html(contenido["datos"])
                enviar_correo(contenido["correo"], contenido["cc"], correo_html)
                self._log(f"[OK] Correo enviado a {contenido['correo']}")
                df = eliminar_filas(self.ruta_archivo, df, sucursal_id)
                self._log(f"[OK] Filas de sucursal {sucursal_id} eliminadas")

            self._log("Proceso completado.")

        except Exception as e:
            self._log(f"[ERROR] {e}")
            self.btn_enviar.config(state="normal")


def iniciar_app():
    app = App()
    app.mainloop()