class ErrorControlPermisoModel {
  bool realizado;
  String error;
  String accion;

  ErrorControlPermisoModel({
    this.realizado,
    this.error,
    this.accion,
  });

  factory ErrorControlPermisoModel.fromJson(Map<String, dynamic> json) => ErrorControlPermisoModel(
    realizado: json["realizado"],
    error: json["error"],
    accion: json["accion"],
  );

  Map<String, dynamic> toJson() => {
    "realizado": realizado,
    "error": error,
    "accion": accion,
  };
}
