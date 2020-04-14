import 'dart:convert';

import 'package:barcode_scan/barcode_scan.dart';
import 'package:covidjujuy_app/src/loader.dart';
import 'package:covidjujuy_app/src/model/qr_envio_model.dart';
import 'package:covidjujuy_app/src/model/respuesta_permiso_model.dart';
import 'package:covidjujuy_app/src/util/prevent_back.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:gps/gps.dart';
import 'package:http/http.dart' as http;

class PermisoOtorgado extends StatefulWidget {
  @override
  _PermisoOtorgadoState createState() => _PermisoOtorgadoState();
}

///
/// Pantalla de permiso otorgado
/// @author JLopez
///
class _PermisoOtorgadoState extends State<PermisoOtorgado> {
  final _nombreController = TextEditingController();
  final _apellidoController = TextEditingController();
  final _domicilioController = TextEditingController();
  String _nombreCompleto;
  String _domicilioCompleto;
  String _textoCompleto;
  bool _controlOtorgado;
  String _dni;
  String _imagen;
  String _qr;
  String _fechaInicio;
  String _fechaFin;
  String _horaInicio;
  String _horaFin;
  int _currentIndex = 0;

  bool loading = false;

  @override
  Widget build(BuildContext context) {
    if(_controlOtorgado == true){
      return WillPopScope(
        onWillPop: () => Future.value(false),
        child: Scaffold(
          body: Stack(
            children: <Widget>[
              _crearFondo(context),
              _permisoCard(context),
              Positioned(
                left: 0,
                right: 0,
                bottom: 0,
                child: bottomNavigationBar,
              ),
            ],
          ),
        ),
      );
    } else {
      return WillPopScope(
        onWillPop: () => Future.value(false),
        child: Scaffold(
          floatingActionButton: volver(),
          floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
          body: Stack(
            children: <Widget>[
              _crearFondo(context),
              _permisoCard(context),
            ],
          ),
        ),
      );
    }
  }

  Widget get bottomNavigationBar {
    return ClipRRect(
      borderRadius: BorderRadius.only(
        topRight: Radius.circular(40),
        topLeft: Radius.circular(40),
      ),
      child: BottomNavigationBar(
        onTap: onTabTapped,
        currentIndex: _currentIndex,
        backgroundColor: Colors.lightBlue,
        items: [
          BottomNavigationBarItem(icon: Icon(Icons.camera_alt), title: Text('QR')),
          BottomNavigationBarItem(icon: Icon(Icons.arrow_back), title: Text('Volver')),
        ],
        unselectedItemColor: Colors.white,
        selectedItemColor: Colors.white,
        showUnselectedLabels: true,
      ),
    );
  }

