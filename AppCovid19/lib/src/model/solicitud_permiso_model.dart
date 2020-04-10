class SolicitudPermisoModel {
  String token;
  String fechaIdeal;
  String dni_individuo;
  String horaIdeal;
  String tipoPermiso;

  SolicitudPermisoModel({
    this.token,
    this.fechaIdeal,
    this.dni_individuo,
    this.horaIdeal,
    this.tipoPermiso,
  });

  factory SolicitudPermisoModel.fromJson(Map<String, dynamic> json) => SolicitudPermisoModel(
    token: json["token"],
    fechaIdeal: json["fecha_ideal"],
    dni_individuo: json["dni_individuo"],
    horaIdeal: json["hora_ideal"],
    tipoPermiso: json["tipo_permiso"],
  );

  Map<String, dynamic> toJson() => {
    "token": token,
    "fecha_ideal": fechaIdeal,
    "dni_individuo": dni_individuo,
    "hora_ideal": horaIdeal,
    "tipo_permiso": tipoPermiso,
  };
}
