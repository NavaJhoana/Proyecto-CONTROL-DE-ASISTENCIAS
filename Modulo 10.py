import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Diccionarios globales
registros_personal = {}
incapacidades_registradas = {}
licencias_registradas = {}
vacaciones_jerarquia = {}

# Colores y fuentes
COLORS = {
    "bg_main": "#f5f5f5",
    "bg_card": "#ffffff",
    "primary": "#1565c0",
    "text_dark": "#212121",
    "sidebar": "#0d47a1",
    "accent": "#0288d1"
}
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_NORMAL = ("Segoe UI", 11)

class HospitalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Control de Asistencias - Hospital")
        self.state("zoomed")
        self.configure(bg=COLORS["bg_main"])

        self.frames = {}
        self.create_layout()

        for FrameClass in (InicioFrame, IncapacidadesFrame, LicenciasFrame, VacacionesJerarquiaFrame, HistorialFrame):
            frame = FrameClass(self.main_frame, self)
            self.frames[FrameClass.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("InicioFrame")

    def create_layout(self):
        header = tk.Frame(self, bg=COLORS["primary"], height=50)
        header.pack(side="top", fill="x")
        tk.Label(header, text="Sistema de Asistencias - Hospital", bg=COLORS["primary"],
                 fg="white", font=FONT_TITLE).pack(side="left", padx=20)

        sidebar = tk.Frame(self, bg=COLORS["sidebar"], width=200)
        sidebar.pack(side="left", fill="y")

        botones = [
            ("Inicio", "InicioFrame"),
            ("Incapacidades", "IncapacidadesFrame"),
            ("Licencias", "LicenciasFrame"),
            ("Vacaciones Jerarquía", "VacacionesJerarquiaFrame"),
            ("Historial", "HistorialFrame")
        ]

        for texto, frame in botones:
            tk.Button(sidebar, text=texto, font=FONT_NORMAL, fg="white", bg=COLORS["sidebar"],
                      activebackground=COLORS["accent"], bd=0, pady=10,
                      command=lambda f=frame: self.show_frame(f)).pack(fill="x")

        self.main_frame = tk.Frame(self, bg=COLORS["bg_main"])
        self.main_frame.pack(side="right", fill="both", expand=True)

    def show_frame(self, name):
        frame = self.frames[name]
        if name == "HistorialFrame":
            frame.actualizar_ids()
        frame.lift()
class InicioFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])
        tk.Label(self, text="Bienvenido al Sistema", font=FONT_TITLE,
                 bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(pady=40)

class IncapacidadesFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])
        tk.Label(self, text="Registro de Incapacidades", font=FONT_TITLE,
                 bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(pady=20)

        form = tk.Frame(self, bg=COLORS["bg_card"], bd=2, relief="groove")
        form.place(relx=0.5, rely=0.2, anchor="n", width=500, height=300)

        self.id_entry = self._crear_entrada(form, "ID:", 0)
        self.inicio_entry = self._crear_entrada(form, "Inicio (YYYY-MM-DD):", 1)
        self.fin_entry = self._crear_entrada(form, "Fin (YYYY-MM-DD):", 2)
        self.motivo_entry = self._crear_entrada(form, "Motivo:", 3)

        tk.Button(form, text="Registrar Incapacidad", font=FONT_NORMAL,
                  bg=COLORS["primary"], fg="white", command=self.registrar).grid(row=4, column=0, columnspan=2, pady=10)

    def _crear_entrada(self, frame, texto, fila):
        tk.Label(frame, text=texto, font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=fila, column=0, sticky='e', padx=5, pady=5)
        entrada = tk.Entry(frame, font=FONT_NORMAL)
        entrada.grid(row=fila, column=1, padx=5, pady=5)
        return entrada

    def registrar(self):
        id_ = self.id_entry.get().strip()
        inicio = self.inicio_entry.get().strip()
        fin = self.fin_entry.get().strip()
        motivo = self.motivo_entry.get().strip()

        try:
            f1 = datetime.strptime(inicio, "%Y-%m-%d")
            f2 = datetime.strptime(fin, "%Y-%m-%d")
            if f2 < f1:
                raise ValueError
        except:
            messagebox.showerror("Error", "Fechas inválidas")
            return

        incapacidades_registradas.setdefault(id_, []).append((inicio, fin, motivo))
        messagebox.showinfo("Éxito", f"Incapacidad registrada para {id_}")
        self.id_entry.delete(0, tk.END)
        self.inicio_entry.delete(0, tk.END)
        self.fin_entry.delete(0, tk.END)
        self.motivo_entry.delete(0, tk.END)
class LicenciasFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])
        tk.Label(self, text="Registro de Licencias", font=FONT_TITLE,
                 bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(pady=20)

        form = tk.Frame(self, bg=COLORS["bg_card"], bd=2, relief="groove")
        form.place(relx=0.5, rely=0.2, anchor="n", width=500, height=350)

        self.id_entry = self._crear_entrada(form, "ID:", 0)
        self.inicio_entry = self._crear_entrada(form, "Inicio (YYYY-MM-DD):", 1)
        self.fin_entry = self._crear_entrada(form, "Fin (YYYY-MM-DD):", 2)

        self.tipo = ttk.Combobox(form, values=["Con sueldo", "Sin sueldo"],
                                 state="readonly", font=FONT_NORMAL)
        self.tipo.grid(row=3, column=1, padx=5, pady=5)
        tk.Label(form, text="Tipo:", font=FONT_NORMAL,
                 bg=COLORS["bg_card"]).grid(row=3, column=0, sticky='e')

        self.motivo_entry = self._crear_entrada(form, "Motivo:", 4)

        tk.Button(form, text="Registrar Licencia", font=FONT_NORMAL, bg=COLORS["primary"], fg="white",
                  command=self.registrar).grid(row=5, column=0, columnspan=2, pady=10)

    def _crear_entrada(self, frame, texto, fila):
        tk.Label(frame, text=texto, font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=fila, column=0, sticky='e', padx=5, pady=5)
        entrada = tk.Entry(frame, font=FONT_NORMAL)
        entrada.grid(row=fila, column=1, padx=5, pady=5)
        return entrada

    def registrar(self):
        id_ = self.id_entry.get().strip()
        inicio = self.inicio_entry.get().strip()
        fin = self.fin_entry.get().strip()
        tipo = self.tipo.get()
        motivo = self.motivo_entry.get().strip()

        try:
            f1 = datetime.strptime(inicio, "%Y-%m-%d")
            f2 = datetime.strptime(fin, "%Y-%m-%d")
            dias = (f2 - f1).days
            if dias < 0 or dias > 30:
                raise ValueError
        except:
            messagebox.showerror("Error", "Fechas inválidas o fuera del límite de 1 mes")
            return

        licencias_registradas.setdefault(id_, []).append((inicio, fin, tipo, motivo))
        messagebox.showinfo("Éxito", f"Licencia registrada para {id_}")
        self.id_entry.delete(0, tk.END)
        self.inicio_entry.delete(0, tk.END)
        self.fin_entry.delete(0, tk.END)
        self.tipo.set('')
        self.motivo_entry.delete(0, tk.END)
