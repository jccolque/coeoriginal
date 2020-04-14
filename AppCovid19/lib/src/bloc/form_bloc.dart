import 'dart:async';

import 'package:covidjujuy_app/src/bloc/validators.dart';
import 'package:rxdart/rxdart.dart';


class FormBloc with Validators{

  final _localidadController    = BehaviorSubject<String>();
  final _calleController    = BehaviorSubject<String>();
  final _numeroController    = BehaviorSubject<String>();
  final _aclaracionesController    = BehaviorSubject<String>();
  final _fechaRegistroController    = BehaviorSubject<String>();
  final _separadoAisladoController    = BehaviorSubject<bool>();

  final _emailController    = BehaviorSubject<String>();
  final _passwordController = BehaviorSubject<String>();


  //Recuperar datos de Stream
  Stream<String> get localidadStream => _localidadController.stream.transform(validarLocalidad);
  Stream<String> get calleStream => _calleController.stream.transform(validarLocalidad);
  Stream<String> get numeroStream => _numeroController.stream.transform(validarLocalidad);
  Stream<String> get aclaracionesStream => _aclaracionesController.stream.transform(validarLocalidad);
  Stream<String> get fechaRegistroStream => _fechaRegistroController.stream.transform(validarLocalidad);
  Stream<bool> get separadoAisladoStream => _separadoAisladoController.stream.transform(validarSeparadoAislado);


  Stream<String> get emailStream => _emailController.stream.transform(validarEmail);
  Stream<String> get paswordStream => _passwordController.stream.transform( validarPassword );

  Stream<bool> get formValidStream =>
      Rx.combineLatest2(emailStream, paswordStream, (e, p) => true);

  Stream<bool> get formSalvoConductoStream =>
      Rx.combineLatest6(localidadStream, calleStream, numeroStream, aclaracionesStream, fechaRegistroStream, separadoAisladoStream,
              (l, c, n, a, f, s) => true);
  //
  Function(String) get changeLocalidad => _localidadController.sink.add;
  Function(String) get changeCalle => _calleController.sink.add;
  Function(String) get changeNumero => _numeroController.sink.add;
  Function(String) get changeAclaraciones => _aclaracionesController.sink.add;
  Function(String) get changeFechaRgistro => _fechaRegistroController.sink.add;
  Function(bool) get changeSeparadoAislado => _separadoAisladoController.sink.add;

  Function(String) get changeEmail => _emailController.sink.add;
  Function(String) get changePassword => _passwordController.sink.add;

  // Obtener el ultimo valor
  String get localidad => _localidadController.value;
  String get calle => _calleController.value;
  String get numero => _numeroController.value;
  String get aclaraciones => _aclaracionesController.value;
  String get fechaRegistro => _fechaRegistroController.value;
  bool get separadoAislado => _separadoAisladoController.value;

  String get email => _emailController.value;
  String get password => _passwordController.value;

  dispose() {
    _localidadController?.close();
    _emailController?.close();
    _passwordController?.close();
  }


}