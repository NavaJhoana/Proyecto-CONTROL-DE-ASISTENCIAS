import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta, date

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
registros_personal = {}  # Datos del personal
asistencias_registradas = {} # fecha: hora_entrada
retardos_registrados = {} 
salidas_registradas = {} # fecha: hora_salida
horas_extra_registradas = {} # minutos_extra

retardos_acumulados_quincena = {}
penalizaciones_aplicadas = {}


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

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

TURNOS = {
    "Matutino (07:00 - 14:30)": {
        "horario": ("07:00", "14:30"),
        "dias_laborales": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    },
    "Nocturno A (21:00 - 07:00)": {
        "horario": ("21:00", "07:00"),
        "dias_laborales": ["Lunes", "Miércoles", "Viernes"]
    },
    "Nocturno B (21:00 - 07:00)": {
        "horario": ("21:00", "07:00"),
        "dias_laborales": ["Martes", "Jueves", "Sábado"]
    },
    "Jornada Acumulada (07:00 - 20:30)": {
        "horario": ("07:00", "20:30"),
        "dias_laborales": ["Sábado", "Domingo", "Festivos"]
    },
    "Jornada Acumulada Especial (20:00 - 07:30)": {
        "horario": ("20:00", "07:30"),
        "dias_laborales": ["Sábado", "Domingo", "Festivos"]
    },
    "Jornada Mixta (07:00 - 14:30)": {
        "horario": ("07:00", "14:30"),
        "dias_laborales": ["Lunes", "Martes", "Jueves", "Viernes"]
    },
    "Vespertino (14:00 - 10:30)": {
        "horario": ("14:00", "10:30"),
        "dias_laborales": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    },
    "Nocturno (10:00 - 07:30)": {
        "horario": ("10:00", "07:30"),
        "dias_laborales": ["Lunes", "Martes", "Miércoles"]
    }
}


TURNOS_ESPECIALES = {}

TOLERANCIA_RETARDO_MENOR_MINUTOS = 10 
TOLERANCIA_RETARDO_MAYOR_MINUTOS = 11 

LIMITE_RETARDOS_MENORES = 3
LIMITE_RETARDOS_MAYORES = 2

class HospitalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Control de Asistencias - Hospital")
        self.state("zoomed")
        self.configure(bg=COLORS["bg_main"])

        self.frames = {}
        self.create_layout()

        for FrameClass in (InicioFrame, RegistroFrame, VacacionesFrame, TurnoFrame, AsistenciaFrame, SalidaFrame, PermisosFrame, DiasConcedidosFrame, HistorialFrame, PeriodoExtraFrame):
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
            ("Días Concedidos", "DiasConcedidosFrame"),
            ("Permisos", "PermisosFrame"),
            ("Periodo Extraordinario", "PeriodoExtraFrame"),

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
        elif name == "RegistroFrame":
            frame.actualizar_tabla_personal()
        elif name == "TurnoFrame":
            frame.actualizar_combobox_turnos() # Incluir los turnos especiales 
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

        form_entry_frame = tk.Frame(self, bg=COLORS["bg_card"], bd=2, relief="groove")
        form_entry_frame.pack(pady=10, padx=20, fill='x', expand=False)

        form_entry_frame.grid_columnconfigure(0, weight=1)
        form_entry_frame.grid_columnconfigure(1, weight=3)

        self.entries = {}
        self.comboboxes = {}
        self.radio_vars = {}

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

        current_row = len(labels_original)

        tk.Label(form_entry_frame, text="Fecha de Nacimiento (AAAA-MM-DD):", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=current_row, column=0, padx=5, pady=2, sticky='e')
        self.entries["fecha_nacimiento"] = tk.Entry(form_entry_frame, font=FONT_NORMAL, width=30)
        self.entries["fecha_nacimiento"].grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
        current_row += 1

        tk.Label(form_entry_frame, text="Tipo de Contratación:", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=current_row, column=0, padx=5, pady=2, sticky='e')
        tipos_contratacion = ["Basificados", "Homologados", "Regularizados", "Contrato", "Suplentes o cubreincidencias"]
        self.comboboxes["tipo_contratacion"] = ttk.Combobox(form_entry_frame, values=tipos_contratacion, font=FONT_NORMAL, state="readonly", width=28)
        self.comboboxes["tipo_contratacion"].grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
        self.comboboxes["tipo_contratacion"].set('Selecciona tipo')
        current_row += 1

        tk.Label(form_entry_frame, text="Sexo:", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=current_row, column=0, padx=5, pady=2, sticky='e')
        sexo_frame = tk.Frame(form_entry_frame, bg=COLORS["bg_card"])
        sexo_frame.grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
        self.radio_vars["sexo"] = tk.StringVar()
        tk.Radiobutton(sexo_frame, text="Masculino", variable=self.radio_vars["sexo"], value="Masculino", font=FONT_NORMAL, bg=COLORS["bg_card"]).pack(side='left')
        tk.Radiobutton(sexo_frame, text="Femenino", variable=self.radio_vars["sexo"], value="Femenino", font=FONT_NORMAL, bg=COLORS["bg_card"]).pack(side='left', padx=10)
        current_row += 1

        tk.Label(form_entry_frame, text="Último Grado de Estudio:", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=current_row, column=0, padx=5, pady=2, sticky='e')
        grados_estudio = ["Primaria", "Secundaria", "Bachillerato", "Técnico", "Licenciatura", "Maestría", "Doctorado"]
        self.comboboxes["grado_estudio"] = ttk.Combobox(form_entry_frame, values=grados_estudio, font=FONT_NORMAL, state="readonly", width=28)
        self.comboboxes["grado_estudio"].grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
        self.comboboxes["grado_estudio"].set('Selecciona grado')
        current_row += 1

        tk.Label(form_entry_frame, text="Cédula Profesional:", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=current_row, column=0, padx=5, pady=2, sticky='e')
        self.entries["cedula_profesional"] = tk.Entry(form_entry_frame, font=FONT_NORMAL, width=30)
        self.entries["cedula_profesional"].grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
        current_row += 1

        tk.Label(form_entry_frame, text="Domicilio:", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=current_row, column=0, padx=5, pady=2, sticky='e')
        self.entries["domicilio"] = tk.Entry(form_entry_frame, font=FONT_NORMAL, width=30)
        self.entries["domicilio"].grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
        current_row += 1

        tk.Label(form_entry_frame, text="Teléfono:", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=current_row, column=0, padx=5, pady=2, sticky='e')
        self.entries["telefono"] = tk.Entry(form_entry_frame, font=FONT_NORMAL, width=30)
        self.entries["telefono"].grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
        current_row += 1

        tk.Label(form_entry_frame, text="Correo Electrónico:", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=current_row, column=0, padx=5, pady=2, sticky='e')
        self.entries["correo_electronico"] = tk.Entry(form_entry_frame, font=FONT_NORMAL, width=30)
        self.entries["correo_electronico"].grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
        current_row += 1

        tk.Label(form_entry_frame, text="Fecha de Ingreso (AAAA-MM-DD):", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=current_row, column=0, padx=5, pady=2, sticky='e')
        self.entries["fecha_ingreso"] = tk.Entry(form_entry_frame, font=FONT_NORMAL, width=30)
        self.entries["fecha_ingreso"].grid(row=current_row, column=1, padx=5, pady=2, sticky='w')
        current_row += 1

        tk.Button(self, text="Registrar Personal", font=FONT_NORMAL, bg=COLORS["primary"], fg="white",
                  command=self.guardar_registro).pack(pady=10)


        tree_frame = tk.Frame(self, bg=COLORS["bg_card"])
        tree_frame.pack(padx=20, pady=10, fill='both', expand=True)

        columns = ("ID", "Nombre", "Puesto", "Edad", "NSS", "Fecha Nac.", "Tipo Cont.",
                   "Sexo", "Grado Est.", "Cédula Prof.", "Domicilio", "Teléfono", "Email", "Fecha Ing.")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)

        for col in columns:
            self.tree.heading(col, text=col)
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

        scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar_y.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        scrollbar_x.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=scrollbar_x.set)

        self.actualizar_tabla_personal()

    def guardar_registro(self):
        id_ = self.entries["id"].get().strip()
        nombre = self.entries["nombre"].get().strip()
        puesto = self.comboboxes["puesto"].get()
        edad_str = self.entries["edad"].get().strip()
        nss = self.entries["nss"].get().strip()

        fecha_nacimiento = self.entries["fecha_nacimiento"].get().strip()
        tipo_contratacion = self.comboboxes["tipo_contratacion"].get()
        sexo = self.radio_vars["sexo"].get()
        ultimo_grado_estudio = self.comboboxes["grado_estudio"].get()
        cedula_profesional = self.entries["cedula_profesional"].get().strip()
        domicilio = self.entries["domicilio"].get().strip()
        telefono = self.entries["telefono"].get().strip()
        correo_electronico = self.entries["correo_electronico"].get().strip()
        fecha_ingreso = self.entries["fecha_ingreso"].get().strip()

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
            "turno_asignado_nombre": None,
            "horario_inicio": None,
            "horario_fin": None,
            "dias_laborales_turno": []
        }

        messagebox.showinfo("Registro Exitoso", f"Personal '{nombre}' con ID '{id_}' registrado correctamente.")

        for entry in self.entries.values():
            entry.delete(0, tk.END)
        for combo in self.comboboxes.values():
            if combo.winfo_exists():
                combo.set('')
        for var in self.radio_vars.values():
            var.set('')

        self.actualizar_tabla_personal()

    def actualizar_tabla_personal(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

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

        self.form_frame = tk.Frame(self, bg=COLORS["bg_card"], bd=2, relief="groove")
        self.form_frame.place(relx=0.5, rely=0.2, anchor="n", width=750, height=500)

        tk.Label(self.form_frame, text="ID del trabajador:", font=FONT_NORMAL, bg=COLORS["bg_card"]).place(relx=0.05, rely=0.05)
        self.id_entry = tk.Entry(self.form_frame, font=FONT_NORMAL)
        self.id_entry.place(relx=0.4, rely=0.05, relwidth=0.5)

        self.bloque1_var = tk.StringVar()
        self.bloque2_var = tk.StringVar()

        self.bloque1_frame = tk.LabelFrame(self.form_frame, text="Enero - Julio", font=FONT_NORMAL, bg=COLORS["bg_card"])
        self.bloque1_frame.place(relx=0.05, rely=0.2, relwidth=0.4, relheight=0.5)

        self.bloque2_frame = tk.LabelFrame(self.form_frame, text="Julio - Diciembre", font=FONT_NORMAL, bg=COLORS["bg_card"])
        self.bloque2_frame.place(relx=0.5, rely=0.2, relwidth=0.4, relheight=0.5)

        self.boton_asignar = tk.Button(self.form_frame, text="Asignar Vacaciones", font=FONT_NORMAL, bg=COLORS["primary"], fg="white",
                                       command=self.asignar)
        self.boton_asignar.place(relx=0.3, rely=0.8, relwidth=0.4)

        self.actualizar_vacaciones_disponibles()

    def actualizar_vacaciones_disponibles(self):
        for widget in self.bloque1_frame.winfo_children():
            widget.destroy()
        for widget in self.bloque2_frame.winfo_children():
            widget.destroy()

        self.periodos_bloque1 = []
        self.periodos_bloque2 = []

        for periodo in vacaciones_disponibles:
            if periodo in vacaciones_ocupadas:
                continue
            inicio = datetime.strptime(periodo.split(" - ")[0], "%d/%m/%Y")
            if inicio.month <= 6:
                self.periodos_bloque1.append(periodo)
            else:
                self.periodos_bloque2.append(periodo)

        for p in self.periodos_bloque1:
            tk.Radiobutton(self.bloque1_frame, text=p, variable=self.bloque1_var, value=p, anchor="w",
                           font=("Segoe UI", 9), bg=COLORS["bg_card"]).pack(anchor="w")
        for p in self.periodos_bloque2:
            tk.Radiobutton(self.bloque2_frame, text=p, variable=self.bloque2_var, value=p, anchor="w",
                           font=("Segoe UI", 9), bg=COLORS["bg_card"]).pack(anchor="w")

    def asignar(self):
        id_ = self.id_entry.get().strip()
        periodo1 = self.bloque1_var.get()
        periodo2 = self.bloque2_var.get()

        if not id_:
            messagebox.showerror("Error", "Por favor ingresa un ID válido")
            return
        if id_ not in registros_personal:
            messagebox.showerror("Error", "El ID no está registrado")
            return
        if not periodo1 or not periodo2:
            messagebox.showerror("Error", "Debes seleccionar un periodo en cada bloque")
            return
        if periodo1 in vacaciones_ocupadas or periodo2 in vacaciones_ocupadas:
            messagebox.showerror("Error", "Uno de los periodos seleccionados ya está ocupado")
            return

        registros_personal[id_]["vacaciones"] = f"{periodo1} / {periodo2}"
        vacaciones_ocupadas.update([periodo1, periodo2])

        messagebox.showinfo("Asignación Exitosa", f"Vacaciones asignadas a {registros_personal[id_]['nombre']}:{periodo1}{periodo2}")

        self.id_entry.delete(0, tk.END)
        self.bloque1_var.set("")
        self.bloque2_var.set("")
        self.actualizar_vacaciones_disponibles()

class TurnoFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])
        tk.Label(self, text="Asignación de Turno y Horario", font=FONT_TITLE,
                 bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(pady=20)

        form_frame = tk.Frame(self, bg=COLORS["bg_card"], bd=2, relief="groove")
        form_frame.place(relx=0.5, rely=0.2, anchor="n", width=700, height=450)

        tk.Label(form_frame, text="ID del trabajador:", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.id_entry = tk.Entry(form_frame, font=FONT_NORMAL)
        self.id_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(form_frame, text="Selecciona turno predefinido:", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.combo_turno_predefinido = ttk.Combobox(form_frame, font=FONT_NORMAL,
                                                    values=list(TURNOS.keys()), state="readonly")
        self.combo_turno_predefinido.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.combo_turno_predefinido.bind("<<ComboboxSelected>>", self.on_turno_predefinido_selected)

        tk.Label(form_frame, text="- O -", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=2, column=0, columnspan=2, pady=10)

        tk.Label(form_frame, text="Crear Turno Especial:", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=3, column=0, columnspan=2, pady=5)

        tk.Label(form_frame, text="Nombre del Turno Especial:", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=4, column=0, padx=10, pady=2, sticky="w")
        self.entry_nombre_turno_especial = tk.Entry(form_frame, font=FONT_NORMAL)
        self.entry_nombre_turno_especial.grid(row=4, column=1, padx=10, pady=2, sticky="ew")

        tk.Label(form_frame, text="Hora de Inicio (HH:MM):", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=5, column=0, padx=10, pady=2, sticky="w")
        self.entry_hora_inicio_especial = tk.Entry(form_frame, font=FONT_NORMAL)
        self.entry_hora_inicio_especial.grid(row=5, column=1, padx=10, pady=2, sticky="ew")

        tk.Label(form_frame, text="Hora de Fin (HH:MM):", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=6, column=0, padx=10, pady=2, sticky="w")
        self.entry_hora_fin_especial = tk.Entry(form_frame, font=FONT_NORMAL)
        self.entry_hora_fin_especial.grid(row=6, column=1, padx=10, pady=2, sticky="ew")

        tk.Label(form_frame, text="Días laborales (selecciona):", font=FONT_NORMAL, bg=COLORS["bg_card"]).grid(row=7, column=0, padx=10, pady=5, sticky="nw")

        self.dias_vars = {}
        dias_frame = tk.Frame(form_frame, bg=COLORS["bg_card"])
        dias_frame.grid(row=7, column=1, padx=10, pady=5, sticky="ew")
        for i, dia in enumerate(DIAS_SEMANA):
            self.dias_vars[dia] = tk.BooleanVar()
            chk = tk.Checkbutton(dias_frame, text=dia, variable=self.dias_vars[dia], bg=COLORS["bg_card"], font=FONT_NORMAL)
            chk.grid(row=i // 3, column=i % 3, sticky="w")

        tk.Button(form_frame, text="Crear y Asignar Turno Especial", font=FONT_NORMAL, bg=COLORS["accent"], fg="white",
                  command=self.crear_y_asignar_turno_especial).grid(row=8, column=0, columnspan=2, pady=10)

        tk.Button(form_frame, text="Asignar Turno Seleccionado", font=FONT_NORMAL, bg=COLORS["primary"], fg="white",
                  command=self.asignar_turno_predefinido).grid(row=9, column=0, columnspan=2, pady=10)

        form_frame.grid_columnconfigure(1, weight=1)

        # Nueva etiqueta para mostrar los días laborales asignados automáticamente
        self.label_dias_laborales = tk.Label(form_frame, text="Días laborales asignados: -", font=FONT_NORMAL, bg=COLORS["bg_card"], fg=COLORS["text_dark"])
        self.label_dias_laborales.grid(row=10, column=0, columnspan=2, pady=5)


    def actualizar_combobox_turnos(self):
        # turnos predefinidos y especiales 
        all_turn_names = list(TURNOS.keys()) + list(TURNOS_ESPECIALES.keys())
        self.combo_turno_predefinido['values'] = all_turn_names

    def on_turno_predefinido_selected(self, event=None):
        self.entry_nombre_turno_especial.delete(0, tk.END)
        self.entry_hora_inicio_especial.delete(0, tk.END)
        self.entry_hora_fin_especial.delete(0, tk.END)
        for var in self.dias_vars.values():
            var.set(False)

        nombre_turno = self.combo_turno_predefinido.get()
        turno_data = TURNOS.get(nombre_turno, TURNOS_ESPECIALES.get(nombre_turno))

        if turno_data:
            dias = turno_data.get("dias_laborales", [])
            self.label_dias_laborales.config(text=f"Días laborales asignados: {', '.join(dias)}")
        else:
            self.label_dias_laborales.config(text="Días laborales asignados: -")

        self.entry_nombre_turno_especial.delete(0, tk.END)
        self.entry_hora_inicio_especial.delete(0, tk.END)
        self.entry_hora_fin_especial.delete(0, tk.END)
        for var in self.dias_vars.values():
            var.set(False)

    def crear_y_asignar_turno_especial(self):
        id_ = self.id_entry.get().strip()
        nombre_turno = self.entry_nombre_turno_especial.get().strip()
        hora_inicio = self.entry_hora_inicio_especial.get().strip()
        hora_fin = self.entry_hora_fin_especial.get().strip()
        dias_seleccionados = [dia for dia, var in self.dias_vars.items() if var.get()]

        if not all([id_, nombre_turno, hora_inicio, hora_fin, dias_seleccionados]):
            messagebox.showerror("Error", "Por favor completa todos los campos del turno especial y selecciona al menos un día.")
            return

        if id_ not in registros_personal:
            messagebox.showerror("Error", "El ID no está registrado en el sistema.")
            return

        try:
            datetime.strptime(hora_inicio, "%H:%M")
            datetime.strptime(hora_fin, "%H:%M")
        except ValueError:
            messagebox.showerror("Error de Formato", "Las horas deben estar en formato HH:MM (ej: 07:00).")
            return

        if nombre_turno in TURNOS or nombre_turno in TURNOS_ESPECIALES:
            messagebox.showerror("Error", f"El nombre de turno '{nombre_turno}' ya existe. Elige otro.")
            return

        TURNOS_ESPECIALES[nombre_turno] = {
            "horario": (hora_inicio, hora_fin),
            "dias_laborales": dias_seleccionados
        }

        registros_personal[id_]["turno_asignado_nombre"] = nombre_turno
        registros_personal[id_]["horario_inicio"] = hora_inicio
        registros_personal[id_]["horario_fin"] = hora_fin
        registros_personal[id_]["dias_laborales_turno"] = dias_seleccionados

        messagebox.showinfo("Asignado", f"Turno especial '{nombre_turno}' asignado a {registros_personal[id_]['nombre']}.")
        self.label_dias_laborales.config(text=f"Días laborales asignados: {', '.join(dias_seleccionados)}")
        self.label_dias_laborales.config(text=f"Días laborales asignados: {', '.join(dias_laborales)}")
        self.limpiar_campos_turno()
        self.actualizar_combobox_turnos() # nuevo turno especial

    def asignar_turno_predefinido(self):
        id_ = self.id_entry.get().strip()
        nombre_turno_seleccionado = self.combo_turno_predefinido.get()

        if not id_:
            messagebox.showerror("Error", "Por favor ingresa un ID válido.")
            return

        if id_ not in registros_personal:
            messagebox.showerror("Error", "El ID no está registrado en el sistema.")
            return

        if not nombre_turno_seleccionado:
            messagebox.showerror("Error", "Selecciona un turno predefinido o crea uno especial.")
            return

        # Busca el turno en los turnos predefinidos primero, luego en los especiales
        turno_data = TURNOS.get(nombre_turno_seleccionado)
        if not turno_data:
            turno_data = TURNOS_ESPECIALES.get(nombre_turno_seleccionado)

        if not turno_data:
            messagebox.showerror("Error", "Turno seleccionado no encontrado. Por favor, selecciona uno válido.")
            return

        horario_inicio, horario_fin = turno_data["horario"]
        dias_laborales = turno_data["dias_laborales"]

        registros_personal[id_]["turno_asignado_nombre"] = nombre_turno_seleccionado
        registros_personal[id_]["horario_inicio"] = horario_inicio
        registros_personal[id_]["horario_fin"] = horario_fin
        registros_personal[id_]["dias_laborales_turno"] = dias_laborales

        messagebox.showinfo("Asignado", f"Turno '{nombre_turno_seleccionado}' asignado a {registros_personal[id_]['nombre']}.")
        self.label_dias_laborales.config(text=f"Días laborales asignados: {', '.join(dias_seleccionados)}")
        self.label_dias_laborales.config(text=f"Días laborales asignados: {', '.join(dias_laborales)}")
        self.limpiar_campos_turno()

    def limpiar_campos_turno(self):
        self.id_entry.delete(0, tk.END)
        self.combo_turno_predefinido.set("")
        self.entry_nombre_turno_especial.delete(0, tk.END)
        self.entry_hora_inicio_especial.delete(0, tk.END)
        self.entry_hora_fin_especial.delete(0, tk.END)
        for var in self.dias_vars.values():
            var.set(False)

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

        personal_data = registros_personal[id_]
        turno_nombre = personal_data.get("turno_asignado_nombre")
        horario_inicio_str = personal_data.get("horario_inicio")
        horario_fin_str = personal_data.get("horario_fin") 
        dias_laborales_turno = personal_data.get("dias_laborales_turno", [])

        if not turno_nombre or not horario_inicio_str or not horario_fin_str:
            messagebox.showerror("Error", "El trabajador no tiene turno y horario asignados.")
            return

        ahora = datetime.now()
        fecha_actual_str = ahora.strftime("%d/%m/%Y")
        dia_semana_actual = DIAS_SEMANA[ahora.weekday()]

        if id_ in asistencias_registradas and fecha_actual_str in asistencias_registradas[id_]:
            messagebox.showwarning("Advertencia", f"La asistencia para el ID {id_} ya ha sido registrada hoy.")
            return

        # Determinar la hora de inicio de turno para la comparación
        hora_inicio_dt_base = datetime.strptime(horario_inicio_str, "%H:%M")
        hora_inicio_turno = ahora.replace(hour=hora_inicio_dt_base.hour, minute=hora_inicio_dt_base.minute, second=0, microsecond=0)

        # Si la hora actual es "temprano" (antes de las 12 PM) y la hora de inicio es "tarde" (después de las 12 PM)
        # se asume que el turno empezó el día anterior.
        if "Nocturno" in turno_nombre and ahora.hour < 12 and hora_inicio_dt_base.hour >= 12:
            hora_inicio_turno = hora_inicio_turno - timedelta(days=1)

        if dia_semana_actual not in dias_laborales_turno:
            messagebox.showwarning("Advertencia", f"Hoy ({dia_semana_actual}) no es un día laboral programado para el turno de {personal_data['nombre']}. Aun así, se registrará la asistencia.")
        

        # Calcular el retardo
        diferencia_minutos = (ahora - hora_inicio_turno).total_seconds() / 60
        mensaje = ""
        retardo_tipo = None 

        if diferencia_minutos <= 0:
            mensaje = "Asistencia registrada. Estás a tiempo."
        elif 0 < diferencia_minutos <= TOLERANCIA_RETARDO_MENOR_MINUTOS:
            mensaje = "Asistencia registrada. Retardo menor detectado."
            retardo_tipo = "menor"
        elif diferencia_minutos > TOLERANCIA_RETARDO_MAYOR_MINUTOS:
            mensaje = "Asistencia registrada. Retardo mayor detectado."
            retardo_tipo = "mayor"

        asistencias_registradas.setdefault(id_, {})[fecha_actual_str] = ahora.strftime("%H:%M:%S")

        if retardo_tipo:
            self._registrar_retardo(id_, fecha_actual_str, retardo_tipo, ahora)
            self._evaluar_retardos_quincena(id_, ahora.date())

        messagebox.showinfo("Asistencia", f"{mensaje}\nHora: {ahora.strftime('%H:%M:%S')}")
        self.id_entry.delete(0, tk.END)

    def _registrar_retardo(self, id_trabajador, fecha_str, tipo_retardo, hora_registro_dt):
        retardos_registrados.setdefault(id_trabajador, {})
        retardos_registrados[id_trabajador][fecha_str] = {
            "tipo_ultimo": tipo_retardo,
            "hora_registro": hora_registro_dt.strftime("%H:%M:%S")
        }

    def _evaluar_retardos_quincena(self, id_trabajador, fecha_actual_date):


        retardos_menores_quincena = 0
        retardos_mayores_quincena = 0
     
        for i in range(16):
            fecha_a_evaluar = fecha_actual_date - timedelta(days=i)
            fecha_a_evaluar_str = fecha_a_evaluar.strftime("%d/%m/%Y")

            if id_trabajador in retardos_registrados and fecha_a_evaluar_str in retardos_registrados[id_trabajador]:
                retardo_info = retardos_registrados[id_trabajador][fecha_a_evaluar_str]
                if retardo_info["tipo_ultimo"] == "menor":
                    retardos_menores_quincena += 1
                elif retardo_info["tipo_ultimo"] == "mayor":
                    retardos_mayores_quincena += 1

        # Actualizar los contadores acumulados de la quincena
        retardos_acumulados_quincena.setdefault(id_trabajador, {})
        retardos_acumulados_quincena[id_trabajador]["menores"] = retardos_menores_quincena
        retardos_acumulados_quincena[id_trabajador]["mayores"] = retardos_mayores_quincena
        retardos_acumulados_quincena[id_trabajador]["ultima_fecha_evaluada"] = fecha_actual_date

        # Evaluar si se exceden los límites
        if retardos_menores_quincena > LIMITE_RETARDOS_MENORES or \
           retardos_mayores_quincena > LIMITE_RETARDOS_MAYORES:

            # Evitar aplicar la penalización múltiples veces en el mismo día si hay varios retardos
            fecha_penalizacion_str = fecha_actual_date.strftime("%d/%m/%Y")
            ya_penalizado_hoy = False
            if id_trabajador in penalizaciones_aplicadas:
                for p in penalizaciones_aplicadas[id_trabajador]:
                    if p["fecha"] == fecha_penalizacion_str:
                        ya_penalizado_hoy = True
                        break

            if not ya_penalizado_hoy:
                self._aplicar_penalizacion(id_trabajador, fecha_actual_date, retardos_menores_quincena, retardos_mayores_quincena)

    def _aplicar_penalizacion(self, id_trabajador, fecha_penalizacion_date, menores_total, mayores_total):
        nombre_trabajador = registros_personal[id_trabajador]["nombre"]
        fecha_penalizacion_str = fecha_penalizacion_date.strftime("%d/%m/%Y")
        razon = f"Exceso de retardos en quincena. (Menores: {menores_total}/{LIMITE_RETARDOS_MENORES}, Mayores: {mayores_total}/{LIMITE_RETARDOS_MAYORES})"

        penalizaciones_aplicadas.setdefault(id_trabajador, []).append({
            "fecha": fecha_penalizacion_str,
            "tipo": "Descuento Salarial (1 día)",
            "razon": razon
        })
        messagebox.showwarning("¡Penalización Aplicada!",
                               f"Se ha aplicado una penalización de 1 día de salario a {nombre_trabajador} (ID: {id_trabajador}).\n"
                               f"Razón: {razon}")

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

        personal_data = registros_personal[id_]
        turno_nombre = personal_data.get("turno_asignado_nombre")
        horario_fin_str = personal_data.get("horario_fin")

        if not turno_nombre or not horario_fin_str:
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

        elif turno_nombre.startswith("Nocturno") and ahora.hour < hora_fin_programada_dt.hour and hora_entrada_dt.day < ahora.day:
             hora_fin_programada_dt += timedelta(days=1)
       
        elif ahora > hora_fin_programada_dt and horario_fin_str < horario_inicio_str and not turno_nombre.startswith("Nocturno"): # type: ignore
            pass 


        tiempo_extra_minutos = 0
        if ahora > hora_fin_programada_dt:
            diferencia_tiempo = ahora - hora_fin_programada_dt
            tiempo_extra_minutos = int(diferencia_tiempo.total_seconds() / 60)

            messagebox.showinfo("Salida Registrada",
                                 f"Salida registrada para {personal_data['nombre']}.\n"
                                 f"Hora de Salida: {hora_salida_actual_str}\n"
                                 f"¡Tiempo extra trabajado: {tiempo_extra_minutos} minutos!")
        else:
            messagebox.showinfo("Salida Registrada",
                                 f"Salida registrada para {personal_data['nombre']}.\n"
                                 f"Hora de Salida: {hora_salida_actual_str}")

        salidas_registradas.setdefault(id_, {})[fecha_actual_str] = hora_salida_actual_str
        if tiempo_extra_minutos > 0:
            horas_extra_registradas.setdefault(id_, {})[fecha_actual_str] = tiempo_extra_minutos

        self.combo_id.set("")
        self.actualizar_ids_salida()

class PermisosFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])

        tk.Label(self, text="📝 Registro de Incapacidades y Licencias", font=FONT_TITLE,
                 bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(pady=25)

        tarjeta = tk.Frame(self, bg=COLORS["bg_card"], bd=3, relief="ridge")
        tarjeta.place(relx=0.5, rely=0.15, anchor="n", width=750, height=480)

        tk.Label(tarjeta, text="ID del trabajador:", font=FONT_NORMAL, bg=COLORS["bg_card"]).place(relx=0.05, rely=0.05)
        self.id_entry = tk.Entry(tarjeta, font=FONT_NORMAL)
        self.id_entry.place(relx=0.45, rely=0.05, relwidth=0.5)

        tk.Label(tarjeta, text="Tipo de permiso:", font=FONT_NORMAL, bg=COLORS["bg_card"]).place(relx=0.05, rely=0.15)
        self.tipo_combo = ttk.Combobox(tarjeta, font=FONT_NORMAL, state="readonly",
                                       values=["Incapacidad", "Licencia con sueldo", "Licencia sin sueldo"])
        self.tipo_combo.place(relx=0.45, rely=0.15, relwidth=0.5)
        self.tipo_combo.set("Selecciona tipo")
        self.tipo_combo.bind("<<ComboboxSelected>>", self.mostrar_campo_extra)

        tk.Label(tarjeta, text="Fecha de inicio (AAAA-MM-DD):", font=FONT_NORMAL,
                 bg=COLORS["bg_card"]).place(relx=0.05, rely=0.25)
        self.fecha_inicio = tk.Entry(tarjeta, font=FONT_NORMAL)
        self.fecha_inicio.place(relx=0.45, rely=0.25, relwidth=0.5)

        tk.Label(tarjeta, text="Fecha de fin (AAAA-MM-DD):", font=FONT_NORMAL,
                 bg=COLORS["bg_card"]).place(relx=0.05, rely=0.35)
        self.fecha_fin = tk.Entry(tarjeta, font=FONT_NORMAL)
        self.fecha_fin.place(relx=0.45, rely=0.35, relwidth=0.5)

        self.label_extra = tk.Label(tarjeta, text="", font=FONT_NORMAL, bg=COLORS["bg_card"])
        self.label_extra.place(relx=0.05, rely=0.45)
        self.entry_extra = tk.Entry(tarjeta, font=FONT_NORMAL)
        self.entry_extra.place(relx=0.45, rely=0.45, relwidth=0.5)

        self.mensaje = tk.Label(tarjeta, text="", font=("Segoe UI", 10, "italic"),
                                fg="gray", bg=COLORS["bg_card"])
        self.mensaje.place(relx=0.05, rely=0.60, relwidth=0.9)

        tk.Button(tarjeta, text="Registrar Permiso", font=FONT_NORMAL,
                  bg=COLORS["primary"], fg="white", command=self.registrar_permiso).place(relx=0.3, rely=0.75, relwidth=0.4)

    def mostrar_campo_extra(self, event=None):
        tipo = self.tipo_combo.get()
        if tipo == "Incapacidad":
            self.label_extra.config(text="Razón médica de la incapacidad:")
            self.entry_extra.place(relx=0.45, rely=0.45, relwidth=0.5)
        elif "Licencia" in tipo:
            self.label_extra.config(text="Motivo de la licencia:")
            self.entry_extra.place(relx=0.45, rely=0.45, relwidth=0.5)
        else:
            self.label_extra.config(text="")
            self.entry_extra.place_forget()

    def registrar_permiso(self):
        id_ = self.id_entry.get().strip()
        tipo = self.tipo_combo.get()
        inicio = self.fecha_inicio.get().strip()
        fin = self.fecha_fin.get().strip()
        razon = self.entry_extra.get().strip()

        if id_ not in registros_personal:
            messagebox.showerror("Error", "ID no registrado.")
            return
        if not all([tipo, inicio, fin]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return
        if tipo in ["Incapacidad", "Licencia con sueldo", "Licencia sin sueldo"] and not razon:
            messagebox.showerror("Error", "Por favor proporciona la razón o motivo del permiso.")
            return
        try:
            fecha_inicio = datetime.strptime(inicio, "%Y-%m-%d").date()
            fecha_fin = datetime.strptime(fin, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Usa AAAA-MM-DD.")
            return
        if fecha_fin < fecha_inicio:
            messagebox.showerror("Error", "La fecha de fin no puede ser antes que la de inicio.")
            return
        if (fecha_fin - fecha_inicio).days > 31:
            messagebox.showerror("Error", "La duración no puede ser mayor a un mes.")
            return

        registros_personal[id_].setdefault("permisos", []).append({
            "tipo": tipo,
            "inicio": inicio,
            "fin": fin,
            "razon": razon
        })

        self.mensaje.config(text=f"{tipo} registrada del {inicio} al {fin}.")
        messagebox.showinfo("Registrado", f"{tipo} registrada exitosamente para {registros_personal[id_]['nombre']}.")

        self.id_entry.delete(0, tk.END)
        self.tipo_combo.set("Selecciona tipo")
        self.fecha_inicio.delete(0, tk.END)
        self.fecha_fin.delete(0, tk.END)
        self.entry_extra.delete(0, tk.END)
        self.label_extra.config(text="")

class DiasConcedidosFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])

        tk.Label(self, text="📅 Consulta de Días Concedidos y Obligatorios",
                 font=FONT_TITLE, bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(pady=20)

        contenedor = tk.Frame(self, bg=COLORS["bg_main"])
        contenedor.pack(expand=True, fill="both", pady=10, padx=30)

        # Columna izquierda: Días concedidos
        concedidos = [
            "12 de diciembre - Día del Doctor",
            "Jueves Santo",
            "Viernes Santo",
            "Día del Trabajador del Hospital (3 de marzo)"
        ]

        obligatorios = [
            "1 de enero - Año Nuevo",
            "5 de febrero - Día de la Constitución",
            "21 de marzo - Natalicio de Benito Juárez",
            "1 de mayo - Día del Trabajo",
            "16 de septiembre - Independencia",
            "20 de noviembre - Revolución Mexicana",
            "25 de diciembre - Navidad"
        ]

        marco1 = tk.Frame(contenedor, bg=COLORS["bg_card"], bd=2, relief="ridge")
        marco1.pack(side="left", expand=True, fill="both", padx=10)
        tk.Label(marco1, text="🟡 Días Concedidos (No obligatorios)", bg=COLORS["bg_card"],
                 fg="orange", font=FONT_NORMAL).pack(pady=10)

        for dia in concedidos:
            tk.Label(marco1, text=f"• {dia}", font=FONT_NORMAL,
                     bg=COLORS["bg_card"], anchor="w", justify="left").pack(anchor="w", padx=20)

        marco2 = tk.Frame(contenedor, bg=COLORS["bg_card"], bd=2, relief="ridge")
        marco2.pack(side="left", expand=True, fill="both", padx=10)
        tk.Label(marco2, text="🔴 Días de Descanso Obligatorio", bg=COLORS["bg_card"],
                 fg="red", font=FONT_NORMAL).pack(pady=10)

        for dia in obligatorios:
            tk.Label(marco2, text=f"• {dia}", font=FONT_NORMAL,
                     bg=COLORS["bg_card"], anchor="w", justify="left").pack(anchor="w", padx=20)


class HistorialFrame(tk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent, bg=COLORS["bg_main"])

        tk.Label(self, text="Historial de Asistencias, Salidas y Horas Extra",
                 font=FONT_TITLE, bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(pady=(25, 15))

        control_frame = tk.Frame(self, bg=COLORS["bg_main"])
        control_frame.pack(pady=(0, 20))

        tk.Label(control_frame, text="Selecciona ID:", font=FONT_NORMAL,
                 bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(side="left")

        self.combo_id = ttk.Combobox(control_frame, font=FONT_NORMAL, state="readonly", width=18)
        self.combo_id.pack(side="left", padx=8)
        self.combo_id.bind("<<ComboboxSelected>>", lambda e: self.mostrar_historial())

        tk.Button(control_frame, text="Mostrar historial", font=FONT_NORMAL,
                  bg=COLORS["accent"], fg="white", activebackground=COLORS["primary"],
                  activeforeground="white", cursor="hand2", command=self.mostrar_historial).pack(side="left", padx=8)

        self.scroll_canvas = tk.Canvas(self, bg=COLORS["bg_main"])
        self.scroll_canvas.pack(fill="both", expand=True, padx=20, pady=10)

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.scroll_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.contenido_frame = tk.Frame(self.scroll_canvas, bg=COLORS["bg_main"])
        self.scroll_canvas.create_window((0, 0), window=self.contenido_frame, anchor="nw")

        self.contenido_frame.bind("<Configure>", lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all")))

        self.actualizar_ids()

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background=COLORS["bg_card"],
                        foreground=COLORS["text_dark"],
                        rowheight=26,
                        fieldbackground=COLORS["bg_card"],
                        font=FONT_NORMAL)
        style.configure("Custom.Treeview.Heading",
                        background=COLORS["primary"],
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))
        style.map("Custom.Treeview",
                  background=[('selected', COLORS["accent"])],
                  foreground=[('selected', 'white')])

    def actualizar_ids(self):
        ids = list(registros_personal.keys())
        self.combo_id['values'] = ids
        if ids:
            self.combo_id.current(0)
            self.mostrar_historial()
        else:
            self.combo_id.set('')
        for widget in self.contenido_frame.winfo_children():
            widget.destroy()

    def mostrar_historial(self):
        id_ = self.combo_id.get()
        if id_ not in registros_personal:
            messagebox.showerror("Error", "Selecciona un ID válido.")
            return

        for widget in self.contenido_frame.winfo_children():
            widget.destroy()

        personal = registros_personal[id_]

        datos_complementarios = tk.LabelFrame(self.contenido_frame, text="Detalles del Empleado", font=FONT_NORMAL,
                                              bg=COLORS["bg_card"], fg=COLORS["text_dark"], padx=15, pady=10)
        datos_complementarios.pack(fill="x", padx=10, pady=(0, 10))

        info = [
            ("ID", id_),
            ("Nombre", personal.get("nombre", "")),
            ("Puesto", personal.get("puesto", "")),
            ("Edad", personal.get("edad", "")),
            ("NSS", personal.get("nss", "")),
            ("Fecha de Nacimiento", personal.get("fecha_nacimiento", "")),
            ("Tipo de Contratación", personal.get("tipo_contratacion", "")),
            ("Sexo", personal.get("sexo", "")),
            ("Último Grado de Estudio", personal.get("ultimo_grado_estudio", "")),
            ("Cédula Profesional", personal.get("cedula_profesional", "")),
            ("Domicilio", personal.get("domicilio", "")),
            ("Teléfono", personal.get("telefono", "")),
            ("Correo Electrónico", personal.get("correo_electronico", "")),
            ("Fecha de Ingreso", personal.get("fecha_ingreso", "")),
            ("Vacaciones asignadas", personal.get("vacaciones", "")),
            ("Turno asignado", personal.get("turno_asignado_nombre", "")),
            ("Días laborales", personal.get("dias_laborales", "")),
        ]

        for i in range(0, len(info), 2):
            campo1, valor1 = info[i]
            campo2, valor2 = info[i+1] if i+1 < len(info) else ("", "")

            tk.Label(datos_complementarios, text=f"{campo1}:", font=("Segoe UI", 10, "bold"),
                     bg=COLORS["bg_card"], anchor="e", width=25, fg=COLORS["text_dark"]).grid(row=i, column=0, sticky="e", padx=5, pady=2)
            tk.Label(datos_complementarios, text=valor1, font=FONT_NORMAL,
                     bg=COLORS["bg_card"], anchor="w", fg=COLORS["text_dark"]).grid(row=i, column=1, sticky="w", padx=5, pady=2)

            if campo2:
                tk.Label(datos_complementarios, text=f"{campo2}:", font=("Segoe UI", 10, "bold"),
                         bg=COLORS["bg_card"], anchor="e", width=25, fg=COLORS["text_dark"]).grid(row=i, column=2, sticky="e", padx=5, pady=2)
                tk.Label(datos_complementarios, text=valor2, font=FONT_NORMAL,
                         bg=COLORS["bg_card"], anchor="w", fg=COLORS["text_dark"]).grid(row=i, column=3, sticky="w", padx=5, pady=2)

        retardos_frame = tk.LabelFrame(self.contenido_frame, text="Retardos y Evaluaciones", font=FONT_NORMAL,
                                       bg=COLORS["bg_card"], fg=COLORS["text_dark"], padx=15, pady=10)
        retardos_frame.pack(fill="x", padx=10, pady=(0, 10))

        menor = personal.get("retardos_menores", 0)
        mayor = personal.get("retardos_mayores", 0)
        eval_final = personal.get("ultima_evaluacion", "Sin registro")
        penalizaciones = personal.get("penalizaciones", [])

        tk.Label(retardos_frame, text=f"Menores: {menor}/3", font=FONT_NORMAL,
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w")
        tk.Label(retardos_frame, text=f"Mayores: {mayor}/2", font=FONT_NORMAL,
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w")
        tk.Label(retardos_frame, text=f"Última evaluación de quincena: {eval_final}", font=FONT_NORMAL,
                 bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w", pady=(5, 0))

        penal_frame = tk.LabelFrame(self.contenido_frame, text="Penalizaciones", font=FONT_NORMAL,
                                    bg=COLORS["bg_card"], fg=COLORS["text_dark"], padx=15, pady=10)
        penal_frame.pack(fill="x", padx=10, pady=(0, 15))

        if penalizaciones:
            for p in penalizaciones:
                tk.Label(penal_frame, text=f"- {p}", font=FONT_NORMAL,
                         bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w")
        else:
            tk.Label(penal_frame, text="No hay penalizaciones registradas.", font=FONT_NORMAL,
                     bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w")

        self.crear_tabla_historial(id_)

    def crear_tabla_historial(self, id_):
        tabla_frame = tk.LabelFrame(self.contenido_frame, text="Historial Diario", font=FONT_NORMAL,
                                    bg=COLORS["bg_card"], fg=COLORS["text_dark"], padx=10, pady=10)
        tabla_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columnas = ("Fecha", "Entrada", "Salida", "Retardo", "Horas Extra")
        self.tabla = ttk.Treeview(tabla_frame, columns=columnas, show="headings",
                                  height=15, style="Custom.Treeview")

        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center", width=130)

        scrollbar_y = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        scrollbar_y.pack(side="right", fill="y")
        self.tabla.configure(yscrollcommand=scrollbar_y.set)
        self.tabla.pack(fill="both", expand=True)

        fechas = set()
        fechas.update(asistencias_registradas.get(id_, {}).keys())
        fechas.update(salidas_registradas.get(id_, {}).keys())
        fechas.update(horas_extra_registradas.get(id_, {}).keys())
        fechas.update(retardos_registrados.get(id_, {}).keys())

        fechas_ordenadas = sorted(fechas, key=lambda f: datetime.strptime(f, "%d/%m/%Y"), reverse=True)

        for i, fecha in enumerate(fechas_ordenadas):
            entrada = asistencias_registradas.get(id_, {}).get(fecha, "—")
            salida = salidas_registradas.get(id_, {}).get(fecha, "—")
            extra = horas_extra_registradas.get(id_, {}).get(fecha, 0)
            retardo = "No"
            if fecha in retardos_registrados.get(id_, {}):
                r = retardos_registrados[id_][fecha]
                retardo = f"{r['tipo_ultimo']} ({r['hora_registro']})"
            self.tabla.insert("", "end",
                              values=(fecha, entrada, salida, retardo, f"{extra} min" if extra else "—"),
                              tags=("evenrow" if i % 2 == 0 else "oddrow",))

        self.tabla.tag_configure("evenrow", background="#f0f0f0")
        self.tabla.tag_configure("oddrow", background="#e0e0e0")

        trabajador = registros_personal.get(id_, {})
        permisos = trabajador.get("permisos", [])
        if permisos:
            permisos_frame = tk.LabelFrame(self.contenido_frame, text="📝 Permisos Registrados",
                                           font=FONT_NORMAL, bg=COLORS["bg_card"], fg=COLORS["text_dark"],
                                           padx=15, pady=10)
            permisos_frame.pack(fill="x", padx=10, pady=(10, 0))
            for p in permisos:
                texto_permiso = f"- {p['tipo']} del {p['inicio']} al {p['fin']} (Razón: {p['razon']})"
                tk.Label(permisos_frame, text=texto_permiso, font=FONT_NORMAL,
                         bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w")

        tercero = trabajador.get("tercer_periodo", [])
        if tercero:
            extra_frame = tk.LabelFrame(self.contenido_frame, text="🌟 Periodo Extraordinario (Terceras Vacaciones)",
                                        font=FONT_NORMAL, bg=COLORS["bg_card"], fg=COLORS["text_dark"],
                                        padx=15, pady=10)
            extra_frame.pack(fill="x", padx=10, pady=(10, 15))
            for t in tercero:
                texto_extra = f"- Nivel: {t['riesgo']} → {t['dias_concedidos']} concedidos"
                tk.Label(extra_frame, text=texto_extra, font=FONT_NORMAL,
                         bg=COLORS["bg_card"], fg=COLORS["text_dark"]).pack(anchor="w")
        
class PeriodoExtraFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS["bg_main"])
        tk.Label(self, text="🎯 Periodo Extraordinario (Terceras Vacaciones)", font=FONT_TITLE,
                 bg=COLORS["bg_main"], fg=COLORS["text_dark"]).pack(pady=20)

        card = tk.Frame(self, bg=COLORS["bg_card"], bd=3, relief="ridge")
        card.place(relx=0.5, rely=0.2, anchor="n", width=650, height=350)

        tk.Label(card, text="ID del trabajador:", font=FONT_NORMAL, bg=COLORS["bg_card"]).place(relx=0.05, rely=0.1)
        self.id_entry = tk.Entry(card, font=FONT_NORMAL)
        self.id_entry.place(relx=0.5, rely=0.1, relwidth=0.4)

        tk.Label(card, text="Nivel de Riesgo:", font=FONT_NORMAL, bg=COLORS["bg_card"]).place(relx=0.05, rely=0.3)
        self.riesgo_combo = ttk.Combobox(card, font=FONT_NORMAL, state="readonly",
                                         values=["Alto Riesgo", "Mediano Riesgo", "Bajo Riesgo"])
        self.riesgo_combo.place(relx=0.5, rely=0.3, relwidth=0.4)
        self.riesgo_combo.bind("<<ComboboxSelected>>", self.actualizar_dias)

        tk.Label(card, text="Días concedidos:", font=FONT_NORMAL, bg=COLORS["bg_card"]).place(relx=0.05, rely=0.5)
        self.dias_var = tk.StringVar()
        self.dias_label = tk.Label(card, textvariable=self.dias_var, font=FONT_NORMAL,
                                   bg=COLORS["bg_card"], fg=COLORS["accent"])
        self.dias_label.place(relx=0.5, rely=0.5)

        tk.Button(card, text="Asignar Tercer Periodo", font=FONT_NORMAL,
                  bg=COLORS["primary"], fg="white", command=self.registrar_tercer_periodo)\
            .place(relx=0.3, rely=0.75, relwidth=0.4)

    def actualizar_dias(self, event=None):
        nivel = self.riesgo_combo.get()
        if nivel == "Alto Riesgo":
            self.dias_var.set("15 días")
        elif nivel == "Mediano Riesgo":
            self.dias_var.set("8 días")
        elif nivel == "Bajo Riesgo":
            self.dias_var.set("3 días")
        else:
            self.dias_var.set("")

    def registrar_tercer_periodo(self):
        id_ = self.id_entry.get().strip()
        riesgo = self.riesgo_combo.get()
        dias_texto = self.dias_var.get()

        if id_ not in registros_personal:
            messagebox.showerror("Error", "ID no registrado.")
            return
        if not riesgo or not dias_texto:
            messagebox.showerror("Error", "Selecciona el nivel de riesgo.")
            return

        registros_personal[id_].setdefault("tercer_periodo", []).append({
            "riesgo": riesgo,
            "dias_concedidos": dias_texto
        })

        messagebox.showinfo("Registrado", f"{dias_texto} de vacaciones extraordinarias asignados a {registros_personal[id_]['nombre']}.")
        self.id_entry.delete(0, tk.END)
        self.riesgo_combo.set("")
        self.dias_var.set("")

if __name__ == "__main__":
    app = HospitalApp()
    app.mainloop()
