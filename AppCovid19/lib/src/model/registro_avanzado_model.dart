///
/// Modelo para el envío de petición  de permiso de circulación
/// @author JLopez
///
class RegistroAvanzadoModel {
  int dni;
  String localidad;
  String calle;
  int numero;
  String aclaraciones;
  String fechaRegistro;
  bool separadoAislamiento;
  String imagen;

  RegistroAvanzadoModel({
    this.dni,
    this.localidad,
    this.calle,
    this.numero,
    this.aclaraciones,
    this.fechaRegistro,
    this.separadoAislamiento,
    this.imagen
  });

  factory RegistroAvanzadoModel.fromJson(Map<String, dynamic> json) => RegistroAvanzadoModel(
    dni: json["dni"],
    localidad: json["localidad"],
    calle: json["calle"],
    numero: json["numero"],
    aclaraciones: json["aclaraciones"],
    fechaRegistro: json["fechaRegistro"],
    separadoAislamiento: json["separadoAislamiento"],
    imagen: json["imagen"],
  );

  Map<String, dynamic> toJson() => {
    "dni": dni,
    "localidad": localidad,
    "calle": calle,
    "numero": numero,
    "imagen": imagen,
    "aclaraciones": aclaraciones,
    "fechaRegistro": fechaRegistro,
    "separadoAislamiento": separadoAislamiento

  };
}
