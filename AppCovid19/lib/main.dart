import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:isolate';
import 'dart:ui';
import 'package:background_locator/location_dto.dart';
import 'package:background_locator/location_settings.dart';
import 'package:covidjujuy_app/pages/permiso_otorgado.dart';
import 'package:covidjujuy_app/pages/permiso_otorgado_control.dart';
import 'package:covidjujuy_app/pages/salvo_conducto.dart';
import 'package:covidjujuy_app/pages/solicitar_permiso.dart';
import 'package:covidjujuy_app/src/model/permiso_ya_otorgado_model.dart';
import 'package:covidjujuy_app/src/model/respuesta_permiso_model.dart';
import 'package:covidjujuy_app/ui/formulario.dart';
import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:gps/gps.dart';
import 'package:intl/intl.dart';
import 'ui/cuestionario.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:permission_handler/permission_handler.dart';

import 'package:background_locator/background_locator.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      routes: <String, WidgetBuilder>{
        '/cuestionario': (BuildContext context) => CuestionarioPage(),
        '/formulario': (BuildContext context) => FormularioPage(),
        '/salvoconducto': (BuildContext context) => SalvoConducto(),
        '/solicitarpermiso': (BuildContext context) => SolicitarPermiso(),
        '/permisootorgado': (BuildContext context) => PermisoOtorgado(),
        '/permisootorgadocontrol': (BuildContext context) => PermisoOtorgadoControl(),
        '/main': (BuildContext context) => MyApp(),
      },
      home: MyLoginPage(),
    );
  }
}

class MyLoginPage extends StatefulWidget {
  MyLoginPage({Key key}) : super(key: key);

  @override
  _MyLoginPageState createState() => _MyLoginPageState();
}

class _MyLoginPageState extends State<MyLoginPage> {
  Future<void> launched;
  String _coelaunchUrl = 'http://coe.jujuy.gob.ar';

  bool _termCondAceptados = false;
  bool _locationUp = false;
  int _dni = 0;
  bool _loaded = false;
  ReceivePort port = ReceivePort();

  String logStr = '';
  bool isRunning;
  LocationDto lastLocation;
  DateTime lastTimeLocation;
  String _latitud;
  String _longitud;
  static const String _isolateName = 'LocatorIsolate';

  String _dniOperador = '';
  String _password = '';
  bool _encuestaRealizada = false;
  bool _geoTrackActicado = false;

