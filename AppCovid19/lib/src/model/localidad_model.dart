///
/// Model Localidad
/// @author JLopez
///
class LocalidadModel {
  Pagination pagination;
  List<Result> results;

  LocalidadModel({
    this.pagination,
    this.results,
  });

  factory LocalidadModel.fromJson(Map<String, dynamic> json) {
    var list = json['results'] as List;
    print(list.runtimeType);
    List<Result> imagesList = list.map((i) => Result.fromJson(i)).toList();

    return LocalidadModel(
      pagination: Pagination.fromJson(json["pagination"]),
      results: imagesList,
    );
  }

  Map<String, dynamic> toJson() => {
    "pagination": pagination.toJson(),
    "results": List<dynamic>.from(results.map((x) => x.toJson())),
  };
}

class Pagination {
  bool more;

  Pagination({
    this.more,
  });

  factory Pagination.fromJson(Map<String, dynamic> json) => Pagination(
    more: json["more"],
  );

  Map<String, dynamic> toJson() => {
    "more": more,
  };
}

class Result {
  String id;
  String text;
  String selectedText;

  Result({
    this.id,
    this.text,
    this.selectedText,
  });

  factory Result.fromJson(Map<String, dynamic> json) => Result(
    id: json["id"],
    text: json["text"],
    selectedText: json["selected_text"],
  );

  Map<String, dynamic> toJson() => {
    "id": id,
    "text": text,
    "selected_text": selectedText,
  };
}
