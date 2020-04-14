///
/// Model a ser usado en servicio de envio de imagen de perfil
/// @author JLopez
///
class ImagenPerfilModel {
  int dni;
  String imagen;

  ImagenPerfilModel({
    this.dni,
    this.imagen,
  });

  factory ImagenPerfilModel.fromJson(Map<String, dynamic> json) => ImagenPerfilModel(
    dni: json["dni"],
    imagen: json["imagen"],
  );

  Map<String, dynamic> toJson() => {
    "dni": dni,
    "imagen": imagen,
  };
}