  @override
  void initState() {
    _launchFirstTermCondDialogConfirmation();
    super.initState();
    if (IsolateNameServer.lookupPortByName(_isolateName) != null) {
      IsolateNameServer.removePortNameMapping(_isolateName);
    }

    _getGeoActivateSharedPref().then((v){
      setState(() {
        _geoTrackActicado = v;
      });
    });

    IsolateNameServer.registerPortWithName(port.sendPort, _isolateName);

    port.listen(
      (dynamic data) async {
        await updateUI(data);
      },
    );
    _getLoadedSharedPref().then((v){
      setState(() {
        if(v == true) {
          _loaded = true;
        }else {
          _loaded = false;
        }
      });
    });
    _getDniSharedPref().then((v){});

    initPlatformState();
    _getPermisoOtorgadoSharedPref().then((permiso) {
      print('permiso');
      print(permiso);
      setState(() {
        if (permiso != null) {
          _encuestaRealizada = permiso;
        } else {
          _encuestaRealizada = false;
        }
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    SystemChrome.setSystemUIOverlayStyle(SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
    ));

    return WillPopScope(
      onWillPop: () => Future.value(false),
      child: Scaffold(
        key: _scaffoldKey,
        resizeToAvoidBottomInset: false,
        body: Container(
          child: Container(
              decoration: BoxDecoration(
                  gradient: LinearGradient(
                begin: Alignment.bottomCenter,
                end: Alignment.topCenter,
                colors: [Colors.blue[900], Colors.lightBlue],
              )),
              height: MediaQuery.of(context).size.height,
              child: Container(
                child: build_child(context),
              )),
        ),
      ),
    );
  }

  Widget build_child(BuildContext context) {
    if (_loaded) {
      return SingleChildScrollView(
        child: SafeArea(
            child: Column(
          children: <Widget>[
            Container(
              padding: EdgeInsets.only(top: 20),
              child: Column(
                children: <Widget>[
                  Image.asset(
                    'assets/graphics/GOBCOEJUwide.jpg',
                    width: 300,
                  ),
                  SizedBox(height: 20.0),
                  Text(
                    'Cuestionario',
                    style: TextStyle(
                      fontSize: 45.0,
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
                  Text(
                    'COVID-19',
                    style: TextStyle(
                      fontSize: 30.0,
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
                ],
              ),
            ),
            Container(
              padding: EdgeInsets.only(left: 20.0, right: 20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  SizedBox(height: 50.0),
                  Center(
                    child: Text(
                      _dni != 0 ? 'Todas las respuestas en este dispositivo serán enviadas con este dni: $_dni' : '',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 22.0,
                        fontWeight: FontWeight.bold,
                        fontFamily: 'Montserrat',
                      ),
                    ),
                  ),
                  SizedBox(height: 60.0),
                  Visibility(
                    visible: !_termCondAceptados,
                    child: Container(
                      child: Center(
                        child: RaisedButton(
                          padding: EdgeInsets.only(top: 10.0, bottom: 10.0, left: 30.0, right: 30.0),
                          color: Colors.yellowAccent,
                          splashColor: Colors.blueAccent,
                          elevation: 4,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(24.0),
                          ),
                          onPressed: () async {
                            _handleFirsGeoConfirmation(_scaffoldKey);
                          },
                          child: Text(
                            'Ver términos y condiciones de uso',
                            textAlign: TextAlign.center,
                            style: TextStyle(color: Colors.black, fontSize: 22.0, fontWeight: FontWeight.bold, fontFamily: 'Montserrat'),
                          ),
                        ),
                      ),
                    ),
                  ),
                  Visibility(
                    visible: _termCondAceptados,
                    child: Container(
                      child: Center(
                        child: RaisedButton(
                          padding: EdgeInsets.only(top: 10.0, bottom: 10.0, left: 90.0, right: 90.0),
                          color: Colors.white,
                          splashColor: Colors.blueAccent,
                          elevation: 4,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(24.0),
                          ),
                          onPressed: () async {
                            print('DNI OBTENIDO');
                            print(_dni);
                            _dni == 0 ? _getDniFromSharedPref() : (!_termCondAceptados ? _launchTermCondDialogConfirmation() : _checkPermissions());
                            //_getDniFromSharedPref();
                            //_checkPermissions();
                          },
                          child: Text(
                            'Cuestionario covid-19',
                            textAlign: TextAlign.center,
                            style: TextStyle(color: Colors.black, fontSize: 22.0, fontWeight: FontWeight.bold, fontFamily: 'Montserrat'),
                          ),
                        ),
                      ),
                    ),
                  ),

                  SizedBox(height: 20.0),
                  Container(
                    child: Center(
                      child: RaisedButton(
                        padding: EdgeInsets.only(top: 10.0, bottom: 10.0, left: 60.0, right: 60.0),
                        color: Colors.white,
                        splashColor: Colors.blueAccent,
                        elevation: 4,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(24.0),
                        ),
                        onPressed: () {
                          //Navigator.of(context).pushNamed('/coe');
                          _launchInBroser(_coelaunchUrl);
                        },
                        child: Text(
                          'Información oficial COE',
                          textAlign: TextAlign.center,
                          style: TextStyle(color: Colors.black, fontSize: 22.0, fontWeight: FontWeight.bold, fontFamily: 'Montserrat'),
                        ),
                      ),
                    ),
                  ),
                  SizedBox(height: 30),
                  Container(
                    child: Visibility(
                      visible: _encuestaRealizada,
                      child: Center(
                        child: RaisedButton(
                          padding: EdgeInsets.only(top: 10.0, bottom: 10.0, left: 80.0, right: 80.0),
                          color: Colors.white,
                          splashColor: Colors.blueAccent,
                          elevation: 4,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(24.0),
                          ),
                          onPressed: () {
                            _lauchSalvoConductoForm(context);
                          },
                          child: Text(
                            'Salvo Conducto',
                            textAlign: TextAlign.center,
                            style: TextStyle(color: Colors.black, fontSize: 22.0, fontWeight: FontWeight.bold, fontFamily: 'Montserrat'),
                          ),
                        ),
                      ),
                    ),
                  ),
                  SizedBox(height: 20.0),

                  Container(
                    child: Visibility(
                      visible: _encuestaRealizada && !_geoTrackActicado,
                      child: Center(
                        child: RaisedButton(
                          padding: EdgeInsets.only(top: 10.0, bottom: 10.0, left: 60.0, right: 60.0),
                          color: Colors.white,
                          splashColor: Colors.blueAccent,
                          elevation: 4,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(24.0),
                          ),
                          onPressed: () {
                            _mostrarDialogIngreseDatos(context);
                          },
                          child: Text(
                            'Activar Geotracking',
                            textAlign: TextAlign.center,
                            style: TextStyle(color: Colors.black, fontSize: 22.0, fontWeight: FontWeight.bold, fontFamily: 'Montserrat'),
                          ),
                        ),
                      ),
                    ),
                  ),
                  Container(
                    child: Visibility(
                      visible: _encuestaRealizada && _geoTrackActicado,
                      child: Center(
                        child: RaisedButton(
                          padding: EdgeInsets.only(top: 10.0, bottom: 10.0, left: 50.0, right: 50.0),
                          color: Colors.red,
                          splashColor: Colors.white,
                          elevation: 4,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(24.0),
                          ),
                          onPressed: () {
//                            _mostrarDialogIngreseDatos(context);
                          },
                          child: Text(
                            'GeoTracking Activado',
                            textAlign: TextAlign.center,
                            style: TextStyle(color: Colors.white, fontSize: 22.0, fontWeight: FontWeight.bold, fontFamily: 'Montserrat'),
                          ),
                        ),
                      ),
                    ),
                  ),

                  SizedBox(height: 30),

                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: <Widget>[
                      Center(
                        child: Image.asset(
                          'assets/graphics/JujuyEnergiaVivaTrazoNegro.png',
                          height: 40,
                        ),
                      ),
                      Container(
                          child: Image.asset(
                        'assets/graphics/GA_logo.png',
                        height: 30,
                      )),
                      Container(
                          child: Text(
                        '@GA_ide',
                        style: TextStyle(color: Colors.white),
                      )),
                    ],
                  ),
                ],
              ),
            ),
          ],
        )),
      );
    } else {
      return Container(
        child: SafeArea(
          child: Column(
            children: <Widget>[
              SizedBox(height: 20.0),
              Image.asset(
                'assets/graphics/banner.png',
                width: 200,
              ),
              SizedBox(height: 20.0),
              Text(
                'Cuestionario',
                style: TextStyle(
                  fontSize: 45.0,
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
              Text(
                'COVID-19',
                style: TextStyle(
                  fontSize: 30.0,
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
              SizedBox(height: 100.0),
              Visibility(
                visible: !_loaded,
                child: Container(
                  child: Center(
                    child: RaisedButton(
                      padding: EdgeInsets.only(top: 10.0, bottom: 10.0, left: 60.0, right: 60.0),
                      color: Colors.lightGreen,
                      splashColor: Colors.blueAccent,
                      elevation: 4,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(24.0),
                      ),
                      onPressed: () {
                        _getDniFromSharedPref();
                      },
                      child: Text(
                        'Ingresar',
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Colors.white, fontSize: 40.0, fontWeight: FontWeight.bold, fontFamily: 'Montserrat'),
                      ),
                    ),
                  ),
                ),
              )
            ],
          ),
        ),
      );
    }
  }

  Future<void> _getDniFromSharedPref() async {
    print('_getDniFromSharedPref');
    SharedPreferences prefs = await SharedPreferences.getInstance();
    final startupDniNumber = prefs.getInt('savedDniNumber');
    if (startupDniNumber == null) {
      setState(() {
        _dni = 0;
        _loaded = false;
      });
      Navigator.of(context).pushNamed('/formulario');
    } else {
      setState(() {
        _dni = startupDniNumber;
        _loaded = true;
      });
    }
  }

  Future<void> _getDniSharedPref() async {
    print('_getDniSharedPref');
    SharedPreferences prefs = await SharedPreferences.getInstance();
    final startupDniNumber = prefs.getInt('savedDniNumber');
    if (startupDniNumber == null) {
      setState(() {
        _dni = 0;
      });
    } else {
      setState(() {
        _dni = startupDniNumber;
      });
    }
  }

  Future<bool> _getTermCondAceptadosFromSharedPref() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    bool result = await prefs.getBool('termCond');
    if (result == null) {
      return false;
    } else {
      return true;
    }
  }

  Future<bool> _setTermCondAceptadosFromSharedPref() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    return await prefs.setBool('termCond', true);
  }

  Future<void> _launchInBroser(String url) async {
    if (await canLaunch(url)) {
      await launch(
        url,
        forceSafariVC: false,
        forceWebView: false,
        headers: <String, String>{'header_key': 'header_value'},
      );
    } else {
      throw 'Could not launch $url';
    }
  }

  Future<void> _launchTermCondDialogConfirmation() async {
    await _getTermCondAceptadosFromSharedPref().then(_updateTermAndCondt);
    if (!_termCondAceptados) {
      WidgetsBinding.instance.addPostFrameCallback((_) => _handleFirsGeoConfirmation(_scaffoldKey));
    }
  }

  Future<void> _launchFirstTermCondDialogConfirmation() async {
    await _getTermCondAceptadosFromSharedPref().then(_updateTermAndCondt);
  }

  Future<bool> _getLoadedSharedPref() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    final loadOk = await prefs.getBool('loadOk');
    return loadOk != null ? loadOk : false;
  }

  Future<bool> _getPermisoOtorgadoSharedPref() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    final permiso = await prefs.getBool('encuestaRealizada');
    return permiso != null ? permiso : false;
  }

  Future<bool> _lauchSalvoConductoForm(BuildContext context) async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    final startupDniNumber = prefs.getInt('savedDniNumber');
    final imagen = prefs.getBool('imagenPerfil');
    final permiso = prefs.getBool('permisoOtorgado');
    if (startupDniNumber != null) {
      final perm = PermisoYaOtorgadoModel(dniIndividuo: _dni.toString(), token: "");
      await _getPermisosYaOtorgado(perm).then((v) {
        print('permiso otorgado');
        print(v);
        if (v == true) {
          Navigator.of(context).pushNamed('/permisootorgado');
          return true;
        } else {
          if (imagen != null) {
            if (imagen == true) {
              if (permiso != null) {
                if (permiso == true) {
                  Navigator.of(context).pushNamed('/permisootorgado');
                  return true;
                } else {
                  Navigator.of(context).pushNamed('/solicitarpermiso');
                  return true;
                }
              } else {
                Navigator.of(context).pushNamed('/solicitarpermiso');
                return true;
              }
            } else {
              Navigator.of(context).pushNamed('/salvoconducto');
              return true;
            }
          } else {
            Navigator.of(context).pushNamed('/salvoconducto');
            return true;
          }
        }
      });
    }
  }

  void _updateTermAndCondt(bool value) {
    setState(() {
      _termCondAceptados = value;
    });
  }

  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  void _setLatitudLongitud() async {
    var latlng = await Gps.currentGps();
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setDouble('latitud', double.parse(latlng.lat));
    await prefs.setDouble('longitud', double.parse(latlng.lng));
  }

  Future<void> _getLatitudLongitud() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    final latitud = await prefs.getDouble('latitud');
    final longitud = await prefs.getDouble('longitud');
    setState(() {
      _latitud = latitud.toString();
      _longitud = longitud.toString();
      _geoTrackActicado = true;
      _setGeoActivateSharedPref(true);
    });
  }

  Future<bool> _getPermisosYaOtorgado(PermisoYaOtorgadoModel permisoYaOtorgadoModel) async {
    final response = await http.post('http://coe.jujuy.gob.ar/covid19/get/salvoconducto', body: (utf8.encode(json.encode(permisoYaOtorgadoModel))));
    if (response.statusCode == 200) {
      RespuestaPermisoModel list = RespuestaPermisoModel.fromJson(json.decode(response.body));
      await _setPermisoOtorgadoSharedPref(list).then((v) {
        print('ok');
      });
      await _setPermisoSharedPref(true).then((v){
        return true;
      });
      return true;
    } else {
      await _setPermisoSharedPref(false).then((v){
        return false;
      });
    }
  }

  Future<void> _setGeoActivateSharedPref(bool permiso) async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    return await prefs.setBool('geoTrackActicado', permiso);
  }

  Future<bool> _getGeoActivateSharedPref() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    final loadOk = await prefs.getBool('geoTrackActicado');
    return loadOk != null ? loadOk : false;
  }

  Future<void> _setPermisoSharedPref(bool permiso) async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    return await prefs.setBool('permisoOtorgado', permiso);
  }

  Future<void> _setPermisoOtorgadoSharedPref(RespuestaPermisoModel permisoOtorgado) async {
    DateFormat dateFormat = DateFormat("dd/MM/yyyy");
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setString('nombreCompletoOtorgado', permisoOtorgado.nombreCompleto);
    await prefs.setString('dniOtorgado', permisoOtorgado.dniIndividuo);
    await prefs.setString('domicilioOtorgado', permisoOtorgado.domicilio);
    await prefs.setString('textoOtorgado', permisoOtorgado.texto);
    await prefs.setBool('controlOtorgado', permisoOtorgado.control);
    await prefs.setString('imagenPerfilOtorgada', permisoOtorgado.imagen);
    await prefs.setString('qrOtorgado', permisoOtorgado.qr);
    await prefs.setString('fechaInicioOtorgado', dateFormat.format(permisoOtorgado.fechaInicio));
    await prefs.setString('fechaFinOtorgado', dateFormat.format(permisoOtorgado.fechaFin));
    await prefs.setString('horaInicioOtorgado', permisoOtorgado.horaInicio);
    await prefs.setString('horaFinOtorgado', permisoOtorgado.horaFin);
    await prefs.setString('textoOtorgado', permisoOtorgado.texto);
  }

  void _checkPermissions() async {
    Map<PermissionGroup, PermissionStatus> permissions = await PermissionHandler().requestPermissions([PermissionGroup.location]);
    PermissionStatus permission = await PermissionHandler().checkPermissionStatus(PermissionGroup.location);
    ServiceStatus serviceStatus = await PermissionHandler().checkServiceStatus(PermissionGroup.location);

    if (permission == PermissionStatus.granted) {
      if (serviceStatus == ServiceStatus.enabled) {
        _setLatitudLongitud();
        setState(() {
          _locationUp = true;
        });
        _termCondAceptados && _dni != 0
            ? Navigator.of(context).pushNamed('/cuestionario')
            : showInSnackBar('No podrá usar la app si no acepta los términos y condiciones de uso');
      } else {
        showInSnackBar('Para usar la aplicacion mantenga prendida la ubicación gps');
      }
    } else if (permission == PermissionStatus.neverAskAgain) {
      _handleConfirmPermissions(_scaffoldKey);
    }
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
        onTap: () {
          !_termCondAceptados ? _handleFirsGeoConfirmation(_scaffoldKey) : showInSnackBar('Términos y condiciones de úso aceptados');
        },
      ),
      backgroundColor: Colors.pink,
    );
    _scaffoldKey.currentState.removeCurrentSnackBar();
    _scaffoldKey.currentState.showSnackBar(mySnackBar);
  }

  void _handleConfirmPermissions(GlobalKey<ScaffoldState> _scaffoldKey) {
    confirmPermissions(context, _scaffoldKey).then((bool value) {
      if (value) {
        showInSnackBar('Recuerde que si no acepta los permisos no podrá usar la aplicación');
      } else {
        showInSnackBar('Para usar la aplicacion deberá aceptar los terminos y condiciones de úso');
      }
    });
  }

  void _handleFirsGeoConfirmation(GlobalKey<ScaffoldState> _scaffoldKey) {
    confirmGeolocalizationDialog(context, _scaffoldKey).then((bool value) {
      if (value) {
        _setTermCondAceptadosFromSharedPref().then((bool commited) {
          setState(() {
            _termCondAceptados = true;
          });
        });
      } else {
        showInSnackBar('Para usar la aplicacion deberá aceptar los terminos y condiciones de úso');
      }
    });
  }

  Future<void> initPlatformState() async {
    print('Initializing...');
    await BackgroundLocator.initialize();
    print('Initialization done');
    final _isRunning = await BackgroundLocator.isRegisterLocationUpdate();
    setState(() {
      isRunning = _isRunning;
    });
    print('Running ${isRunning.toString()}');
  }

  Future<void> updateUI(LocationDto data) async {
    await apiRequest(data);
  }

  static void callback(LocationDto locationDto) async {
    print('location in dart: ${locationDto.toString()}');
    final SendPort send = IsolateNameServer.lookupPortByName(_isolateName);
    send?.send(locationDto);
  }

  static void notificationCallback() {
    print('notificationCallback');
  }

  void startLocationService() {
    BackgroundLocator.registerLocationUpdate(
      callback,
      androidNotificationCallback: notificationCallback,
      settings: LocationSettings(
          notificationTitle: "Covid19 - Jujuy",
          notificationMsg: "Su ubicación esta siendo rastreada",
          wakeLockTime: 20,
          autoStop: false,
          interval: 600),
    );
  }

  ///
  /// Metodo para enviar las coordenadas hacia /covid19/tracking
  /// @authos JLopez
  ///
  Future<String> apiRequest(LocationDto locationDto) async {
    var now = DateTime.now();
    var fecha = DateFormat('yyyyMMdd');
    var hora = DateFormat('HHmm');

    final item = {
      "dni_individuo": _dni,
      "fecha": fecha.format(now),
      "hora": hora.format(now),
      "latitud": locationDto.latitude,
      "longitud": locationDto.longitude
    };
    HttpClient httpClient = HttpClient();
    HttpClientRequest request = await httpClient.postUrl(Uri.parse('http://coe.jujuy.gob.ar/covid19/tracking'));
    request.headers.set('content-type', 'application/json');
    request.add(utf8.encode(json.encode(item)));
    HttpClientResponse response = await request.close();
    print(response.statusCode);
    if (response.statusCode == 200) {
      String reply = await response.transform(utf8.decoder).join();
      httpClient.close();
      return reply;
    } else {
      String reply = await response.transform(utf8.decoder).join();
      return null;
    }
  }

  ///
  /// Metodo para enviar las coordenadas hacia /covid19/start/tracking
  /// @authos German Udaeta
  ///
  Future<String> apiRequestStartTracking() async {
    final item = {"dni_individuo": _dni, "dni_operador": _dniOperador, "password": _password, "latitud": _latitud, "longitud": _longitud};
    HttpClient httpClient = HttpClient();
    HttpClientRequest request = await httpClient.postUrl(Uri.parse('http://coe.jujuy.gob.ar/covid19/start/tracking'));
    request.headers.set('content-type', 'application/json');
    request.add(utf8.encode(json.encode(item)));
    HttpClientResponse response = await request.close();
    print(response.statusCode);
    if (response.statusCode == 200) {
      String reply = await response.transform(utf8.decoder).join();
      httpClient.close();
      return reply;
    } else {
      String reply = await response.transform(utf8.decoder).join();
      return null;
    }
  }

  //
  void _mostrarDialogIngreseDatos(BuildContext context) {
    showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) {
          return AlertDialog(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20.0)),
            title: Center(
                child: Text(
              'Ingrese sus datos',
              style: TextStyle(fontSize: 15),
            )),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: <Widget>[
                TextField(
                  autofocus: true,
                  textAlign: TextAlign.left,
                  textCapitalization: TextCapitalization.sentences,
                  decoration: InputDecoration(
                    contentPadding: EdgeInsets.all(10),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(20.0)),
                    hintText: 'Ingrese DNI',
                    labelText: 'DNI',
                  ),
                  onChanged: (valor) {
                    setState(() {
                      _dniOperador = valor;
                    });
                  },
                ),
                Divider(),
                TextField(
                  obscureText: true,
                  decoration: InputDecoration(
                    contentPadding: EdgeInsets.all(10),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(20.0)),
                    hintText: 'Contraseña',
                    labelText: 'Contraseña',
                  ),
                  onChanged: (valor) {
                    setState(() {
                      _password = valor;
                    });
                  },
                ),
              ],
            ),
            actions: <Widget>[
              FlatButton(
                child: Text('Cancelar'),
                onPressed: () => Navigator.of(context).pop(),
              ),
              FlatButton(
                child: Text('Iniciar'),
                onPressed: () {
                  _getLatitudLongitud().then((v) {
                    apiRequestStartTracking();
                    startLocationService();
                  });
                  Navigator.of(context).pop();
                },
              )
            ],
          );
        });
  }
}

