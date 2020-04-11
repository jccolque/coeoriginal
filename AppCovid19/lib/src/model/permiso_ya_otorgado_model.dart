class PermisoYaOtorgadoModel {
  String token;
  String dniIndividuo;

  PermisoYaOtorgadoModel({
    this.token,
    this.dniIndividuo,
  });

  factory PermisoYaOtorgadoModel.fromJson(Map<String, dynamic> json) => PermisoYaOtorgadoModel(
    token: json["token"],
    dniIndividuo: json["dni_individuo"],
  );

  Map<String, dynamic> toJson() => {
    "token": token,
    "dni_individuo": dniIndividuo,
  };
}
