class SolicitudPermisoModel {
  String token;
  String fechaIdeal;
  String dniIndividuo;
  String horaIdeal;
  String tipoPermiso;

  SolicitudPermisoModel({
    this.token,
    this.fechaIdeal,
    this.dniIndividuo,
    this.horaIdeal,
    this.tipoPermiso,
  });

  factory SolicitudPermisoModel.fromJson(Map<String, dynamic> json) => SolicitudPermisoModel(
    token: json["token"],
    fechaIdeal: json["fecha_ideal"],
    dniIndividuo: json["dni_individuo"],
    horaIdeal: json["hora_ideal"],
    tipoPermiso: json["tipo_permiso"],
  );

  Map<String, dynamic> toJson() => {
    "token": token,
    "fecha_ideal": fechaIdeal,
    "dni_individuo": dniIndividuo,
    "hora_ideal": horaIdeal,
    "tipo_permiso": tipoPermiso,
  };
}
