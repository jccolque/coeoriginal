import 'dart:convert';

import 'package:covidjujuy_app/src/model/localidad_model.dart';
import 'package:flutter/services.dart';

class ViewLocalidadModel {
  static List<LocalidadModel> localidades;

  static Future loadPlayers() async {
    try {
      localidades = new List<LocalidadModel>();
      String jsonString = await rootBundle.loadString('assets/players.json');
      Map parsedJson = json.decode(jsonString);
      var categoryJson = parsedJson['players'] as List;
      for (int i = 0; i < categoryJson.length; i++) {
        localidades.add(new LocalidadModel.fromJson(categoryJson[i]));
      }
    } catch (e) {
      print(e);
    }
  }
}