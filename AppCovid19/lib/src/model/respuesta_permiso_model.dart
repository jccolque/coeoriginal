///
/// Model Respuesta de permiso
/// @author JLopez
///
class RespuestaPermisoModel {
  bool realizado;
  DateTime fechaFin;
  String texto;
  String horaFin;
  String imagen;
  String tipoPermiso;
  String qr;
  String action;
  DateTime fechaInicio;
  String horaInicio;

  RespuestaPermisoModel({
    this.realizado,
    this.fechaFin,
    this.texto,
    this.horaFin,
    this.imagen,
    this.tipoPermiso,
    this.qr,
    this.action,
    this.fechaInicio,
    this.horaInicio,
  });

  factory RespuestaPermisoModel.fromJson(Map<String, dynamic> json) => RespuestaPermisoModel(
    realizado: json["realizado"],
    fechaFin: DateTime.parse(json["fecha_fin"]),
    texto: json["texto"],
    horaFin: json["hora_fin"],
    imagen: json["imagen"],
    tipoPermiso: json["tipo_permiso"],
    qr: json["qr"],
    action: json["action"],
    fechaInicio: DateTime.parse(json["fecha_inicio"]),
    horaInicio: json["hora_inicio"],
  );

  Map<String, dynamic> toJson() => {
    "realizado": realizado,
    "fecha_fin": "${fechaFin.year.toString().padLeft(4, '0')}-${fechaFin.month.toString().padLeft(2, '0')}-${fechaFin.day.toString().padLeft(2, '0')}",
    "texto": texto,
    "hora_fin": horaFin,
    "imagen": imagen,
    "tipo_permiso": tipoPermiso,
    "qr": qr,
    "action": action,
    "fecha_inicio": "${fechaInicio.year.toString().padLeft(4, '0')}-${fechaInicio.month.toString().padLeft(2, '0')}-${fechaInicio.day.toString().padLeft(2, '0')}",
    "hora_inicio": horaInicio,
  };
}