Future<bool> confirmPermissions(BuildContext context, GlobalKey<ScaffoldState> _scaffoldKey) {
  showDialog(
    context: context,
    child: AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24.0)),
      title: Column(
        children: <Widget>[
          Center(
            child: Text(
              'Para usar la app deberá tener la ubicación encendida y aceptar los permisos',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 22.0, fontFamily: 'Montserrat'),
            ),
          ),
          Center(
            child: Text(
              'Si usted bloqueó los permisos que requiere la aplicación, por favor habilitelos desde la configuracion de su dispostivo',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 18.0, fontFamily: 'Montserrat'),
            ),
          ),
        ],
      ),
      elevation: 7.0,
      actions: <Widget>[
        Row(
          children: <Widget>[
            FlatButton(
              child: Text(
                'Aceptar',
                style: TextStyle(color: Colors.blueAccent, fontWeight: FontWeight.bold, fontSize: 22.0, fontFamily: 'Montserrat'),
              ),
              onPressed: () async {
                await PermissionHandler().openAppSettings();
                Navigator.of(context).pop(true);
              },
            ),
            FlatButton(
              child: Text(
                'Cerrar',
                style: TextStyle(color: Colors.blueAccent, fontWeight: FontWeight.bold, fontSize: 22.0, fontFamily: 'Montserrat'),
              ),
              onPressed: () {
                //Navigator.of(context).pushNamed('/main');
                Navigator.of(context).pop(false);
              },
            ),
          ],
        )
      ],
    ),
  );
}

