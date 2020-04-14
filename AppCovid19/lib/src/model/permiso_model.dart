///
/// Model Permiso
/// @author JLopez
///
class PermisoModel {
  List<Permiso> permisos;

  PermisoModel({
    this.permisos,
  });

  factory PermisoModel.fromJson(Map<String, dynamic> json) => PermisoModel(
    permisos: List<Permiso>.from(json["permisos"].map((x) => Permiso.fromJson(x))),
  );

  Map<String, dynamic> toJson() => {
    "permisos": List<dynamic>.from(permisos.map((x) => x.toJson())),
  };
}

class Permiso {
  String id;
  String descripcion;

  Permiso({
    this.id,
    this.descripcion,
  });

  factory Permiso.fromJson(Map<String, dynamic> json) => Permiso(
    id: json["id"],
    descripcion: json["descripcion"],
  );

  Map<String, dynamic> toJson() => {
    "id": id,
    "descripcion": descripcion,
  };
}
