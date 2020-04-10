class RespuestaPermisoModel {
  bool realizado;
  String horaInicio;
  String imagen;
  String action;
  String qr;
  DateTime fecha;
  String texto;
  String horaFin;

  RespuestaPermisoModel({
    this.realizado,
    this.horaInicio,
    this.imagen,
    this.action,
    this.qr,
    this.fecha,
    this.texto,
    this.horaFin,
  });

  factory RespuestaPermisoModel.fromJson(Map<String, dynamic> json) => RespuestaPermisoModel(
    realizado: json["realizado"],
    horaInicio: json["hora_inicio"],
    imagen: json["imagen"],
    action: json["action"],
    qr: json["qr"],
    fecha: DateTime.parse(json["fecha"]),
    texto: json["texto"],
    horaFin: json["hora_fin"],
  );

  Map<String, dynamic> toJson() => {
    "realizado": realizado,
    "hora_inicio": horaInicio,
    "imagen": imagen,
    "action": action,
    "qr": qr,
    "fecha": "${fecha.year.toString().padLeft(4, '0')}-${fecha.month.toString().padLeft(2, '0')}-${fecha.day.toString().padLeft(2, '0')}",
    "texto": texto,
    "hora_fin": horaFin,
  };
}
