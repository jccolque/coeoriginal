import 'dart:convert';
import 'dart:io';

import 'package:covidjujuy_app/src/loader.dart';
import 'package:covidjujuy_app/src/model/permiso_error_model.dart';
import 'package:covidjujuy_app/src/model/permiso_model.dart';
import 'package:covidjujuy_app/src/model/respuesta_permiso_model.dart';
import 'package:covidjujuy_app/src/model/solicitud_permiso_model.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:fluttertoast/fluttertoast.dart';

class SolicitarPermiso extends StatefulWidget {
  @override
  _SolicitarPermisoState createState() => _SolicitarPermisoState();
}

class _SolicitarPermisoState extends State<SolicitarPermiso> {

  String _permisoSeleccionado;
  List<DropdownMenuItem<String>> _dropDownMenuItems;
  DateTime selectedDate = DateTime.now();
  TimeOfDay selectedTime;
  DateTime date3;
  bool loading = true;
  int _dni;
  final fechaController = TextEditingController();
  final horaController = TextEditingController();

  @override
  void initState() {
    print('initState');
    getPermisos().then((permiso){
      List<DropdownMenuItem<String>> items = new List();
      for (Permiso city in permiso) {
        items.add(new DropdownMenuItem(
            value: city.id,
            child: new Text(city.descripcion)
        ));
      }
      setState(() {
        _dropDownMenuItems = items;
        _permisoSeleccionado = _dropDownMenuItems[0].value;
        loading = false;
      });
    });

    _getDniFromSharedPref().then((dni) {
      setState(() {
        _dni = dni;
      });
    });
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title:  Text("Solicitud de Permiso"),
      ),
      body: Stack(
        children: <Widget>[
          _crearFondo( context ),
          _seleccionPermiso(context),
        ],
      ),
    );
  }

  Widget loader() {
    if(loading == true ){
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

  Widget _crearFondo(BuildContext context) {

    final size = MediaQuery.of(context).size;

    final fondoGradient =  Container(
      height: double.infinity,
      width: double.infinity,
      decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.bottomCenter,
            end: Alignment.topCenter,
            colors: [Colors.blue[900], Colors.lightBlue],
          )
      ),
    );

    final circulo = Container(
      width: 100.0,
      height: 100.0,
      decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(100.0),
          color: Color.fromRGBO(255, 255, 255, 0.05)
      ),
    );

    return Stack(
      children: <Widget>[
        fondoGradient,
        Positioned( top: 90.0, left: 30.0, child: circulo),
        Positioned( top: -40.0, left: -30.0, child: circulo),
        Positioned( bottom: -50.0, right: -10.0, child: circulo),
        Positioned( bottom: 120.0, right: 20.0, child: circulo),
        Positioned( bottom: -50.0, left: -20.0, child: circulo)
      ],
    );
  }

  Widget _seleccionPermiso(BuildContext context) {
    final size = MediaQuery.of(context).size;
    return SingleChildScrollView(
      child: Column(
        children: <Widget>[
          SafeArea(
            child: Container(
            ),
          ),
          Container(
            width: size.width * 0.85,
            margin: EdgeInsets.symmetric(vertical: 30.0),
            padding: EdgeInsets.symmetric(vertical: 20.0),
            decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(5.0),
                boxShadow: <BoxShadow> [
                  BoxShadow(
                      color: Colors.black26,
                      blurRadius: 3.0,
                      offset: Offset(0.0, 5.0),
                      spreadRadius: 3.0
                  )
                ]
            ),
            child: Column(
              children: <Widget>[
                Container(
                  padding: EdgeInsets.only(top: 10.0),
                  child: Column(
                    children: <Widget>[
                      loader(),
                      Text('Elija tipo de permiso', style: TextStyle(color: Colors.grey, fontSize: 20.0),),
                      SizedBox(height: 10.0, width: double.infinity,),
                      DropdownButton(
                        value: _permisoSeleccionado,
                        items: _dropDownMenuItems,
                        onChanged: changedDropDownItem,
                      ),
                      SizedBox(height: 10.0, width: double.infinity,),
                      _crearFecha(),
                      SizedBox(height: 10.0, width: double.infinity,),
                      _crearBoton(),
                      SizedBox(height: 10.0, width: double.infinity,),
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

  void changedDropDownItem(String permiso) {
    print(permiso);
    setState(() {
      _permisoSeleccionado = permiso;
    });
  }

  Future<List<Permiso>> getPermisos() async {
    print('fetchPost');
    final response =
    await http.get('http://coe.jujuy.gob.ar/covid19/tipo_permisos');

    if (response.statusCode == 200) {
      // Si el servidor devuelve una repuesta OK, parseamos el JSON
      PermisoModel list = PermisoModel.fromJson(json.decode(response.body));
      print(response);
      return list.permisos;
    } else {
      // Si esta respuesta no fue OK, lanza un error.
      throw Exception('Failed to load post');
    }
  }

  Widget _crearBoton( ) {

    return RaisedButton(
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: 80.0, vertical: 15.0),
        child: Text('Enviar'),
      ),
      shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(5.0)
      ),
      elevation: 0.0,
      color: Colors.lightBlue,
      textColor: Colors.white,
      onPressed: (){
        print(_dni);
        print(fechaController.text);
        print(_permisoSeleccionado);
        DateFormat dateFormat = DateFormat("yyyyMMdd");
        DateFormat timeFormat = DateFormat("HHmm");
        final dt = DateTime(selectedDate.year, selectedDate.month, selectedDate.day, selectedTime.hour, selectedTime.minute);
        final time = timeFormat.format(dt);

        final permiso = SolicitudPermisoModel(
          dni_individuo: _dni.toString(),
          fechaIdeal: dateFormat.format(selectedDate),
          horaIdeal: time,
          tipoPermiso: _permisoSeleccionado
        );
        envioSolicitudPermiso(permiso);
      },
    );
  }

  Future<RespuestaPermisoModel> envioSolicitudPermiso( SolicitudPermisoModel solicitudPermisoModel ) async {
    final response =
    await http.post('http://coe.jujuy.gob.ar/covid19/salvoconducto', body: (utf8.encode(json.encode(solicitudPermisoModel))));

    if (response.statusCode == 200) {
      // Si el servidor devuelve una repuesta OK, parseamos el JSON
      RespuestaPermisoModel permisoOtorgado = RespuestaPermisoModel.fromJson(json.decode(response.body));
      print(json.encode(permisoOtorgado));
      print(permisoOtorgado.imagen);
      print(permisoOtorgado.qr);
      showLongToast(permisoOtorgado.texto);
      await _setPermisoSharedPref(true);
      await _setPermisoOtorgadoSharedPref(permisoOtorgado);
      return permisoOtorgado;
    } else {
      // Si esta respuesta no fue OK, lanza un error.
      PermisoErrorModel permisoErrorModel = PermisoErrorModel.fromJson(json.decode(response.body));
      print(permisoErrorModel.error);
      showLongErrorToast(permisoErrorModel.error);
      await _setPermisoSharedPref(false);
//      throw Exception('Failed to load post');
    }
  }

  Widget _crearFecha() {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 20.0),
      child: Container(
        child: Row(
          mainAxisSize: MainAxisSize.max,
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Expanded(
              flex: 3,
              child: Container(
                child: TextField(
                  controller: fechaController,
                  enabled: false,
                ),
              ),
            ),
            Expanded(
              flex: 1,
              child: Container(
                child: RaisedButton(
                  textColor: Colors.white,
                  color: Theme.of(context).primaryColor,
                  child: Icon(Icons.calendar_today),
                  onPressed: () =>  _selectDate(context),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(50.0),
                  ),
                ),
              ),
            ),//
          ],
        ),
      ),
    );
  }

  Future<Null> _selectDate(BuildContext context) async {
    DateFormat dateFormat = DateFormat("dd/MM/yyyy");
    DateTime now = DateTime.now();
    String formattedDate = dateFormat.format(now);
    DateTime dateTime = dateFormat.parse(formattedDate);
    final DateTime picked = await showDatePicker(
        context: context,
        initialDate: selectedDate,
        firstDate: dateTime,
        lastDate: DateTime(2023));
    if (picked != null && picked != selectedDate)
      setState(() {
        selectedDate = picked;
        fechaController.text = dateFormat.format(selectedDate);
        _selectTime(context);
      });
  }

  Future<void> _selectTime(BuildContext context) async {
    DateFormat dateFormat = DateFormat("dd/MM/yyyy HH:mm");
    final TimeOfDay picked = await showTimePicker(
        context: context,
        initialTime: TimeOfDay.now());
    if (picked != null && picked != selectedTime)
      setState(() {
        selectedTime = picked;
        final dt = DateTime(selectedDate.year, selectedDate.month, selectedDate.day, selectedTime.hour, selectedTime.minute);
        final format = dateFormat.format(dt);
        fechaController.text = format;
      });
  }

  Future<int> _getDniFromSharedPref() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    final startupDniNumber = prefs.getInt('savedDniNumber');
    print('startupDniNumber');
    print(startupDniNumber);
    return startupDniNumber;
  }

  Future<void> _setPermisoSharedPref(bool permiso) async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    return await prefs.setBool('permisoOtorgado', permiso);
  }

  Future<void> _setPermisoOtorgadoSharedPref(RespuestaPermisoModel permisoOtorgado) async {
    DateFormat dateFormat = DateFormat("dd/MM/yyyy");
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setString('imagenPerfilOtorgada', permisoOtorgado.imagen);
    await prefs.setString('qrOtorgado', permisoOtorgado.qr);
    await prefs.setString('fechaOtorgado', dateFormat.format(permisoOtorgado.fecha));
    await prefs.setString('horaInicioOtorgado', permisoOtorgado.horaInicio);
    await prefs.setString('horaFinOtorgado', permisoOtorgado.horaFin);
    await prefs.setString('textoOtorgado', permisoOtorgado.texto);
  }

  void showLongToast(String mensaje) {
    Fluttertoast.showToast(
      msg: mensaje,
      toastLength: Toast.LENGTH_LONG,
        backgroundColor: Colors.green,
        textColor: Colors.white
    );
  }

  void showLongErrorToast(String mensaje) {
    Fluttertoast.showToast(
      msg: mensaje,
      toastLength: Toast.LENGTH_LONG,
      backgroundColor: Colors.red,
      textColor: Colors.white
    );
  }
}
