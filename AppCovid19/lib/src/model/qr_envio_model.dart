class QrEnvioModel {
  double latitud;
  String qrCode;
  double longitud;
  String dniOperador;

  QrEnvioModel({
    this.latitud,
    this.qrCode,
    this.longitud,
    this.dniOperador,
  });

  factory QrEnvioModel.fromJson(Map<String, dynamic> json) => QrEnvioModel(
    latitud: json["latitud"].toDouble(),
    qrCode: json["qr_code"],
    longitud: json["longitud"].toDouble(),
    dniOperador: json["dni_operador"],
  );

  Map<String, dynamic> toJson() => {
    "latitud": latitud,
    "qr_code": qrCode,
    "longitud": longitud,
    "dni_operador": dniOperador,
  };
}