  void onTabTapped(int index) {
    print(index);
    if (index == 1) {
      Navigator.of(context).pushNamed('/main');
    }
    if (index == 0) {
      _scanQR();
    }
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  void initState() {
    _getPermisoSharedPref().then((val) {
      print('cargo todo');
    });
  }

  Widget _crearFondo(BuildContext context) {
    final size = MediaQuery.of(context).size;

    final fondoGradient = Container(
      height: double.infinity,
      width: double.infinity,
      decoration: BoxDecoration(
          gradient: LinearGradient(
        begin: Alignment.bottomCenter,
        end: Alignment.topCenter,
        colors: [Colors.blue[900], Colors.lightBlue],
      )),
    );

    final circulo = Container(
      width: 100.0,
      height: 100.0,
      decoration: BoxDecoration(borderRadius: BorderRadius.circular(100.0), color: Color.fromRGBO(255, 255, 255, 0.05)),
    );

    return Stack(
      children: <Widget>[
        fondoGradient,
        Positioned(top: 90.0, left: 30.0, child: circulo),
        Positioned(top: -40.0, left: -30.0, child: circulo),
        Positioned(bottom: -50.0, right: -10.0, child: circulo),
        Positioned(bottom: 120.0, right: 20.0, child: circulo),
        Positioned(bottom: -50.0, left: -20.0, child: circulo)
      ],
    );
  }

  Widget volver() {
    return FloatingActionButton(
      backgroundColor: Colors.blue,
      onPressed: () {
        Navigator.of(context).pushNamed('/main');
      },
      tooltip: 'Volver',
      child: Icon(Icons.arrow_back),
    );
  }

  _scanQR() async {
    String futureString;

    try {
      futureString = await BarcodeScanner.scan();
      print('Codigo escaneado');
      print(futureString);
      await Gps.currentGps().then((coor) {
        setState(() {
          loading = true;
        });
        final qr =
            QrEnvioModel(qrCode: futureString, dniOperador: _dni.toString(), latitud: double.parse(coor.lat), longitud: double.parse(coor.lng));
        _getDatosPorQr(qr).then((resp){
          if(resp != null){
            _setPermisoOtorgadoSharedPref(resp).then((v){
              Navigator.of(context).pushNamed('/permisootorgadocontrol');
            });
          }
        });
      });
    } catch (e) {
      futureString = e.toString();
    }
  }

  Future<RespuestaPermisoModel> _getDatosPorQr(QrEnvioModel qrEnvioModel) async {
    print('envioSolicitudPermiso');
    print(json.encode(qrEnvioModel));
    final response = await http.post('http://coe.jujuy.gob.ar/covid19/control/salvoconducto', body: (utf8.encode(json.encode(qrEnvioModel))));

    if (response.statusCode == 200) {
      // Si el servidor devuelve una repuesta OK, parseamos el JSON
      RespuestaPermisoModel permisoOtorgado = RespuestaPermisoModel.fromJson(json.decode(response.body));
      print(json.encode(permisoOtorgado));
      print(permisoOtorgado.imagen);
      print(permisoOtorgado.qr);
      setState(() {
        loading = false;
      });

      return permisoOtorgado;
    } else {
      setState(() {
        loading = false;
      });
      // Si esta respuesta no fue OK, lanza un error.
//      throw Exception('Failed to load post');
      return null;
    }
  }

  Widget _permisoCard(BuildContext context) {
    final size = MediaQuery.of(context).size;
    return SingleChildScrollView(
      child: Column(
        children: <Widget>[
          SafeArea(
            child: Container(),
          ),
          Container(
            width: size.width * 0.9,
            margin: EdgeInsets.symmetric(vertical: 10.0),
            padding: EdgeInsets.symmetric(vertical: 20.0),
            decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(5.0),
                boxShadow: <BoxShadow>[BoxShadow(color: Colors.black26, blurRadius: 3.0, offset: Offset(0.0, 5.0), spreadRadius: 3.0)]),
            child: Column(
              children: <Widget>[
                Container(
                  padding: EdgeInsets.only(top: 10.0),
                  child: Column(
                    children: <Widget>[
//                      loader(),
                      Text(
                        'Permiso Otorgado',
                        style: TextStyle(color: Colors.green, fontSize: 20.0),
                      ),
//
                      SizedBox(
                        height: 10.0,
                        width: double.infinity,
                      ),
                      _crearImagen(context),
                      SizedBox(
                        height: 10.0,
                        width: double.infinity,
                      ),
                      _crearNombreApellido(context),
                      SizedBox(
                        height: 10.0,
                        width: double.infinity,
                      ),
                      _crearDomicilio(context),
                      SizedBox(
                        height: 10.0,
                        width: double.infinity,
                      ),
                      _crearValidez(context),
                      SizedBox(
                        height: 10.0,
                        width: double.infinity,
                      ),
                      loader()
                    ],
                  ),
                ),
              ],
            ),
          )
        ],
      ),
    );
  }

  Future<bool> _getPermisoSharedPref() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    final nombreCompleto = await prefs.getString('nombreCompletoOtorgado');
    final dniOtorgado = await prefs.getString('dniOtorgado');
    final domicilioCompleto = await prefs.getString('domicilioOtorgado');
    final textoCompleto = await prefs.getString('textoOtorgado');
    final controlOtorgado = await prefs.getBool('controlOtorgado');
    final nombre = await prefs.getString('nombreGuardado');
    final apellido = await prefs.getString('apellidoGuardado');
    final domicilio = await prefs.getString('domicilioGuardado');
    final barrio = await prefs.getString('barrioGuardado');

    final imagen = await prefs.getString('imagenPerfilOtorgada');
    final qr = await prefs.getString('qrOtorgado');
    final fechaInicio = await prefs.getString('fechaInicioOtorgado');
    final fechaFin = await prefs.getString('fechaFinOtorgado');
    final horaInicio = await prefs.getString('horaInicioOtorgado');
    final horaFin = await prefs.getString('horaFinOtorgado');
    final texto = await prefs.getString('textoOtorgado');

