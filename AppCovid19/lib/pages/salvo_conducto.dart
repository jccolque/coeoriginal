import 'dart:async';
import 'dart:convert';

import 'package:covidjujuy_app/src/bloc/provider.dart';
import 'package:covidjujuy_app/src/model/imagen_perfil_model.dart';
import 'package:covidjujuy_app/src/model/localidad_model.dart';
import 'package:covidjujuy_app/src/model/registro_avanzado_model.dart';
import 'package:covidjujuy_app/src/model/view_localidad_model.dart';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_typeahead/flutter_typeahead.dart';
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';

class SalvoConducto extends StatefulWidget {
  @override
  _SalvoConductoState createState() => _SalvoConductoState();
}

class _SalvoConductoState extends State<SalvoConducto> {
  File image;

  TextEditingController controller = TextEditingController();

  String _localidad;
  DateTime selectedDate = DateTime.now();
  final fechaController = TextEditingController();
  final aclaracionController = TextEditingController();
  final numeroController = TextEditingController();
  final calleController = TextEditingController();

  bool _separadoAislado = false;
  bool _imagenGuardada = false;

  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();
  final TextEditingController _typeAheadController = TextEditingController();

  @override
  Widget build(BuildContext context) {
      return Scaffold(
        appBar: AppBar(
          title: Text("Agregue su imagen de perfil"),
        ),
        body: Stack(
          children: <Widget>[
            _crearFondo( context ),
            _permisoForm( context ),
          ],
        ),
      );
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

  picker() async {
    print('Picker is called');
    File img = await ImagePicker.pickImage(source: ImageSource.camera);
//    File img = await ImagePicker.pickImage(source: ImageSource.gallery);
    if (img != null) {
      image = img;
      setState(() {});
    }
  }

  Widget cameraButton() {
    return RawMaterialButton(
      onPressed: () {
        picker();
      },
      child:  Icon(
        Icons.camera_enhance,
        color: Colors.blue,
        size: 35.0,
      ),
      shape:  CircleBorder(),
      elevation: 2.0,
      fillColor: Colors.white,
      padding: const EdgeInsets.all(15.0),
    );
  }

  Widget _imagenCapturada(BuildContext context) {
    final size = MediaQuery.of(context).size;
    return Container(
      width: size.width * 0.6,
      height: size.width * 0.6,
      margin: EdgeInsets.symmetric(vertical: 10.0),
      padding: EdgeInsets.symmetric(vertical: 10.0),
      decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(10.0),
          boxShadow: <BoxShadow> [
            BoxShadow(
                color: Colors.black26,
                blurRadius: 10.0,
                offset: Offset(0.0, 5.0),
                spreadRadius: 3.0
            )
          ]
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(20.0),
        child: Image.file(image),
      ),
    );
  }

  Widget _permisoForm(BuildContext context) {

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
                      image == null ? Icon(Icons.account_circle, color: Colors.blue, size: 100.0)
                          : _imagenCapturada( context ),
                      SizedBox(height: 10.0, width: double.infinity,),
//              Text('Juan Manuel Lopez', style: TextStyle(color: Colors.white, fontSize: 25.0),),

                    ],
                  ),
                ),
                cameraButton(),
                SizedBox(height: 10.0),
                _crearBoton(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _crearLocalidadAutocomplete(BuildContext context) {

    return Container(
      padding: EdgeInsets.symmetric(horizontal: 20.0),
      child: Container(
        child: Column(
          children: <Widget>[
            Text(
                ''
            ),
            TypeAheadFormField(
              textFieldConfiguration: TextFieldConfiguration(
                  controller: this._typeAheadController,
                  decoration: InputDecoration(
                      labelText: 'Localidad'
                  )
              ),
              suggestionsCallback: (pattern) {
                print(pattern);
                  return fetchPost(pattern);
              },
              itemBuilder: (context, suggestion) {
                return ListTile(
                  title: Text(suggestion),
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
      )
    );
  }

  Widget _crearCalle() {

    return Container(
      padding: EdgeInsets.symmetric(horizontal: 20.0),
      child: TextField(
        controller: calleController,
        decoration: InputDecoration(
            labelText: 'Calle',
        ),
//        onChanged: ( value ) => bloc.changePassword(value),
      ),
    );
  }

  Widget _crearNumero() {

    return Container(
      padding: EdgeInsets.symmetric(horizontal: 20.0),
      child: TextField(
        controller: numeroController,
        keyboardType: TextInputType.number,
        inputFormatters: [
          WhitelistingTextInputFormatter.digitsOnly
        ],
        decoration: InputDecoration(
//          icon: Icon(Icons.format_list_numbered, color: Colors.deepPurple,),
          labelText: 'Número',
        ),
//        onChanged: ( value ) => bloc.changePassword(value),
      ),
    );
  }

  Widget _crearAclaracion() {

    return Container(
      padding: EdgeInsets.symmetric(horizontal: 20.0),
      child: TextField(
        controller: aclaracionController,
        decoration: InputDecoration(
//          icon: Icon(Icons.format_list_numbered, color: Colors.deepPurple,),
          labelText: 'Aclaraciones',
        ),
//        onChanged: ( value ) => bloc.changePassword(value),
      ),
    );
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
                    borderRadius: BorderRadius.circular(30.0),
                  ),
                ),
              ),
            ),//
          ],
        ),
      ),
    );
  }

  Widget _crearSeparadoAislado() {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 50.0),
      child: Container(
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text("Separado/Aislamiento"),
            Checkbox(
              value: _separadoAislado,
              onChanged: (bool value) {
                setState(() {
                  _separadoAislado = value;
                });
              },
            ),
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
      });
  }

  Future<List<String>> fetchPost(String filtro) async {
    print('fetchPost');
    final response =
    await http.get('http://coe.jujuy.gob.ar/georef/localidad-autocomplete/?q=${filtro}');

    if (response.statusCode == 200) {
      // Si el servidor devuelve una repuesta OK, parseamos el JSON
      List<Result> list = LocalidadModel.fromJson(json.decode(response.body)).results;
      List<String> salida = List();
      list.forEach((text){
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
        _getDniFromSharedPref().then( (dni) {

          List<int> imageBytes = image.readAsBytesSync();
          print(imageBytes.toString());
          String base64Image = base64Encode(imageBytes);
          _setImageSharedPref(true);
          final form = ImagenPerfilModel(
              imagen: base64Image,
              dni: dni
          );
//          print(json.encode(form.toJson()));
        print(form.imagen);
        envioRegistroAvanzado(form);
        });
      },
    );
  }

  Future<int> _getDniFromSharedPref() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    final startupDniNumber = prefs.getInt('savedDniNumber');
    print('startupDniNumber');
    print(startupDniNumber);
    return startupDniNumber;
  }

  Future<String> envioRegistroAvanzado( ImagenPerfilModel imagenPerfilModel ) async {

    HttpClient httpClient = HttpClient();
    HttpClientRequest request = await httpClient.postUrl(Uri.parse('http://coe.jujuy.gob.ar/covid19/foto_perfil'));
    request.headers.set('content-type', 'application/json');
    request.add(utf8.encode(json.encode(imagenPerfilModel)));
    HttpClientResponse response = await request.close();
    print(response.statusCode);
    if(response.statusCode == 200){
      String reply = await response.transform(utf8.decoder).join();
      httpClient.close();
      setState(() {
        _imagenGuardada = true;
      });
      return reply;
    } else {
      return null;
    }
  }

  Future<bool> _setImageSharedPref(bool image) async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    return await prefs.setBool('imagenPerfil', image);
  }

}

