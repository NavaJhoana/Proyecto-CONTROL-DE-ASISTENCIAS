# Proyecto-CONTROL-DE-ASISTENCIAS

1. Aspectos Teóricos 

ID de empleado

Nombre completo

Fecha de ingreso

Cargo o área de trabajo (opcional)


2. Registro diario de asistencia
Cada día laboral debe registrarse con un estado. Por ejemplo:

Presente

Ausente

Retardo (opcional)

Vacaciones

Día libre o no laborable (opcional)


3. Gestión de vacaciones

a) Derecho a vacaciones

¿Cuántos días de vacaciones tiene derecho cada trabajador?

Ejemplo: 15 días por año trabajado

¿Cuándo comienzan a contar?


4. Control de fechas
Es importante tener en cuenta:

El calendario laboral (fines de semana, feriados)

Evitar que se registren vacaciones en días no laborables si no corresponde

Validar que las fechas ingresadas tengan sentido (inicio antes que fin)

















Planteamiento del Problema

En muchos hospitales, el control de asistencias, turnos y vacaciones del personal se realiza de forma manual o mediante sistemas poco integrados, lo cual genera errores, pérdida de información y retrasos en la gestión de recursos humanos. Esto afecta directamente la eficiencia operativa y la planificación del personal médico y administrativo.

El presente sistema automatiza el registro de datos del personal, la asignación de turnos y vacaciones, y el control de asistencias, permitiendo un acceso rápido, organizado y preciso a la información. Esta solución mejora la administración interna del hospital, optimiza los recursos y reduce significativamente el margen de error humano.

Entrada de datos

Nombre completo del empleado

- ID único del trabajador

- Edad y número de seguridad social

- Puesto que ocupa en el hospital

- Turno (matutino, vespertino o madrugada)

- Selección de periodo vacacional

- Registro de asistencia diaria

Procesamiento
- Validación de datos ingresados

- Almacenamiento organizado en listas y archivos

- Asignación de turnos y vacaciones sin solapamientos

- Control de asistencia con historial por ID

- Cálculo de jornadas trabajadas, ausencias y días libres

Salida de datos
- Confirmación de registro exitoso

- Historial detallado por empleado

- Lista de turnos y vacaciones asignadas

- Reporte visual de asistencias registradas



+---------------------+
|     HospitalApp     |
+---------------------+
| - frames: dict      |
| - clock_label: Label|
| - main_frame: Frame |
+---------------------+
| + show_frame(name: str)       |
| + update_clock()              |
+---------------------+


+----------------------+
|     InicioFrame      |
+----------------------+
| (hereda de Frame)    |
+----------------------+
| + __init__(parent, controller) |
+----------------------+


+----------------------+
|    RegistroFrame     |
+----------------------+
| - entries: dict      |
| - puesto_combo: Combobox |
+----------------------+
| + guardar_registro() |
+----------------------+


+--------------------------+
|    VacacionesFrame       |
+--------------------------+
| - id_entry: Entry        |
| - combo_vacaciones: Combobox |
+--------------------------+
| + asignar()              |
| + obtener_periodos_disponibles() |
+--------------------------+


+----------------------+
|      TurnoFrame      |
+----------------------+
| - id_entry: Entry     |
| - combo_turno: Combobox |
+----------------------+
| + asignar()          |
+----------------------+


+-----------------------------+
|      AsistenciaFrame        |
+-----------------------------+
| - id_entry: Entry           |
+-----------------------------+
| + registrar_asistencia()    |
+-----------------------------+


+-----------------------------+
|      HistorialFrame         |
+-----------------------------+
| - combo_id: Combobox        |
| - text_historial: Text      |
+-----------------------------+
| + actualizar_ids()          |
| + mostrar_historial()       |
+-----------------------------+