Future<bool> confirmGeolocalizationDialog(BuildContext context, GlobalKey<ScaffoldState> _scaffoldKey) {
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
                  '¿Acepta los términos y condiciones de uso?',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 22.0, fontFamily: 'Montserrat'),
                ),
              ),
              Center(
                child: Text(
                  'No podrá usar la aplicación si no los acepta',
                  style: TextStyle(fontSize: 18.0, fontFamily: 'Montserrat'),
                ),
              ),
              Container(
                height: 150,
                color: Colors.white,
                child: SingleChildScrollView(
                  child: Text(
                    mensajeDeTerminosYCondicionesDeUso,
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 10,
                      color: Colors.black.withOpacity(0.5),
                    ),
                  ),
                ),
              )
            ],
          ),
          elevation: 7.0,
          //backgroundColor: Colors.grey,
          actions: <Widget>[
            Row(
              children: <Widget>[
                FlatButton(
                  child: Text(
                    'Cancelar',
                    style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold, fontSize: 22.0, fontFamily: 'Montserrat'),
                  ),
                  onPressed: () {
                    Navigator.of(context).pop(false);
                  },
                ),
                //padding: EdgeInsets.only(right: 20.0),
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
            )
          ],
        );
      });
}

final mensajeDeTerminosYCondicionesDeUso = 'Términos y Condiciones: '
    'Los presentes términos y condiciones particulares (en adelante, los “Términos y Condiciones”) rigen la relación entre el Comité Operativo de Emergencia de la Provincia de Jujuy (en adelante, “COE”), la Secretaría de Modernización (en adelante, “Secretaría”) y los usuarios de la aplicación denominada “Covid2019 Jujuy“(en adelante, los “Usuarios”), versión para dispositivos móviles que podrá descargarse de las tiendas de aplicaciones oficiales de Android e iOS (en adelante, la'
    '“Aplicación”).'
    'El registro del Usuario en la Aplicación implica la aceptación inmediata y sin reserva de los presentes Términos y Condiciones, quedando entendido que en caso de contradicción prevalecerán estos Términos y Condiciones. En consecuencia, el Usuario manifiesta haber leído y aceptado en su totalidad los Términos y Condiciones; dicha aceptación es indispensable para la utilización de la Aplicación. Si no está de acuerdo con los presentes Términos y Condiciones será imposible utilizar la Aplicación.'
    '1. Descripción de la Aplicación'
    '1.1. La Aplicación es una herramienta tecnológica que brinda información sobre diversos temas referentes a los síntomas y/o prevención del virus COVID-19 con la finalidad de ayudar a prevenir la propagación del virus.'
    '1.2 La Aplicación permite realizar un cuestionario que determina la probabilidad de portar el virus COVID-19 (más comúnmente, llamado Coronavirus). Si el riesgo de portarlo es medio o alto, se activará un mensaje de alerta en la base de datos del Comité Operativo de Emergencia de la Provincia de Jujuy; y el personal del SAME se encargará de contactarte y mantenerte en seguimiento.'
    '1.3. La aplicación, en todo momento, lleva el registro de su geoposición con el fin de evitar la propagación exponencial del COVID-2019 y salvaguardar la integridad física y mental de los ciudadanos de la Provincia de Jujuy.'
    '1.4. La Aplicación también permite ingresar la temperatura y enviarla al sistema cuando lo considere oportuno. Automáticamente se actualizarán sus datos la Base de Datos del COE.'
    '2. Requisitos de uso de la Aplicación'
    '2.1. Podrán utilizar la Aplicación todas las personas humanas con capacidad legal para contratar y que residan en la Provincia de Jujuy.'
    '2.2. Para utilizar la Aplicación los Usuarios deberán registrarse siguiendo el procedimiento que se detalla en la Aplicación y aceptar los Términos y Condiciones.'
    '2.3. El Usuario declara y garantiza que todos los datos personales suministrados en el proceso de registro son verdaderos y completos.'
    '2.4. El COE utilizará la información suministrada por el Usuario exclusivamente con el objeto de permitir al Usuario utilizar la Aplicación.'
    '2.5. La utilización de la Aplicación es gratuita, lo que implica que no deberá pagar por ello ningún arancel o retribución.'
    '2.6. Para poder utilizar la Aplicación se requiere conexión a Internet. La libre descarga y la gratuidad del acceso no comprenden las facilidades de conexión a Internet. En ningún caso el COE proveerá a los Usuarios la conectividad necesaria para que puedan utilizar la Aplicación. La conectividad a Internet será por exclusiva cuenta y cargo de cada Usuario.'
    '2.7. El COE podrá rechazar o impedir, en cualquier momento, que un Usuario ingrese a la Aplicación siempre que tal ingreso pueda poner en riesgo la seguridad de la Aplicación y/o que el Usuario haya violado los Términos y Condiciones.'
    '3. Información contenida en la Aplicación'
    '3.1. El contenido y/o el uso de la Aplicación está orientada exclusivamente a informar y realizar seguimiento a todas las personas sobre el virus COVID-19, quedando aclarado que en ningún caso podrá interpretarse como que agota la información disponible.'
    '3.2. Las recomendaciones, lineamientos, sugerencias o guías que puedan encontrarse en la Aplicación no constituyen opinión médica ni deben utilizarse para realizar un diagnóstico ni iniciar un tratamiento médico sin la consulta de un profesional de la salud. La Aplicación no sustituye la opinión médica.'
    '4. Utilización de la Aplicación'
    '4.1. Los Usuarios deberán utilizar la Aplicación de conformidad con las disposiciones establecidas en estos Términos y Condiciones, con el ordenamiento jurídico vigente en la República Argentina, y según las pautas de conducta impuestas por la moral, las buenas costumbres y el debido respeto a los derechos de terceros.'
    '4.2. Queda prohibido el uso de la Aplicación con fines comerciales.'
    '4.3. Queda terminante prohibido: (i) copiar, modificar, adaptar, traducir, realizar ingeniería inversa, descompilar o desensamblar cualquier parte del contenido y/o de la Aplicación; (ii) hacer uso del contenido en otro sitio web o entorno informático para cualquier propósito sin la autorización previa y por escrito de la Secretaría; (iii) reproducir y/o comunicar por cualquier medio el contenido, dado que el acceso se otorga en forma personal y para uso exclusivo del Usuario; (iv) interferir'
    'o interrumpir el funcionamiento de la Aplicación; (v) vender, licenciar o explotar el contenido y/o cualquier tipo de acceso y/o uso de la Aplicación; (vi) utilizar la Aplicación con fines ilícitos o inmorales; e (vii) infringir de cualquier modo los presentes Términos y Condiciones.'
    '5. Protección de Datos Personales'
    '5.1. El COE cumple con lo establecido en la Ley 25.326 y normativa complementaria (en adelante, la “Normativa de Datos Personales”).'
    '5.2. El usuario presta su consentimiento expreso para que la Aplicación recolecte y procese información personal del usuario (Nombre Completo, DNI, Edad, Domicilio, geolocalización y otra información relevante), incluida información sensible referida a su salud (síntomas, antecedentes médicos, diagnóstico), con el fin de recomendarle pasos a seguir según su situación e instrucciones para ser atendido en la unidad de salud más cercana.'
    '5.4. La Aplicación es administrada por el Comité Operativo de Emergencia de la Provincia de Jujuy, con domicilio en Curupaiti 4600, San Salvador de Jujuy, Jujuy.'
    '6. Responsabilidad'
    '6.1. La Aplicación se licencia en forma gratuita a los Usuarios en el marco de las políticas excepcionales derivadas de la emergencia sanitaria declarada por el DNU 260/2020 y su utilización tiene como única finalidad coadyuvar a evitar la propagación del virus y mantener informada a la población. En consecuencia, el COE y la Secretaría, en ningún caso, será responsable por lucro cesante ni por cualquier consecuencia mediata y/o causal, pérdida de datos o información, pérdida de chance, daños'
    'punitivos ni de cualquier otra naturaleza derivadas del uso de la Aplicación.'
    '6.2. El COE y la Secretaría tampoco asume responsabilidad por ningún mal funcionamiento, imposibilidad de acceso o malas condiciones de uso de la Aplicación debido al uso de equipos inadecuados, interrupciones relacionadas con proveedores de servicio de internet, la saturación de la red de internet y/o por cualquier otra razón.'
    '7. Modificaciones de la Aplicación'
    'La Secretaría podrá introducir todos los cambios y modificaciones que estime convenientes en la Aplicación, lo que incluye, pero no se limita a agregar, alterar, sustituir o suprimir cualquier contenido de la Aplicación en todo momento.'
    '8. Propiedad Intelectual'
    '8.1. La Aplicación y el contenido de la Aplicación son de titularidad exclusiva de y/o la Secretaría de Modernización tiene la autorización correspondiente para su utilización y licenciamiento. A título meramente enunciativo, se entenderán incluidos las imágenes, fotografías, diseños, gráficos, sonidos, compilaciones de datos, marcas, nombres, títulos, designaciones, signos distintivos, y todo otro material accesible a través de la Aplicación.'
    '8.2. La Secretaría se reserva todos los derechos sobre la Aplicación y el contenido de la Aplicación, no cede ni transfiere a favor del Usuario ningún derecho sobre su propiedad intelectual.'
    '8.3. Los derechos de propiedad intelectual respecto de los criterios de selección y/o disposición del contenido en la Aplicación corresponden exclusivamente a la Secretaría, quedando estrictamente prohibido al Usuario utilizar los contenidos, las categorías y/o cualquier información de la Aplicación con otra finalidad distinta a la indicada en los presentes Términos y Condiciones.'
    '9. Operatividad de la Aplicación'
    '10.1. El COE y la Secretaría no garantiza el pleno acceso y operatividad de la Aplicación en forma ininterrumpida.'
    '10.2. La Secretaría y el COE podrán suspender el acceso a la Aplicación y/o a determinado contenido por motivos de mantenimiento o de seguridad en cualquier momento.'
    '10. Legislación aplicable y jurisdicción'
    '10.1. A todos los efectos legales en relación a la Aplicación, será aplicable la legislación vigente en la República Argentina.';
