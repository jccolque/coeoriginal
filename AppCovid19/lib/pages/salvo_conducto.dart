import 'dart:async';
import 'dart:convert';

import 'package:covidjujuy_app/src/loader.dart';
import 'package:covidjujuy_app/src/model/imagen_perfil_model.dart';
import 'package:covidjujuy_app/src/model/localidad_model.dart';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class SalvoConducto extends StatefulWidget {
  @override
  _SalvoConductoState createState() => _SalvoConductoState();
}

///
/// Pantalla inicial de salvoconducto
/// @author JLopez
///
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
  bool loading = false;

  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();
  final TextEditingController _typeAheadController = TextEditingController();

  @override
  Widget build(BuildContext context) {
      return WillPopScope(
        onWillPop: () => Future.value(false),
        child: Scaffold(
          floatingActionButton: volver(),
          floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
          appBar: AppBar(
            title: Text("Agregue su imagen de perfil"),
          ),
          body: Stack(
            children: <Widget>[
              _crearFondo( context ),
              _permisoForm( context ),
            ],
          ),
        ),
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
    if (img != null && img.path != null) {
      if (img != null) {
        setState(() {
          image = img;
        });
      }
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
                Visibility(
                  visible: !loading,
                  child: _crearBoton(),
                ),

                Visibility(
                  visible: loading,
                  child: loader(),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Future<List<String>> getLocalidadByFiltro(String filtro) async {
    print('getLocalidadByFiltro');
    final response = await http.get('http://coe.jujuy.gob.ar/georef/localidad-autocomplete/?q=${filtro}');

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
          print(form.imagen);
          envioRegistroAvanzado(form).then((val) {
            Navigator.of(context).pushNamed('/main');
          });
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
    setState(() {
      loading = true;
    });
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
        loading = false;
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

}

