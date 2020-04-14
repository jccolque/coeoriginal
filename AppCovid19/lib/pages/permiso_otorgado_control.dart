import 'dart:convert';

import 'package:barcode_scan/barcode_scan.dart';
import 'package:covidjujuy_app/src/loader.dart';
import 'package:covidjujuy_app/src/model/qr_envio_model.dart';
import 'package:covidjujuy_app/src/model/respuesta_permiso_model.dart';
import 'package:covidjujuy_app/src/util/prevent_back.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:gps/gps.dart';
import 'package:http/http.dart' as http;

class PermisoOtorgadoControl extends StatefulWidget {
  @override
  _PermisoOtorgadoControlState createState() => _PermisoOtorgadoControlState();
}

///
/// Pantalla de permiso otorgado
/// @author JLopez
///
class _PermisoOtorgadoControlState extends State<PermisoOtorgadoControl> {
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

  @override
  Widget build(BuildContext context) {
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
        colors: [Colors.orange[400], Colors.deepOrange],
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
        Navigator.of(context).pushNamed('/permisootorgado');
      },
      tooltip: 'Volver',
      child: Icon(Icons.arrow_back),
    );
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
                        'Control de Permiso',
                        style: TextStyle(color: Colors.blue, fontSize: 30.0),
                      ),
//
                      SizedBox(
                        height: 30.0,
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
                      )
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
    final nombreCompleto = await prefs.getString('nombreCompletoOtorgadoControl');
    final dniOtorgado = await prefs.getString('dniOtorgadoControl');
    final domicilioCompleto = await prefs.getString('domicilioOtorgadoControl');
    final textoCompleto = await prefs.getString('textoOtorgadoControl');
    final controlOtorgado = await prefs.getBool('controlOtorgadoControl');
    final nombre = await prefs.getString('nombreGuardadoControl');
    final apellido = await prefs.getString('apellidoGuardadoControl');
    final domicilio = await prefs.getString('domicilioGuardadoControl');
    final barrio = await prefs.getString('barrioGuardadoControl');

    final imagen = await prefs.getString('imagenPerfilOtorgadaControl');
    final qr = await prefs.getString('qrOtorgadoControl');
    final fechaInicio = await prefs.getString('fechaInicioOtorgadoControl');
    final fechaFin = await prefs.getString('fechaFinOtorgadoControl');
    final horaInicio = await prefs.getString('horaInicioOtorgadoControl');
    final horaFin = await prefs.getString('horaFinOtorgadoControl');

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

}
