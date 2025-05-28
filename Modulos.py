import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

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

vacaciones_ocupadas = set()
registros_personal = {}
asistencias_registradas = {}
retardos_registrados = {}

def generar_vacaciones():
    disponibles = []
    fecha_base = datetime(datetime.now().year, 1, 1)
    for i in range(0, 365, 15):
        inicio = fecha_base + timedelta(days=i)
        fin = inicio + timedelta(days=14)
        periodo = f"{inicio.strftime('%d/%m/%Y')} - {fin.strftime('%d/%m/%Y')}"
        disponibles.append(periodo)
    return disponibles

vacaciones_disponibles = generar_vacaciones()

PUESTOS = ["Doctor", "Enfermero", "Administrativo", "Limpieza", "Seguridad", "Técnico"]

TURNOS = {
    "Matutino (07:00 - 15:00)": ("07:00", "15:00"),
    "Vespertino (15:00 - 23:00)": ("15:00", "23:00"),
    "Madrugada (23:00 - 07:00)": ("23:00", "07:00")
}

TOLERANCIA_MINUTOS = 10 

class HospitalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Control de Asistencias - Hospital")
        self.state("zoomed")
        self.configure(bg=COLORS["bg_main"])

        self.frames = {}
        self.create_layout()

        for FrameClass in (InicioFrame, RegistroFrame, VacacionesFrame, TurnoFrame, AsistenciaFrame, HistorialFrame):
            frame = FrameClass(self.main_frame, self)
            self.frames[FrameClass.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("InicioFrame")

    def create_layout(self):
        header = tk.Frame(self, bg=COLORS["primary"], height=50)
        header.pack(side="top", fill="x")

        title_label = tk.Label(header, text="Sistema Profesional de Asistencia - Hospital",
                               bg=COLORS["primary"], fg="white", font=FONT_TITLE, anchor="w", padx=20)
        title_label.pack(side="left", fill="y")

        self.clock_label = tk.Label(header, bg=COLORS["primary"], fg="white", font=("Segoe UI", 12))
        self.clock_label.pack(side="right", padx=20)
        self.update_clock()

        sidebar = tk.Frame(self, bg=COLORS["sidebar"], width=200)
        sidebar.pack(side="left", fill="y")

        buttons = [
            ("Inicio", "InicioFrame"),
            ("Registro", "RegistroFrame"),
            ("Vacaciones", "VacacionesFrame"),
            ("Turno y Horario", "TurnoFrame"),
            ("Asistencia", "AsistenciaFrame"),
            ("Historial", "HistorialFrame")
        ]

        for text, frame_name in buttons:
            tk.Button(sidebar, text=text, font=FONT_NORMAL, fg="white", bg=COLORS["sidebar"],
                      activebackground=COLORS["accent"], activeforeground="black", bd=0, pady=12,
                      command=lambda name=frame_name: self.show_frame(name)).pack(fill="x")

        self.main_frame = tk.Frame(self, bg=COLORS["bg_main"])
        self.main_frame.pack(side="right", fill="both", expand=True)

    def update_clock(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.clock_label.config(text=now)
        self.after(1000, self.update_clock)

    def show_frame(self, name):
        frame = self.frames[name]
        if name == "HistorialFrame":
            frame.actualizar_ids()
        frame.lift()

class InicioFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])
        tk.Label(self, text="Bienvenido al Sistema de Asistencia Hospitalaria",
                 font=FONT_TITLE, bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(pady=40)

class RegistroFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])
        tk.Label(self, text="Registro de Personal", font=FONT_TITLE,
                 bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(pady=20)

        form_frame = tk.Frame(self, bg=COLORS["bg_card"], bd=2, relief="groove")
        form_frame.place(relx=0.5, rely=0.1, anchor="n", width=600, height=350)

        labels = ["ID:", "Nombre:", "Puesto:", "Edad:", "NSS:"]
        self.entries = {}

        for i, text in enumerate(labels):
            tk.Label(form_frame, text=text, font=FONT_NORMAL, bg=COLORS["bg_card"]).place(relx=0.1, rely=0.1 + i*0.15)
        
        self.entries["id"] = tk.Entry(form_frame, font=FONT_NORMAL)
        self.entries["id"].place(relx=0.4, rely=0.1, relwidth=0.45)

        self.entries["nombre"] = tk.Entry(form_frame, font=FONT_NORMAL)
        self.entries["nombre"].place(relx=0.4, rely=0.25, relwidth=0.45)

        self.puesto_combo = ttk.Combobox(form_frame, font=FONT_NORMAL, values=PUESTOS, state="readonly")
        self.puesto_combo.place(relx=0.4, rely=0.4, relwidth=0.45)
        self.puesto_combo.set(PUESTOS[0])

        self.entries["edad"] = tk.Entry(form_frame, font=FONT_NORMAL)
        self.entries["edad"].place(relx=0.4, rely=0.55, relwidth=0.45)

        self.entries["nss"] = tk.Entry(form_frame, font=FONT_NORMAL)
        self.entries["nss"].place(relx=0.4, rely=0.7, relwidth=0.45)

        tk.Button(form_frame, text="Registrar", font=FONT_NORMAL, bg=COLORS["primary"], fg="white",
                  command=self.guardar_registro).place(relx=0.3, rely=0.85, relwidth=0.4)

    def guardar_registro(self):
        id_ = self.entries["id"].get().strip()
        nombre = self.entries["nombre"].get().strip()
        puesto = self.puesto_combo.get()
        edad = self.entries["edad"].get().strip()
        nss = self.entries["nss"].get().strip()

        if not id_ or not nombre or not edad.isdigit() or not nss:
            messagebox.showerror("Error", "Por favor completa todos los campos correctamente.")
            return

        registros_personal[id_] = {
            "nombre": nombre,
            "puesto": puesto,
            "edad": int(edad),
            "nss": nss,
            "vacaciones": None,
            "turno": None,
            "horario_inicio": None,
            "horario_fin": None
        }
        messagebox.showinfo("Registro", f"Personal '{nombre}' registrado correctamente.")
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.puesto_combo.set(PUESTOS[0])

class VacacionesFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])
        tk.Label(self, text="Asignación de Vacaciones", font=FONT_TITLE,
                 bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(pady=20)

        form_frame = tk.Frame(self, bg=COLORS["bg_card"], bd=2, relief="groove")
        form_frame.place(relx=0.5, rely=0.25, anchor="n", width=650, height=250)  # ancho aumentado

        tk.Label(form_frame, text="ID del trabajador:", font=FONT_NORMAL, bg=COLORS["bg_card"]).place(relx=0.1, rely=0.2)
        self.id_entry = tk.Entry(form_frame, font=FONT_NORMAL)
        self.id_entry.place(relx=0.4, rely=0.2, relwidth=0.45)

        tk.Label(form_frame, text="Selecciona periodo de vacaciones:", font=FONT_NORMAL, bg=COLORS["bg_card"]).place(relx=0.1, rely=0.5)
        self.combo_vacaciones = ttk.Combobox(form_frame, font=FONT_NORMAL, values=self.obtener_periodos_disponibles(), state="readonly", width=40)
        self.combo_vacaciones.place(relx=0.4, rely=0.5, relwidth=0.45)

        tk.Button(form_frame, text="Asignar Vacaciones", font=FONT_NORMAL, bg=COLORS["primary"], fg="white",
                  command=self.asignar).place(relx=0.3, rely=0.8, relwidth=0.4)

    def obtener_periodos_disponibles(self):
        return [p for p in vacaciones_disponibles if p not in vacaciones_ocupadas]

    def asignar(self):
        id_ = self.id_entry.get().strip()
        periodo = self.combo_vacaciones.get()

        if not id_:
            messagebox.showerror("Error", "Por favor ingresa un ID válido")
            return

        if id_ not in registros_personal:
            messagebox.showerror("Error", "El ID no está registrado en el sistema")
            return

        if not periodo:
            messagebox.showerror("Error", "Selecciona un periodo de vacaciones")
            return

        if periodo in vacaciones_ocupadas:
            messagebox.showerror("Ocupado", "Ese periodo ya está asignado a otro trabajador")
            return

        vac_antigua = registros_personal[id_]["vacaciones"]
        if vac_antigua:
            vacaciones_ocupadas.discard(vac_antigua)

        registros_personal[id_]["vacaciones"] = periodo
        vacaciones_ocupadas.add(periodo)
        messagebox.showinfo("Asignado", f"Vacaciones asignadas a {registros_personal[id_]['nombre']}:\n{periodo}")

       
        self.combo_vacaciones['values'] = self.obtener_periodos_disponibles()
        self.combo_vacaciones.set("")
        self.id_entry.delete(0, tk.END)

class TurnoFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])
        tk.Label(self, text="Asignación de Turno y Horario", font=FONT_TITLE,
                 bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(pady=20)

        form_frame = tk.Frame(self, bg=COLORS["bg_card"], bd=2, relief="groove")
        form_frame.place(relx=0.5, rely=0.25, anchor="n", width=600, height=250)

        tk.Label(form_frame, text="ID del trabajador:", font=FONT_NORMAL, bg=COLORS["bg_card"]).place(relx=0.1, rely=0.2)
        self.id_entry = tk.Entry(form_frame, font=FONT_NORMAL)
        self.id_entry.place(relx=0.4, rely=0.2, relwidth=0.45)

        tk.Label(form_frame, text="Selecciona turno:", font=FONT_NORMAL, bg=COLORS["bg_card"]).place(relx=0.1, rely=0.5)
        self.combo_turno = ttk.Combobox(form_frame, font=FONT_NORMAL, values=list(TURNOS.keys()), state="readonly")
        self.combo_turno.place(relx=0.4, rely=0.5, relwidth=0.45)

        tk.Button(form_frame, text="Asignar Turno", font=FONT_NORMAL, bg=COLORS["primary"], fg="white",
                  command=self.asignar).place(relx=0.3, rely=0.8, relwidth=0.4)

    def asignar(self):
        id_ = self.id_entry.get().strip()
        turno = self.combo_turno.get()

        if not id_:
            messagebox.showerror("Error", "Por favor ingresa un ID válido")
            return

        if id_ not in registros_personal:
            messagebox.showerror("Error", "El ID no está registrado en el sistema")
            return

        if not turno:
            messagebox.showerror("Error", "Selecciona un turno")
            return

        horario_inicio, horario_fin = TURNOS[turno]

        registros_personal[id_]["turno"] = turno
        registros_personal[id_]["horario_inicio"] = horario_inicio
        registros_personal[id_]["horario_fin"] = horario_fin
        messagebox.showinfo("Asignado", f"Turno '{turno}' asignado a {registros_personal[id_]['nombre']}.")
        self.combo_turno.set("")
        self.id_entry.delete(0, tk.END)

class AsistenciaFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])
        tk.Label(self, text="Registro de Asistencia", font=FONT_TITLE,
                 bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(pady=20)

        form_frame = tk.Frame(self, bg=COLORS["bg_card"], bd=2, relief="groove")
        form_frame.place(relx=0.5, rely=0.25, anchor="n", width=600, height=200)

        tk.Label(form_frame, text="ID del trabajador:", font=FONT_NORMAL, bg=COLORS["bg_card"]).place(relx=0.1, rely=0.3)
        self.id_entry = tk.Entry(form_frame, font=FONT_NORMAL)
        self.id_entry.place(relx=0.4, rely=0.3, relwidth=0.45)

        tk.Button(form_frame, text="Registrar asistencia", font=FONT_NORMAL, bg=COLORS["primary"], fg="white",
                  command=self.registrar_asistencia).place(relx=0.3, rely=0.7, relwidth=0.4)

    def registrar_asistencia(self):
        id_ = self.id_entry.get().strip()
        if id_ not in registros_personal:
            messagebox.showerror("Error", "El ID no está registrado.")
            return

        turno = registros_personal[id_].get("turno")
        horario_inicio_str = registros_personal[id_].get("horario_inicio")
        horario_fin_str = registros_personal[id_].get("horario_fin")

        if not turno or not horario_inicio_str or not horario_fin_str:
            messagebox.showerror("Error", "El trabajador no tiene turno y horario asignados.")
            return

        ahora = datetime.now()

    
        hora_inicio = datetime.strptime(horario_inicio_str, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day)
        hora_fin = datetime.strptime(horario_fin_str, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day)

      
        if hora_fin <= hora_inicio:
            hora_fin += timedelta(days=1)


        hora_tolerancia = hora_inicio + timedelta(minutes=TOLERANCIA_MINUTOS)

        mensaje = ""
        retardado = False

        if ahora <= hora_tolerancia:
            mensaje = "Asistencia registrada. Estás a tiempo."
        else:
            mensaje = "Asistencia registrada. Retardo detectado."
            retardado = True
            retardos_registrados[id_] = retardos_registrados.get(id_, 0) + 1

        # Registrar asistencia
        asistencias_registradas.setdefault(id_, []).append(ahora.strftime("%d/%m/%Y %H:%M:%S"))

        messagebox.showinfo("Asistencia", f"{mensaje}\nHora: {ahora.strftime('%H:%M:%S')}")
        self.id_entry.delete(0, tk.END)

class HistorialFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])
        tk.Label(self, text="Historial de Asistencias y Retardos", font=FONT_TITLE,
                 bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(pady=20)

        control_frame = tk.Frame(self, bg=COLORS["bg_main"])
        control_frame.pack(pady=10)

        tk.Label(control_frame, text="Selecciona ID:", font=FONT_NORMAL, bg=COLORS["bg_main"]).pack(side="left")
        self.combo_id = ttk.Combobox(control_frame, font=FONT_NORMAL, state="readonly")
        self.combo_id.pack(side="left", padx=5)

        tk.Button(control_frame, text="Mostrar historial", font=FONT_NORMAL,
                  command=self.mostrar_historial).pack(side="left", padx=5)

        self.text_historial = tk.Text(self, width=80, height=20, font=("Segoe UI", 10))
        self.text_historial.pack(padx=20, pady=10)

    def actualizar_ids(self):
        ids = list(registros_personal.keys())
        self.combo_id['values'] = ids
        if ids:
            self.combo_id.current(0)
        self.text_historial.delete("1.0", tk.END)

    def mostrar_historial(self):
        id_ = self.combo_id.get()
        if id_ not in registros_personal:
            messagebox.showerror("Error", "Selecciona un ID válido.")
            return
        self.text_historial.delete("1.0", tk.END)

        personal = registros_personal[id_]
        historial_asist = asistencias_registradas.get(id_, [])
        retardos = retardos_registrados.get(id_, 0)

        texto = f"Nombre: {personal['nombre']}\n"
        texto += f"Puesto: {personal['puesto']}\n"
        texto += f"Edad: {personal['edad']}\n"
        texto += f"NSS: {personal['nss']}\n"
        texto += f"Vacaciones asignadas: {personal['vacaciones']}\n"
        texto += f"Turno asignado: {personal['turno']}\n\n"
        texto += "Historial de asistencias:\n"
        if historial_asist:
            for i, registro in enumerate(historial_asist, 1):
                texto += f"  {i}. {registro}\n"
        else:
            texto += "  No hay registros de asistencia.\n"
        texto += f"\nTotal de retardos: {retardos}"

        self.text_historial.insert(tk.END, texto)


if __name__ == "__main__":
    app = HospitalApp()
    app.mainloop()
