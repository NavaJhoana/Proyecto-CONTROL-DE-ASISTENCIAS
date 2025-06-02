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
registros_personal = {} # Este diccionario ahora almacenará todos los datos del personal
asistencias_registradas = {}
retardos_registrados = {}
salidas_registradas = {}
horas_extra_registradas = {}


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

        for FrameClass in (InicioFrame, RegistroFrame, VacacionesFrame, TurnoFrame, AsistenciaFrame, SalidaFrame, HistorialFrame):
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
            ("Salida", "SalidaFrame"),
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
        elif name == "SalidaFrame":
            frame.actualizar_ids_salida()
        elif name == "RegistroFrame": # Nuevo: Actualiza la tabla de registro al mostrar la sección
            frame.actualizar_tabla_personal()
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

        # Frame para el formulario de entrada de datos
        form_entry_frame = tk.Frame(self, bg=COLORS["bg_card"], bd=2, relief="groove")
        form_entry_frame.pack(pady=10, padx=20, fill='x', expand=False) # Ajustado para nuevos campos

        # Configuración de columnas para el formulario de entrada para mejor alineación
        form_entry_frame.grid_columnconfigure(0, weight=1)
        form_entry_frame.grid_columnconfigure(1, weight=3)

        self.entries = {}
        self.comboboxes = {}
        self.radio_vars = {}

        # --- Campos Originales ---
        labels_original = ["ID:", "Nombre:", "Puesto:", "Edad:", "NSS:"]
        entry_keys_original = ["id", "nombre", "puesto", "edad", "nss"]
        
        for i, text in enumerate(labels_original):
            tk.Label(form_entry_frame, text=text, font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=i, column=0, padx=5, pady=2, sticky='e')
            if text == "Puesto:":
                self.puesto_combo = ttk.Combobox(form_entry_frame, font=FONT_NORMAL, values=PUESTOS, state="readonly", width=30)
                self.puesto_combo.grid(row=i, column=1, padx=5, pady=2, sticky='w')
                self.puesto_combo.set(PUESTOS[0])
                self.comboboxes["puesto"] = self.puesto_combo
            else:
                entry = tk.Entry(form_entry_frame, font=FONT_NORMAL, width=30)
                entry.grid(row=i, column=1, padx=5, pady=2, sticky='w')
                self.entries[entry_keys_original[i]] = entry
        
        # --- Nuevos Campos ---
        current_row = len(labels_original) # Empezar después de los campos originales

        # Fecha de Nacimiento
        tk.Label(form_entry_frame, text="Fecha de Nacimiento (AAAA-MM-DD):", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=current_row, column=0, padx=5, pady=2, sticky='e')
        self.entries["fecha_nacimiento"] = tk.Entry(form_entry_frame, font=FONT_NORMAL, width=30)
        self.entries["fecha_nacimiento"].grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
        current_row += 1

        # Tipo de Contratación
        tk.Label(form_entry_frame, text="Tipo de Contratación:", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=current_row, column=0, padx=5, pady=2, sticky='e')
        tipos_contratacion = ["Basificados", "Homologados", "Regularizados", "Contrato"]
        self.comboboxes["tipo_contratacion"] = ttk.Combobox(form_entry_frame, values=tipos_contratacion, font=FONT_NORMAL, state="readonly", width=28)
        self.comboboxes["tipo_contratacion"].grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
        self.comboboxes["tipo_contratacion"].set('Selecciona tipo')
        current_row += 1

        # Sexo
        tk.Label(form_entry_frame, text="Sexo:", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=current_row, column=0, padx=5, pady=2, sticky='e')
        sexo_frame = tk.Frame(form_entry_frame, bg=COLORS["bg_card"])
        sexo_frame.grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
        self.radio_vars["sexo"] = tk.StringVar()
        tk.Radiobutton(sexo_frame, text="Masculino", variable=self.radio_vars["sexo"], value="Masculino", font=FONT_NORMAL, bg=COLORS["bg_card"]).pack(side='left')
        tk.Radiobutton(sexo_frame, text="Femenino", variable=self.radio_vars["sexo"], value="Femenino", font=FONT_NORMAL, bg=COLORS["bg_card"]).pack(side='left', padx=10)
        current_row += 1

        # Último Grado de Estudio
        tk.Label(form_entry_frame, text="Último Grado de Estudio:", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=current_row, column=0, padx=5, pady=2, sticky='e')
        grados_estudio = ["Primaria", "Secundaria", "Bachillerato", "Técnico", "Licenciatura", "Maestría", "Doctorado"]
        self.comboboxes["grado_estudio"] = ttk.Combobox(form_entry_frame, values=grados_estudio, font=FONT_NORMAL, state="readonly", width=28)
        self.comboboxes["grado_estudio"].grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
        self.comboboxes["grado_estudio"].set('Selecciona grado')
        current_row += 1

        # Cédula Profesional
        tk.Label(form_entry_frame, text="Cédula Profesional:", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=current_row, column=0, padx=5, pady=2, sticky='e')
        self.entries["cedula_profesional"] = tk.Entry(form_entry_frame, font=FONT_NORMAL, width=30)
        self.entries["cedula_profesional"].grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
        current_row += 1

        # Domicilio
        tk.Label(form_entry_frame, text="Domicilio:", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=current_row, column=0, padx=5, pady=2, sticky='e')
        self.entries["domicilio"] = tk.Entry(form_entry_frame, font=FONT_NORMAL, width=30)
        self.entries["domicilio"].grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
        current_row += 1

        # Teléfono
        tk.Label(form_entry_frame, text="Teléfono:", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=current_row, column=0, padx=5, pady=2, sticky='e')
        self.entries["telefono"] = tk.Entry(form_entry_frame, font=FONT_NORMAL, width=30)
        self.entries["telefono"].grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
        current_row += 1

        # Correo Electrónico
        tk.Label(form_entry_frame, text="Correo Electrónico:", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=current_row, column=0, padx=5, pady=2, sticky='e')
        self.entries["correo_electronico"] = tk.Entry(form_entry_frame, font=FONT_NORMAL, width=30)
        self.entries["correo_electronico"].grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
        current_row += 1

        # Fecha de Ingreso
        tk.Label(form_entry_frame, text="Fecha de Ingreso (AAAA-MM-DD):", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=current_row, column=0, padx=5, pady=2, sticky='e')
        self.entries["fecha_ingreso"] = tk.Entry(form_entry_frame, font=FONT_NORMAL, width=30)
        self.entries["fecha_ingreso"].grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
        current_row += 1


        # Botón para registrar
        tk.Button(self, text="Registrar Personal", font=FONT_NORMAL, bg=COLORS["primary"], fg="white",
                  command=self.guardar_registro).pack(pady=10)

        # --- Tabla de Historial de Personal (Nueva adición) ---
        tk.Label(self, text="Historial de Personal Registrado", font=FONT_TITLE,
                 bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(pady=20)

        tree_frame = tk.Frame(self, bg=COLORS["bg_card"])
        tree_frame.pack(padx=20, pady=10, fill='both', expand=True)

        columns = ("ID", "Nombre", "Puesto", "Edad", "NSS", "Fecha Nac.", "Tipo Cont.",
                   "Sexo", "Grado Est.", "Cédula Prof.", "Domicilio", "Teléfono", "Email", "Fecha Ing.")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)

        # Configurar encabezados de columnas
        for col in columns:
            self.tree.heading(col, text=col)
            # Ajustar anchos para que se vean todos los datos
            if col in ["ID", "Edad", "NSS"]:
                self.tree.column(col, width=70, anchor="center")
            elif col in ["Nombre", "Domicilio", "Email"]:
                self.tree.column(col, width=120, anchor="w")
            elif col in ["Puesto", "Tipo Cont.", "Grado Est."]:
                self.tree.column(col, width=100, anchor="center")
            elif col in ["Fecha Nac.", "Fecha Ing."]:
                self.tree.column(col, width=90, anchor="center")
            else:
                self.tree.column(col, width=80, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)

        # Añadir scrollbar
        scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar_y.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        scrollbar_x.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=scrollbar_x.set)

        self.actualizar_tabla_personal()


    def guardar_registro(self):
        # Campos originales
        id_ = self.entries["id"].get().strip()
        nombre = self.entries["nombre"].get().strip()
        puesto = self.comboboxes["puesto"].get()
        edad_str = self.entries["edad"].get().strip()
        nss = self.entries["nss"].get().strip()

        # Nuevos campos
        fecha_nacimiento = self.entries["fecha_nacimiento"].get().strip()
        tipo_contratacion = self.comboboxes["tipo_contratacion"].get()
        sexo = self.radio_vars["sexo"].get()
        ultimo_grado_estudio = self.comboboxes["grado_estudio"].get()
        cedula_profesional = self.entries["cedula_profesional"].get().strip()
        domicilio = self.entries["domicilio"].get().strip()
        telefono = self.entries["telefono"].get().strip()
        correo_electronico = self.entries["correo_electronico"].get().strip()
        fecha_ingreso = self.entries["fecha_ingreso"].get().strip()

        # Validaciones
        if not all([id_, nombre, puesto, edad_str, nss, fecha_nacimiento,
                    tipo_contratacion, sexo, ultimo_grado_estudio,
                    domicilio, telefono, correo_electronico, fecha_ingreso]):
            messagebox.showerror("Error", "Por favor completa todos los campos obligatorios.")
            return

        if not edad_str.isdigit():
            messagebox.showerror("Error", "La edad debe ser un número.")
            return
        edad = int(edad_str)

        if id_ in registros_personal:
            messagebox.showerror("Error", "El ID ya está registrado. Por favor, usa un ID diferente.")
            return

        try:
            datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
            datetime.strptime(fecha_ingreso, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error de Formato", "Las fechas deben estar en formato AAAA-MM-DD (ej: 2000-01-31).")
            return
        
        if telefono and not telefono.isdigit():
            messagebox.showerror("Error", "El teléfono debe contener solo números.")
            return

        # Guardar todos los datos en registros_personal
        registros_personal[id_] = {
            "nombre": nombre,
            "puesto": puesto,
            "edad": edad,
            "nss": nss,
            "fecha_nacimiento": fecha_nacimiento,
            "tipo_contratacion": tipo_contratacion,
            "sexo": sexo,
            "ultimo_grado_estudio": ultimo_grado_estudio,
            "cedula_profesional": cedula_profesional,
            "domicilio": domicilio,
            "telefono": telefono,
            "correo_electronico": correo_electronico,
            "fecha_ingreso": fecha_ingreso,
            "vacaciones": None,
            "turno": None,
            "horario_inicio": None,
            "horario_fin": None
        }

        messagebox.showinfo("Registro Exitoso", f"Personal '{nombre}' con ID '{id_}' registrado correctamente.")

        # Limpiar campos después de guardar
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        for combo in self.comboboxes.values():
            if combo.winfo_exists(): # Check if widget exists (e.g., puesto_combo is moved to self.comboboxes)
                combo.set('') # Clear selected value
        for var in self.radio_vars.values():
            var.set('') # Clear radio button selection

        self.actualizar_tabla_personal() # Actualizar la tabla de historial

    def actualizar_tabla_personal(self):
        # Limpiar la tabla actual
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insertar todos los registros de personal en la tabla
        for id_trabajador, data in registros_personal.items():
            self.tree.insert("", "end", values=(
                id_trabajador,
                data.get("nombre", ""),
                data.get("puesto", ""),
                data.get("edad", ""),
                data.get("nss", ""),
                data.get("fecha_nacimiento", ""),
                data.get("tipo_contratacion", ""),
                data.get("sexo", ""),
                data.get("ultimo_grado_estudio", ""),
                data.get("cedula_profesional", ""),
                data.get("domicilio", ""),
                data.get("telefono", ""),
                data.get("correo_electronico", ""),
                data.get("fecha_ingreso", "")
            ))


class VacacionesFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])
        tk.Label(self, text="Asignación de Vacaciones", font=FONT_TITLE,
                 bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(pady=20)

        form_frame = tk.Frame(self, bg=COLORS["bg_card"], bd=2, relief="groove")
        form_frame.place(relx=0.5, rely=0.25, anchor="n", width=650, height=250)

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
        fecha_actual_str = ahora.strftime("%d/%m/%Y")

        if id_ in asistencias_registradas and fecha_actual_str in asistencias_registradas[id_]:
            messagebox.showwarning("Advertencia", f"La asistencia para el ID {id_} ya ha sido registrada hoy.")
            return

        hora_inicio_dt = datetime.strptime(horario_inicio_str, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day)
        
        hora_tolerancia_dt = hora_inicio_dt + timedelta(minutes=TOLERANCIA_MINUTOS)

        mensaje = ""
        
        if ahora <= hora_tolerancia_dt:
            mensaje = "Asistencia registrada. Estás a tiempo."
        else:
            mensaje = "Asistencia registrada. Retardo detectado."
            retardos_registrados[id_] = retardos_registrados.get(id_, 0) + 1

        asistencias_registradas.setdefault(id_, {})[fecha_actual_str] = ahora.strftime("%H:%M:%S")

        messagebox.showinfo("Asistencia", f"{mensaje}\nHora: {ahora.strftime('%H:%M:%S')}")
        self.id_entry.delete(0, tk.END)

class SalidaFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])
        tk.Label(self, text="Registro de Salida del Trabajador", font=FONT_TITLE,
                 bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(pady=20)

        form_frame = tk.Frame(self, bg=COLORS["bg_card"], bd=2, relief="groove")
        form_frame.place(relx=0.5, rely=0.25, anchor="n", width=600, height=200)

        tk.Label(form_frame, text="ID del trabajador:", font=FONT_NORMAL, bg=COLORS["bg_card"]).place(relx=0.1, rely=0.3)
        self.combo_id = ttk.Combobox(form_frame, font=FONT_NORMAL, state="readonly")
        self.combo_id.place(relx=0.4, rely=0.3, relwidth=0.45)

        tk.Button(form_frame, text="Registrar Salida", font=FONT_NORMAL, bg=COLORS["primary"], fg="white",
                  command=self.registrar_salida_trabajador).place(relx=0.3, rely=0.7, relwidth=0.4)

    def actualizar_ids_salida(self):
        fecha_actual_str = datetime.now().strftime("%d/%m/%Y")
        ids_disponibles = []
        for id_trabajador in registros_personal.keys():
            if (id_trabajador in asistencias_registradas and
                fecha_actual_str in asistencias_registradas[id_trabajador] and
                (id_trabajador not in salidas_registradas or fecha_actual_str not in salidas_registradas[id_trabajador])):
                ids_disponibles.append(id_trabajador)

        self.combo_id['values'] = ids_disponibles
        if ids_disponibles:
            self.combo_id.current(0)
        else:
            self.combo_id.set("")

    def registrar_salida_trabajador(self):
        id_ = self.combo_id.get().strip()
        if not id_:
            messagebox.showerror("Error", "Por favor selecciona un ID válido.")
            return

        if id_ not in registros_personal:
            messagebox.showerror("Error", "El ID no está registrado en el sistema.")
            return

        turno = registros_personal[id_].get("turno")
        horario_fin_str = registros_personal[id_].get("horario_fin")

        if not turno or not horario_fin_str:
            messagebox.showerror("Error", "El trabajador no tiene turno y horario asignados.")
            return

        ahora = datetime.now()
        fecha_actual_str = ahora.strftime("%d/%m/%Y")
        hora_salida_actual_str = ahora.strftime("%H:%M:%S")

        if id_ not in asistencias_registradas or fecha_actual_str not in asistencias_registradas[id_]:
            messagebox.showerror("Error", "El trabajador no ha registrado su asistencia hoy.")
            return

        if id_ in salidas_registradas and fecha_actual_str in salidas_registradas[id_]:
            messagebox.showwarning("Advertencia", f"La salida para el ID {id_} ya ha sido registrada hoy.")
            return

        hora_entrada_registrada_str = asistencias_registradas[id_][fecha_actual_str]
        hora_entrada_dt = datetime.strptime(f"{fecha_actual_str} {hora_entrada_registrada_str}", "%d/%m/%Y %H:%M:%S")
        hora_fin_programada_dt = datetime.strptime(horario_fin_str, "%H:%M").replace(
            year=ahora.year, month=ahora.month, day=ahora.day
        )

        if hora_fin_programada_dt < hora_entrada_dt:
            hora_fin_programada_dt += timedelta(days=1)

        tiempo_extra_minutos = 0
        if ahora > hora_fin_programada_dt:
            diferencia_tiempo = ahora - hora_fin_programada_dt
            tiempo_extra_minutos = int(diferencia_tiempo.total_seconds() / 60)

            messagebox.showinfo("Salida Registrada",
                                 f"Salida registrada para {registros_personal[id_]['nombre']}.\n"
                                 f"Hora de Salida: {hora_salida_actual_str}\n"
                                 f"¡Tiempo extra trabajado: {tiempo_extra_minutos} minutos!")
        else:
            messagebox.showinfo("Salida Registrada",
                                 f"Salida registrada para {registros_personal[id_]['nombre']}.\n"
                                 f"Hora de Salida: {hora_salida_actual_str}")

        salidas_registradas.setdefault(id_, {})[fecha_actual_str] = hora_salida_actual_str
        if tiempo_extra_minutos > 0:
            horas_extra_registradas.setdefault(id_, {})[fecha_actual_str] = tiempo_extra_minutos

        self.combo_id.set("")
        self.actualizar_ids_salida()


class HistorialFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])
        tk.Label(self, text="Historial de Asistencias, Salidas y Horas Extra", font=FONT_TITLE,
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
        retardos = retardos_registrados.get(id_, 0)

        fechas_registradas = set(asistencias_registradas.get(id_, {}).keys())
        fechas_registradas.update(salidas_registradas.get(id_, {}).keys())
        fechas_registradas.update(horas_extra_registradas.get(id_, {}).keys())

        fechas_ordenadas = sorted(list(fechas_registradas), key=lambda x: datetime.strptime(x, "%d/%m/%Y"), reverse=True)


        texto = f"""
--- Detalles del Empleado ---
Nombre: {personal['nombre']}
Puesto: {personal['puesto']}
Edad: {personal['edad']}
NSS: {personal['nss']}
Fecha de Nacimiento: {personal.get('fecha_nacimiento', 'No especificado')}
Tipo de Contratación: {personal.get('tipo_contratacion', 'No especificado')}
Sexo: {personal.get('sexo', 'No especificado')}
Último Grado de Estudio: {personal.get('ultimo_grado_estudio', 'No especificado')}
Cédula Profesional: {personal.get('cedula_profesional', 'No especificado')}
Domicilio: {personal.get('domicilio', 'No especificado')}
Teléfono: {personal.get('telefono', 'No especificado')}
Correo Electrónico: {personal.get('correo_electronico', 'No especificado')}
Fecha de Ingreso: {personal.get('fecha_ingreso', 'No especificado')}
Vacaciones asignadas: {personal['vacaciones'] if personal['vacaciones'] else 'No asignadas'}
Turno asignado: {personal['turno'] if personal['turno'] else 'No asignado'}
-----------------------------

--- Historial Diario ---
"""
        if fechas_ordenadas:
            for fecha in fechas_ordenadas:
                entrada = asistencias_registradas.get(id_, {}).get(fecha, 'No registrada')
                salida = salidas_registradas.get(id_, {}).get(fecha, 'No registrada')
                tiempo_extra = horas_extra_registradas.get(id_, {}).get(fecha, 0)

                texto += f"  Fecha: {fecha}\n"
                texto += f"    Entrada: {entrada}\n"
                texto += f"    Salida: {salida}\n"
                if tiempo_extra > 0:
                    texto += f"    Horas Extra: {tiempo_extra} minutos\n"
                texto += "\n"
        else:
            texto += "  No hay registros de asistencia ni salida para este empleado.\n"

        texto += f"-----------------------------\n"
        texto += f"Total de Retardos Acumulados: {retardos}\n"
        texto += "-----------------------------"

        self.text_historial.insert(tk.END, texto)


if __name__ == "__main__":
    app = HospitalApp()
    app.mainloop()
