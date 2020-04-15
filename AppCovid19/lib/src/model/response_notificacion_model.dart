class ResponseNotificacionModel {
  String error;
  String realizado;
  String notifMensaje;
  String notifTitulo;
  String accion;

  ResponseNotificacionModel({
    this.error,
    this.realizado,
    this.notifMensaje,
    this.notifTitulo,
    this.accion,
  });

  factory ResponseNotificacionModel.fromJson(Map<String, dynamic> json) => ResponseNotificacionModel(
    error: json["error"],
    realizado: json["realizado"],
    notifMensaje: json["notif_mensaje"],
    notifTitulo: json["notif_titulo"],
    accion: json["accion"],
  );

  Map<String, dynamic> toJson() => {
    "error": error,
    "realizado": realizado,
    "notif_mensaje": notifMensaje,
    "notif_titulo": notifTitulo,
    "accion": accion,
  };
}