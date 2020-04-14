///
/// Model Respuesta de permiso
/// @author JLopez
///
class RespuestaPermisoModel {
  String action;
  String domicilio;
  String nombreCompleto;
  String dniIndividuo;
  String horaFin;
  String texto;
  String imagen;
  String tipoPermiso;
  DateTime fechaInicio;
  DateTime fechaFin;
  bool control;
  bool realizado;
  String horaInicio;
  String qr;

  RespuestaPermisoModel({
    this.action,
    this.domicilio,
    this.nombreCompleto,
    this.dniIndividuo,
    this.horaFin,
    this.texto,
    this.imagen,
    this.tipoPermiso,
    this.fechaInicio,
    this.fechaFin,
    this.control,
    this.realizado,
    this.horaInicio,
    this.qr,
  });

  factory RespuestaPermisoModel.fromJson(Map<String, dynamic> json) => RespuestaPermisoModel(
    action: json["action"],
    domicilio: json["domicilio"],
    nombreCompleto: json["nombre_completo"],
    dniIndividuo: json["dni_individuo"],
    horaFin: json["hora_fin"],
    texto: json["texto"],
    imagen: json["imagen"],
    tipoPermiso: json["tipo_permiso"],
    fechaInicio: DateTime.parse(json["fecha_inicio"]),
    fechaFin: DateTime.parse(json["fecha_fin"]),
    control: json["control"],
    realizado: json["realizado"],
    horaInicio: json["hora_inicio"],
    qr: json["qr"],
  );

  Map<String, dynamic> toJson() => {
    "action": action,
    "domicilio": domicilio,
    "nombre_completo": nombreCompleto,
    "dni_individuo": dniIndividuo,
    "hora_fin": horaFin,
    "texto": texto,
    "imagen": imagen,
    "tipo_permiso": tipoPermiso,
    "fecha_inicio": "${fechaInicio.year.toString().padLeft(4, '0')}-${fechaInicio.month.toString().padLeft(2, '0')}-${fechaInicio.day.toString().padLeft(2, '0')}",
    "fecha_fin": "${fechaFin.year.toString().padLeft(4, '0')}-${fechaFin.month.toString().padLeft(2, '0')}-${fechaFin.day.toString().padLeft(2, '0')}",
    "control": control,
    "realizado": realizado,
    "hora_inicio": horaInicio,
    "qr": qr,
  };
}
