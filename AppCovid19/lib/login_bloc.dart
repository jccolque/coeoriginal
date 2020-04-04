import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:equatable/equatable.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:bloc/bloc.dart';

enum LoginExceptionType { emailIncorrect, passwordIncorrect, unknownError }

class LoginException extends Equatable implements Exception {
  final LoginExceptionType type;
  LoginException(this.type);

  @override
  get props => [type];

  @override
  String toString() {
    switch (type) {
      case LoginExceptionType.emailIncorrect:
        return 'The e-mail is incorrect';
      case LoginExceptionType.passwordIncorrect:
        return 'The password is incorrect';
      case LoginExceptionType.unknownError:
        return 'An unknown error has ocurred';
      default:
        return type.toString();
    }
  }
}

class UserRepository {
  final _storage = FlutterSecureStorage();

  Future<void> auth({@required String email, @required String password}) async {
    var response = await Dio().post(
      'https://endpointDelGobierno.gov.ar/verificarUsuario',
      data: json.encode({
        "email": email,
        "password": password,
      }),
    );
    Map decodedData = json.decode(response.data);
    if (decodedData.containsKey('error')) {
      if (decodedData['error'] == 'email') {
        throw LoginExceptionType.emailIncorrect;
      } else if (decodedData['error'] == 'password') {
        throw LoginExceptionType.passwordIncorrect;
      } else {
        throw LoginExceptionType.unknownError;
      }
    }
  }

  Future<void> deleteLogin() async {
    await Future.wait(
        [_storage.delete(key: 'email'), _storage.delete(key: 'password')]);
  }

  Future<void> persistLogin(String email, String password) async {
    await Future.wait([
      _storage.write(key: 'email', value: email),
      _storage.write(key: 'password', value: password)
    ]);
  }

  Future<bool> hasLogin() async {
    var values = await Future.wait(
        [_storage.read(key: 'email'), _storage.read(key: 'password')]);
    return values.every((v) => v != null);
  }
}

enum AuthState { uninitialized, authenticated, unauthenticated, loading }

abstract class AuthEvent extends Equatable {
  final List props;

  AuthEvent([this.props = const []]);
}

class AppStarted extends AuthEvent {
  @override
  String toString() => 'AppStarted';
}

class LoggedIn extends AuthEvent {
  final String email;
  final String password;

  LoggedIn({@required this.email, @required this.password})
      : super([email, password]);

  @override
  String toString() => 'LoggedIn { email: $email, password: $password }';
}

class LoggedOut extends AuthEvent {
  @override
  String toString() => 'LoggedOut';
}

class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final UserRepository repository;

  AuthBloc({@required this.repository}) : assert(repository != null);

  @override
  AuthState get initialState => AuthState.uninitialized;

  @override
  Stream<AuthState> mapEventToState(AuthEvent event) async* {
    if (event is AppStarted) {
      final bool hasLogin = await repository.hasLogin();

      if (hasLogin) {
        yield AuthState.authenticated;
      } else {
        yield AuthState.unauthenticated;
      }
    }

    if (event is LoggedIn) {
      yield AuthState.loading;
      await repository.persistLogin(event.email, event.password);
      yield AuthState.authenticated;
    }

    if (event is LoggedOut) {
      yield AuthState.loading;
      await repository.deleteLogin();
      yield AuthState.unauthenticated;
    }
  }
}
