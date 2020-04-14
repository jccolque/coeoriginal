import 'dart:convert';
import 'package:covidjujuy_app/src/model/localidad_model.dart';
import 'package:covidjujuy_app/src/model/registro_model.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_typeahead/flutter_typeahead.dart';
import '../main.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'package:connectivity/connectivity.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'temperatura.dart';

class FormularioPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      routes: <String, WidgetBuilder>{
        '/main': (BuildContext context) => MyApp(),
        '/temperatura': (BuildContext context) => TemperaturaPage(),
      },
      home: MyFormularioPage(),
    );
  }
}

class MyFormularioPage extends StatefulWidget {
  @override
  _MyFormularioPage createState() => _MyFormularioPage();
}

class _MyFormularioPage extends State<MyFormularioPage> {
  static const API = 'http://coe.jujuy.gob.ar/covid19/registro';

  static const headers = {'apiKey': '12039i10238129038', 'Content-Type': 'application/json'};

  Future<bool> enviarFormulario(RegistroModel item) async {
    print(json.encode(item.toJson()));
    final response = await http.post(API, body: json.encode(item.toJson()));
    if (response.statusCode == 200) {
      return true;
    }
    return false;
  }

  FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin;
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  var _dniController = TextEditingController();
  var _apellidoController = TextEditingController();
  var _nombreController = TextEditingController();
  var _direccionCalleController = TextEditingController();
  var _direccionNumeroController = TextEditingController();
  var _telefonoController = TextEditingController();

  final _formKey = GlobalKey<FormState>();
  var _aceptarHabilitado = true;
  var _menuHabilitado = false;

  final TextEditingController _typeAheadController = TextEditingController();
  String _localidad;

  void initState() {
    super.initState();
    flutterLocalNotificationsPlugin = FlutterLocalNotificationsPlugin();
    var initializationSettingsAndroid = AndroidInitializationSettings('@mipmap/ic_launcher');
    var initializationSettingsIOS = IOSInitializationSettings(onDidReceiveLocalNotification: onDidReceiveLocalNotification);
    var initializationSettings = InitializationSettings(initializationSettingsAndroid, initializationSettingsIOS);
    flutterLocalNotificationsPlugin.initialize(initializationSettings, onSelectNotification: onSelectNotification);
    _telefonoController.text = '';
    WidgetsBinding.instance.addPostFrameCallback((_) => _handleConfirmFirstMesseage(_scaffoldKey));
  }

