import 'dart:async';
import 'dart:convert';

import 'package:covidjujuy_app/src/bloc/provider.dart';
import 'package:covidjujuy_app/src/model/localidad_model.dart';
import 'package:covidjujuy_app/src/model/view_localidad_model.dart';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import 'package:http/http.dart' as http;

import 'package:flutter_typeahead/flutter_typeahead.dart';

class SalvoConducto extends StatefulWidget {
  @override
  _SalvoConductoState createState() => _SalvoConductoState();
}

class _SalvoConductoState extends State<SalvoConducto> {
  File image;

  TextEditingController controller = TextEditingController();
  String _selectedCity;
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();
  final TextEditingController _typeAheadController = TextEditingController();

  void _loadData() async {
    await ViewLocalidadModel.loadPlayers();
  }

  @override
  Widget build(BuildContext context) {

    return Scaffold(
      body: Stack(
        children: <Widget>[
          _crearFondo( context ),
          _loginForm( context ) ,
        ],
      ),
      floatingActionButton: cameraButton(),
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
        Positioned( bottom: -50.0, left: -20.0, child: circulo),

        Container(
          padding: EdgeInsets.only(top: 30.0),
          child: Column(
            children: <Widget>[
              image == null ? Icon(Icons.account_circle, color: Colors.white, size: 100.0)
              : _imagenCapturada( context ),
              SizedBox(height: 10.0, width: double.infinity,),
//              Text('Juan Manuel Lopez', style: TextStyle(color: Colors.white, fontSize: 25.0),),

            ],
          ),
        )
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
        Icons.camera_front,
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
      width: size.width * 0.4,
      height: size.width * 0.4,
      margin: EdgeInsets.symmetric(vertical: 5.0),
      padding: EdgeInsets.symmetric(vertical: 5.0),
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
      child: ClipRRect(
        borderRadius: BorderRadius.circular(50.0),
        child: Image.file(image),
      ),
    );
  }

  Widget _loginForm(BuildContext context) {

//    final bloc = Provider.of(context);

    final size = MediaQuery.of(context).size;

    return SingleChildScrollView(
      child: Column(
        children: <Widget>[
          SafeArea(
            child: Container(
              height: 180.0,
            ),
          ),

          Container(
            width: size.width * 0.85,
            margin: EdgeInsets.symmetric(vertical: 30.0),
            padding: EdgeInsets.symmetric(vertical: 50.0),
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
                Text('Ingreso', style: TextStyle(fontSize: 20.0),),
                SizedBox(height: 60.0),
                _crearLocalidadAutocomplete( context ),
                SizedBox(height: 30.0),
//                _crearPassword( bloc ),
                SizedBox(height: 30.0),
//                _crearBoton( bloc ),
              ],
            ),
          ),
          SizedBox(height: 100.0)
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
                'What is your favorite city?'
            ),
            TypeAheadFormField(
              textFieldConfiguration: TextFieldConfiguration(
                  controller: this._typeAheadController,
                  decoration: InputDecoration(
                      labelText: 'City'
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
                this._typeAheadController.text = suggestion;
              },
              validator: (value) {
                if (value.isEmpty) {
                  return 'Please select a city';
                }
              },
              onSaved: (value) => this._selectedCity = value,
            ),
            SizedBox(height: 10.0,),
            RaisedButton(
              child: Text('Submit'),
              onPressed: () {
                if (this._formKey.currentState.validate()) {
                  this._formKey.currentState.save();
                  Scaffold.of(context).showSnackBar(SnackBar(
                      content: Text('Your Favorite City is ${this._selectedCity}')
                  ));
                }
              },
            )
          ],
        ),
      )
    );
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
}

