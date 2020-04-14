///
/// Model Permiso Error
/// @author JLopez
///
class PermisoErrorModel {
  String action;
  String error;
  bool realizado;

  PermisoErrorModel({
    this.action,
    this.error,
    this.realizado,
  });

  factory PermisoErrorModel.fromJson(Map<String, dynamic> json) => PermisoErrorModel(
    action: json["action"],
    error: json["error"],
    realizado: json["realizado"],
  );

  Map<String, dynamic> toJson() => {
    "action": action,
    "error": error,
    "realizado": realizado,
  };
}
