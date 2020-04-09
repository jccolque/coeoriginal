import 'package:covidjujuy_app/src/bloc/form_bloc.dart';
import 'package:flutter/material.dart';
export 'package:covidjujuy_app/src/bloc/form_bloc.dart';

///
/// Provider encargado de escuchar el form bloc
/// @authos JLopez
///
class Provider extends InheritedWidget {

  static Provider _instancia;

  factory Provider({Key key, Widget child}) {
    if(_instancia == null) {
      _instancia = new Provider._internal(key: key, child: child);
    }
    return _instancia;
  }

  Provider._internal({Key key, Widget child})
      : super(key: key, child: child);

  final formBloc = FormBloc();

  @override
  bool updateShouldNotify(InheritedWidget oldWidget) => true ;

  static FormBloc of ( BuildContext context )  {
    return ( context.inheritFromWidgetOfExactType(Provider) as Provider ).formBloc;
  }

}