    setState(() {
      _nombreCompleto = nombreCompleto;
      _dni = dniOtorgado;
      _domicilioCompleto =domicilioCompleto;
      _textoCompleto = textoCompleto;
      _controlOtorgado = controlOtorgado;
      _nombreController.text = nombre;
      _apellidoController.text = apellido;
      _domicilioController.text = domicilio;
      _imagen = imagen;
      _qr = qr;
      _fechaInicio = fechaInicio;
      _fechaFin = fechaFin;
      _horaInicio = horaInicio.substring(0, 5);
      _horaFin = horaFin.substring(0, 5);
    });

    return true;
  }

  Widget _crearImagen(BuildContext context) {
    return Container(
        padding: EdgeInsets.symmetric(horizontal: 20.0),
        child: Row(
          mainAxisSize: MainAxisSize.max,
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Expanded(
              flex: 1,
              child: FadeInImage(
                image: NetworkImage('http://coe.jujuy.gob.ar${_imagen}'),
                placeholder: AssetImage('assets/graphics/no-image.jpg'),
                fit: BoxFit.cover,
              ),
            ),
            Expanded(
              flex: 1,
              child: FadeInImage(
                image: NetworkImage('http://coe.jujuy.gob.ar${_qr}'),
                placeholder: AssetImage('assets/graphics/no-image.jpg'),
                fit: BoxFit.cover,
              ),
            )
          ],
        ));
  }

  Widget _crearNombreApellido(BuildContext context) {
    return Container(
        padding: EdgeInsets.symmetric(horizontal: 20.0, vertical: 10),
        child: Column(
          mainAxisSize: MainAxisSize.max,
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
          Text(_nombreCompleto, style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),),
            SizedBox(height: 10,),
            Text(_dni),
            Text(_textoCompleto),
          ],
        ));
  }

  Widget _crearDomicilio(BuildContext context) {
    final size = MediaQuery.of(context).size;
    return Container(
        width: size.width,
        padding: EdgeInsets.symmetric(horizontal: 20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Text('Domicilio: ${_domicilioCompleto}'),
//            Text('Barrio: '),
          ],
        ));
  }

  Widget _crearValidez(BuildContext context) {
    final size = MediaQuery.of(context).size;
    return Container(
        width: size.width,
        padding: EdgeInsets.symmetric(horizontal: 20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Text('Permiso valido:'),
            Text('Desde:  ${_fechaInicio} - ${_horaInicio}'),
            Text('Hasta:  ${_fechaFin} - ${_horaFin}'),
          ],
        ));
  }

  Widget loader() {
    if (loading == true) {
      return Container(
        child: Loader(
          color1: Colors.blue,
          color2: Colors.yellow,
          color3: Colors.green,
        ),
      );
    } else {
      return Container();
    }
  }

  Future<void> _setPermisoOtorgadoSharedPref(RespuestaPermisoModel permisoOtorgado) async {
    DateFormat dateFormat = DateFormat("dd/MM/yyyy");
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setString('nombreCompletoOtorgadoControl', permisoOtorgado.nombreCompleto);
    await prefs.setString('dniOtorgadoControl', permisoOtorgado.dniIndividuo);
    await prefs.setString('domicilioOtorgadoControl', permisoOtorgado.domicilio);
    await prefs.setString('textoOtorgadoControl', permisoOtorgado.texto);
    await prefs.setBool('controlOtorgadoControl', permisoOtorgado.control);
    await prefs.setString('imagenPerfilOtorgadaControl', permisoOtorgado.imagen);
    await prefs.setString('qrOtorgadoControl', permisoOtorgado.qr);
    await prefs.setString('fechaInicioOtorgadoControl', dateFormat.format(permisoOtorgado.fechaInicio));
    await prefs.setString('fechaFinOtorgadoControl', dateFormat.format(permisoOtorgado.fechaFin));
    await prefs.setString('horaInicioOtorgadoControl', permisoOtorgado.horaInicio);
    await prefs.setString('horaFinOtorgadoControl', permisoOtorgado.horaFin);
    await prefs.setString('textoOtorgadoControl', permisoOtorgado.texto);
  }
}
