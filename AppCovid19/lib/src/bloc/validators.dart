import 'dart:async';

class Validators {

  ///
  /// Metodo para validar localidad
  /// @author JLopez
  ///
  final validarLocalidad = StreamTransformer<String, String>.fromHandlers(
    handleData: ( localidad, sink ) {
      if(localidad.length >= 1) {
        sink.add(localidad);
      } else {
        sink.addError('Por favor seleccione una localidad');
      }
    }
  );

  ///
  ///
  ///
  final validarCalle = StreamTransformer<String, String>.fromHandlers(
      handleData: ( calle, sink ) {
        if(calle.length >= 1) {
          sink.add(calle);
        } else {
          sink.addError('Por favor ingrese calle');
        }
      }
  );

  ///
  ///
  ///
  final validarNumero = StreamTransformer<String, String>.fromHandlers(
      handleData: ( numero, sink ) {
        if(numero.length >= 1) {
          sink.add(numero);
        } else {
          sink.addError('Por favor ingrese numero.');
        }
      }
  );

  ///
  ///
  ///
  final validarAclaracion = StreamTransformer<String, String>.fromHandlers(
      handleData: ( aclaracion, sink ) {
        if(aclaracion.length >= 1) {
          sink.add(aclaracion);
        } else {
          sink.addError('Por favor ingrese calle');
        }
      }
  );

  ///
  ///
  ///
  final validarFecha = StreamTransformer<String, String>.fromHandlers(
      handleData: ( fecha, sink ) {
        if(fecha.length >= 1) {
          sink.add(fecha);
        } else {
          sink.addError('Por favor ingrese calle');
        }
      }
  );

  ///
  ///
  ///
  final validarSeparadoAislado = StreamTransformer<bool, bool>.fromHandlers(
      handleData: ( separadoAislado, sink ) {
        if(separadoAislado != null) {
          sink.add(separadoAislado);
        } else {
          sink.addError('Por favor ingrese calle');
        }
      }
  );

  ///
  ///
  ///
  final validarEmail = StreamTransformer<String, String>.fromHandlers(
      handleData: ( email, sink ) {
        Pattern pattern = r'^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$';
        RegExp regExp = new RegExp(pattern);

        if( regExp.hasMatch(email) ){
          sink.add(email);
        } else {
          sink.addError('Email no es correcto');
        }
      }
  );

  ///
  ///
  ///
  final validarPassword = StreamTransformer<String, String>.fromHandlers(
      handleData: ( password, sink ) {
        if( password.length >= 6 ) {
          sink.add( password );
        } else {
          sink.addError('Mas de 6 caracteres por favor');
        }
      }
  );
}