  Future<bool> _prompt(BuildContext context) {
    return showDialog(
          context: context,
          child: AlertDialog(
            title: Text('Advertencia - Registro incompleto'),
            content: Text('¿Quiere teminar de registrarse?'),
            actions: <Widget>[
              FlatButton(
                onPressed: () => Navigator.of(context).pop(true),
                child: Text('No'),
              ),
              FlatButton(
                onPressed: () => Navigator.of(context).pop(false),
                child: Text('Si'),
              ),
            ],
          ),
        ) ??
        false;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey,
      resizeToAvoidBottomInset: false,
      body: SingleChildScrollView(
        child: Container(
          decoration: BoxDecoration(
              gradient: LinearGradient(
            begin: Alignment.bottomCenter,
            end: Alignment.topCenter,
            colors: [Colors.blue[900], Colors.lightBlue],
          )),
          height: MediaQuery.of(context).size.height,
          child: SafeArea(
            child: SingleChildScrollView(
              child: Column(
                children: <Widget>[
                  Center(
                    child: Text(
                      'Registro',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 50.0,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                        shadows: [
                          Shadow(
                            blurRadius: 10.0,
                            color: Colors.black.withOpacity(0.4),
                            offset: Offset(0.0, 3.0),
                          ),
                        ],
                      ),
                    ),
                  ),
                  SizedBox(height: 20.0),
                  Center(
                    child: Text(
                      'El gobierno de Jujuy brindará ayuda, consejos e información sobre su estado y también sobre el operativo provincial con respecto al Covid19.'
                      ' Manténgase informado de las recomendaciones en la página oficial del COE.',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 22.0,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                        shadows: [
                          Shadow(
                            blurRadius: 10.0,
                            color: Colors.black.withOpacity(0.4),
                            offset: Offset(0.0, 3.0),
                          ),
                        ],
                      ),
                    ),
                  ),
                  SizedBox(height: 20.0),
                  Center(
                    child: Text(
                      'Ingrese los siguientes datos:',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 18.0,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                        shadows: [
                          Shadow(
                            blurRadius: 10.0,
                            color: Colors.black.withOpacity(0.4),
                            offset: Offset(0.0, 3.0),
                          ),
                        ],
                      ),
                    ),
                  ),
                  SizedBox(height: 20.0),
                  Form(
                    key: _formKey,
                    child: Column(
                      children: <Widget>[
                        Container(
                          margin: EdgeInsets.only(left: 20.0, right: 20.0),
                          child: TextFormField(
                            controller: _dniController,
                            keyboardType: TextInputType.text,
                            inputFormatters: [
                              WhitelistingTextInputFormatter(RegExp("[a-zA-Z0-9]"))
                            ],
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 20.0,
                            ),
                            decoration: const InputDecoration(
                                errorStyle: TextStyle(
                                  color: Colors.white,
                                ),
                                hintText: 'Ingrese su dni sin puntos',
                                labelText: 'DNI',
                                labelStyle: TextStyle(
                                  fontFamily: 'Montserrat',
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                ),
                                focusedBorder: UnderlineInputBorder(borderSide: BorderSide(color: Colors.white))),
                            validator: (String value) {
                              return value.isEmpty
                                  ? 'El campo es obligatorio'
                                  : value.contains('.') || value.contains(',') ? 'Porfavor ingrese el dni sin simbolos' : null;
                            },
                          ),
                        ),
                        SizedBox(height: 20.0),
                        Container(
                          margin: EdgeInsets.only(left: 20.0, right: 20.0),
                          child: TextFormField(
                            controller: _apellidoController,
                            textCapitalization: TextCapitalization.words,
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 20.0,
                            ),
                            decoration: const InputDecoration(
                                errorStyle: TextStyle(
                                  color: Colors.white,
                                ),
                                hintText: 'Ingrese su apellido',
                                labelText: 'Apellido',
                                labelStyle: TextStyle(
                                  fontFamily: 'Montserrat',
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                ),
                                focusedBorder: UnderlineInputBorder(borderSide: BorderSide(color: Colors.white))),
                            validator: (String value) {
                              return value.isEmpty ? 'El campo es obligatorio' : null;
                            },
                          ),
                        ),
                        SizedBox(height: 20.0),
                        Container(
                          margin: EdgeInsets.only(left: 20.0, right: 20.0),
                          child: TextFormField(
                            controller: _nombreController,
                            textCapitalization: TextCapitalization.words,
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 20.0,
                            ),
                            decoration: const InputDecoration(
                                errorStyle: TextStyle(
                                  color: Colors.white,
                                ),
                                hintText: 'Ingrese su nombre',
                                labelText: 'Nombre',
                                labelStyle: TextStyle(
                                  fontFamily: 'Montserrat',
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                ),
                                focusedBorder: UnderlineInputBorder(borderSide: BorderSide(color: Colors.white))),
                            validator: (String value) {
                              return value.isEmpty ? 'El campo es obligatorio' : null;
                            },
                          ),
                        ),
                        SizedBox(height: 30.0),
                        Text(
                          'Domicilio',
                          style: TextStyle(
                            fontSize: 22.0,
                            fontFamily: 'Montserrat',
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        _crearLocalidadAutocomplete(context),
                        SizedBox(height: 30.0),
                        Container(
                          margin: EdgeInsets.only(left: 20.0, right: 20.0),
                          child: TextFormField(
                            controller: _direccionCalleController,
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 20.0,
                            ),
                            decoration: const InputDecoration(
                                errorStyle: TextStyle(
                                  color: Colors.white,
                                ),
                                hintText: 'Ingrese el nombre de su calle actual',
                                labelText: 'Calle',
                                labelStyle: TextStyle(
                                  fontFamily: 'Montserrat',
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                ),
                                focusedBorder: UnderlineInputBorder(borderSide: BorderSide(color: Colors.white))),
                            validator: (String value) {
                              return value.isEmpty ? 'El campo es obligatorio' : null;
                            },
                          ),
                        ),
                        SizedBox(height: 20.0),
                        Container(
                          margin: EdgeInsets.only(left: 20.0, right: 20.0),
                          child: TextFormField(
                            keyboardType: TextInputType.number,
                            controller: _direccionNumeroController,
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 20.0,
                            ),
                            decoration: const InputDecoration(
                                errorStyle: TextStyle(
                                  color: Colors.white,
                                ),
                                hintText: 'Ingrese el nro de su domicilio actual',
                                labelText: 'Nro',
                                labelStyle: TextStyle(
                                  fontFamily: 'Montserrat',
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                ),
                                focusedBorder: UnderlineInputBorder(borderSide: BorderSide(color: Colors.white))),
                            validator: (String value) {
                              return value.isEmpty ? 'El campo es obligatorio' : null;
                            },
                          ),
                        ),
                        SizedBox(height: 20.0),
                        Container(
                          margin: EdgeInsets.only(left: 20.0, right: 20.0),
                          child: TextFormField(
                            controller: _telefonoController,
                            keyboardType: TextInputType.number,
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 20.0,
                            ),
                            decoration: const InputDecoration(
                                errorStyle: TextStyle(
                                  color: Colors.white,
                                ),
                                hintText: 'Ingrese su nro telefónico',
                                labelText: 'Nro telefónico',
                                labelStyle: TextStyle(
                                  fontFamily: 'Montserrat',
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                ),
                                focusedBorder: UnderlineInputBorder(borderSide: BorderSide(color: Colors.white))),
                            validator: (String value) {
                              return value.isEmpty
                                  ? 'El campo es obligatorio'
                                  : value.length <= 6 ? 'El nro es demasiado corto, ingrese un nro valido' : null;
                            },
                          ),
                        ),
                      ],
                    ),
                  ),
                  //SizedBox(height: 40.0),
                  SizedBox(height: 80.0),
                  Visibility(
                    visible: _aceptarHabilitado,
                    child: RaisedButton(
                      padding: EdgeInsets.only(top: 10.0, bottom: 10.0, left: 100.0, right: 100.0),
                      color: Colors.deepOrangeAccent,
                      splashColor: Colors.blueAccent,
                      elevation: 4,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(25.0),
                      ),
                      onPressed: () async {
                        setState(() {
                          _aceptarHabilitado = false;
                        });
                        if (_formKey.currentState.validate()) {
                          final form = RegistroModel(
                              dniIndividuo: _dniController.text,
                              apellido: _apellidoController.text,
                              nombre: _nombreController.text,
                              direccionCalle: _direccionCalleController.text,
                              direccionNumero: _direccionNumeroController.text,
                              telefono: _telefonoController.text,
                              localidadNombre: _localidad);
                          var connectivityResult = await (Connectivity().checkConnectivity());

                          if (connectivityResult == ConnectivityResult.mobile) {
                            final result = await enviarFormulario(form);
                            if (result == true) {
                              final res = await _setRegistroSharedPref(form);
                              saveDniCredentials(_dniController.text);
                              showInSnackBar('Datos personales enviados con exito puede seguír al menu principal');
                              setState(() {
                                _menuHabilitado = false;
                                Navigator.of(context).pushNamed('/main');
                              });
                            } else {
                              showInSnackBar('Datos enviados incorrectos');
                              setState(() {
                                _aceptarHabilitado = true;
                              });
                            }
                          } else if (connectivityResult == ConnectivityResult.wifi) {
                            final result = await enviarFormulario(form);
                            if (result == true) {
                              final res = await _setRegistroSharedPref(form);
                              saveDniCredentials(_dniController.text);
                              showInSnackBar('Datos personales enviados con exito puede seguír al menu principal');
//                              setupNotification();
                              setState(() {
                                _menuHabilitado = false;
                                Navigator.of(context).pushNamed('/main');
                              });
                            } else {
                              showInSnackBar('Datos enviados incorrectos');
                              setState(() {
                                _aceptarHabilitado = true;
                              });
                            }
                          } else {
                            setState(() {
                              _aceptarHabilitado = true;
                            });
                            showInSnackBar('Algo salió mal por favor verifique su conexion a internet, e intente de nuevo en unos segundos');
                          }
                        } else {
                          showInSnackBar('Provea todos sus datos');
                          setState(() {
                            _aceptarHabilitado = true;
                          });
                        }
                      },
                      child: Text(
                        'Aceptar',
                        style: TextStyle(color: Colors.white, fontSize: 22.0, fontWeight: FontWeight.bold, fontFamily: 'Montserrat'),
                      ),
                    ),
                  ),
                  SizedBox(height: 30.0),
                  Visibility(
                    visible: _menuHabilitado,
                    child: RaisedButton(
                      padding: EdgeInsets.only(top: 10.0, bottom: 10.0, left: 70.0, right: 70.0),
                      color: Colors.white,
                      elevation: 4,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(25.0),
                      ),
                      onPressed: () {
                        Navigator.of(context).pushNamed('/main');
                      },
                      child: Text(
                        'Menu principal',
                        style: TextStyle(color: Colors.black, fontSize: 22.0, fontWeight: FontWeight.bold, fontFamily: 'Montserrat'),
                      ),
                    ),
                  ),
                  SizedBox(height: 100),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _crearLocalidadAutocomplete(BuildContext context) {
    return Container(
        padding: EdgeInsets.symmetric(horizontal: 20.0),
        child: Container(
          child: Column(
            children: <Widget>[
              Text(''),
              TypeAheadFormField(
                textFieldConfiguration: TextFieldConfiguration(
                    style: TextStyle(color: Colors.white, fontSize: 20.0),
                    controller: this._typeAheadController,
                    decoration: InputDecoration(
                        labelText: 'Localidad',
                        errorStyle: TextStyle(
                          fontFamily: 'Montserrat',
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                        labelStyle: TextStyle(
                          fontFamily: 'Montserrat',
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                        focusedBorder: UnderlineInputBorder(borderSide: BorderSide(color: Colors.white)))),
                suggestionsCallback: (pattern) {
                  print(pattern);
                  return getLocalidades(pattern);
                },
                itemBuilder: (context, suggestion) {
                  return ListTile(
                    title: Text(
                      suggestion,
                      style: TextStyle(color: Colors.black),
                    ),
                  );
                },
                transitionBuilder: (context, suggestionsBox, controller) {
                  return suggestionsBox;
                },
                onSuggestionSelected: (suggestion) {
                  print('suggestion');
                  print(suggestion);
                  this._typeAheadController.text = suggestion;
                  setState(() => this._localidad = suggestion);
                },
                validator: (value) {
                  if (value.isEmpty) {
                    return 'Por favor seleccione una localidad';
                  }
                },
                onSaved: (value) => this._localidad = value,
              ),
            ],
          ),
        ));
  }

  Future<List<String>> getLocalidades(String filtro) async {
    print('fetchPost');
    final response = await http.get('http://coe.jujuy.gob.ar/georef/localidad-autocomplete/?q=${filtro}');

    if (response.statusCode == 200) {
      // Si el servidor devuelve una repuesta OK, parseamos el JSON
      List<Result> list = LocalidadModel.fromJson(json.decode(response.body)).results;
      List<String> salida = List();
      list.forEach((text) {
        salida.add(text.text);
      });
      print(salida);
      return salida;
      return null;
    } else {
      // Si esta respuesta no fue OK, lanza un error.
      throw Exception('Failed to load post');
    }
  }

  Future<bool> _setRegistroSharedPref(RegistroModel item) async {
    print('_setRegistroSharedPref');
    print(item.toJson());
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setString('nombreGuardado', item.nombre);
    await prefs.setString('apellidoGuardado', item.apellido);
    await prefs.setString('domicilioGuardado', item.direccionCalle + ' ' + item.direccionNumero);

    return true;
  }

  void saveDniCredentials(String value) {
    int dni = int.parse(value);
    _saveDniFromSharedPref(dni).then((bool value) {
      //showInSnackBar('dni guardado $value');
    });
  }

  Future<bool> _saveDniFromSharedPref(int dni) async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setBool('loadOk', true);
    return await prefs.setInt('savedDniNumber', dni);
  }

  void showInSnackBar(String value) {
    SnackBar mySnackBar = SnackBar(
      content: InkWell(
        child: Text(
          value,
          style: TextStyle(
            color: Colors.white,
          ),
        ),
      ),
      backgroundColor: Colors.pink,
    );
    _scaffoldKey.currentState.removeCurrentSnackBar();
    _scaffoldKey.currentState.showSnackBar(mySnackBar);
  }

  void _handleConfirmFirstMesseage(GlobalKey<ScaffoldState> _scaffoldKey) {
    confirmFirstMesseage(context, _scaffoldKey).then((bool value) {
      if (value) {
        showInSnackBar('Términos de registro aceptados');
      }
    });
  }

  void setupNotificationPlugin() {
    flutterLocalNotificationsPlugin = FlutterLocalNotificationsPlugin();
    var initializationSettingsAndroid = AndroidInitializationSettings(' @ mipmap / ic_launcher');
    var initializationSettingsIOS = IOSInitializationSettings(
      onDidReceiveLocalNotification: onDidReceiveLocalNotification,
    );
    var initializationSettings = InitializationSettings(initializationSettingsAndroid, initializationSettingsIOS);

    flutterLocalNotificationsPlugin.initialize(
      initializationSettings,
      onSelectNotification: onSelectNotification,
    );
  }

  Future onSelectNotification(String payload) async {
    if (payload != null) {
      debugPrint('notification payload: ' + payload);
    }
  }

  Future onDidReceiveLocalNotification(int id, String title, String body, String payload) async {
    // display a dialog with the notification details, tap ok to go to another page
    await showDialog(
      context: context,
      builder: (BuildContext context) => CupertinoAlertDialog(
        title: Text(title),
        content: Text(body),
        actions: [
          CupertinoDialogAction(
            isDefaultAction: true,
            child: Text('Ok'),
            onPressed: () async {
              Navigator.of(context, rootNavigator: true).pop();
              await Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => TemperaturaPage(),
                ),
              );
            },
          )
        ],
      ),
    );
  }

  void setupNotification() async {
    var time = Time(10, 0, 0);
    var time1 = Time(14, 0, 0);
    var time2 = Time(18, 0, 00);
    var time3 = Time(22, 0, 00);
    var androidPlatformChannelSpecifics = AndroidNotificationDetails(
        'repeatDailyAtTime channel id', 'repeatDailyAtTime temperatura', 'repeatDailyAtTime temperatura',
        importance: Importance.Max, priority: Priority.High, ongoing: true);
    var iOSPlatformChannelSpecifics = IOSNotificationDetails();
    var platformChannelSpecifics = NotificationDetails(androidPlatformChannelSpecifics, iOSPlatformChannelSpecifics);
    await flutterLocalNotificationsPlugin.showDailyAtTime(0, 'Recordatorio', '¡Compruebe su temperatura!', time, platformChannelSpecifics);
    await flutterLocalNotificationsPlugin.showDailyAtTime(1, 'Recordatorio', '¡Compruebe su temperatura!', time1, platformChannelSpecifics);
    await flutterLocalNotificationsPlugin.showDailyAtTime(2, 'Recordatorio', '¡Compruebe su temperatura!', time2, platformChannelSpecifics);
    await flutterLocalNotificationsPlugin.showDailyAtTime(3, 'Recordatorio', '¡Compruebe su temperatura!', time3, platformChannelSpecifics);
  }
}

Future<bool> confirmFirstMesseage(BuildContext context, GlobalKey<ScaffoldState> _scaffoldKey) {
  return showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24.0)),
          title: Column(
            children: <Widget>[
              Center(
                child: Text(
                  'Esta es una herramienta para la salud pública, todos los datos que aquí ingrese son fundamentales.'
                  ' Una vez finalizado el registro no podrá modificar los datos ingresados, por favor tomese su tiempo y sea preciso.',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 22.0, fontFamily: 'Montserrat'),
                ),
              ),
            ],
          ),
          elevation: 7.0,
          //backgroundColor: Colors.grey,
          actions: <Widget>[
            FlatButton(
              child: Text(
                'Aceptar',
                style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold, fontSize: 22.0, fontFamily: 'Montserrat'),
              ),
              onPressed: () {
                Navigator.of(context).pop(true);
              },
            )
          ],
        );
      });
}
