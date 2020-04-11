///
/// Model Respuesta de permiso
/// @author JLopez
///
class RespuestaPermisoModel {
  String fechaInicio;
  String horaFin;
  String qr;
  String fechaFin;
  String error;
  String imagen;
  String horaInicio;
  String texto;
  bool realizado;
  String action;

  RespuestaPermisoModel({
    this.fechaInicio,
    this.horaFin,
    this.qr,
    this.fechaFin,
    this.error,
    this.imagen,
    this.horaInicio,
    this.texto,
    this.realizado,
    this.action,
  });

  factory RespuestaPermisoModel.fromJson(Map<String, dynamic> json) => RespuestaPermisoModel(
    fechaInicio: json["fecha_inicio"],
    horaFin: json["hora_fin"],
    qr: json["qr"],
    fechaFin: json["fecha_fin"],
    error: json["error"],
    imagen: json["imagen"],
    horaInicio: json["hora_inicio"],
    texto: json["texto"],
    realizado: json["realizado"],
    action: json["action"],
  );

  Map<String, dynamic> toJson() => {
    "fecha_inicio": fechaInicio,
    "hora_fin": horaFin,
    "qr": qr,
    "fecha_fin": fechaFin,
    "error": error,
    "imagen": imagen,
    "hora_inicio": horaInicio,
    "texto": texto,
    "realizado": realizado,
    "action": action,
  };
}
