import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

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
  String _imagen;
  String _qr;
  String _fecha;
  String _horaInicio;
  String _horaFin;
  String _texto;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      floatingActionButton: volver(),
      floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
      body: Stack(
        children: <Widget>[
          _crearFondo(context),
          _permisoCard(context),
        ],
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
        colors: [Colors.blue[900], Colors.lightBlue],
      )),
    );

    final circulo = Container(
      width: 100.0,
      height: 100.0,
      decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(100.0),
          color: Color.fromRGBO(255, 255, 255, 0.05)),
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
                boxShadow: <BoxShadow>[
                  BoxShadow(
                      color: Colors.black26,
                      blurRadius: 3.0,
                      offset: Offset(0.0, 5.0),
                      spreadRadius: 3.0)
                ]),
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
    final nombre = await prefs.getString('nombreGuardado');
    final apellido = await prefs.getString('apellidoGuardado');
    final domicilio = await prefs.getString('domicilioGuardado');
    final barrio = await prefs.getString('barrioGuardado');

    final imagen = await prefs.getString('imagenPerfilOtorgada');
    final qr = await prefs.getString('qrOtorgado');
    final fecha = await prefs.getString('fechaOtorgado');
    final horaInicio = await prefs.getString('horaInicioOtorgado');
    final horaFin = await prefs.getString('horaFinOtorgado');
    final texto = await prefs.getString('textoOtorgado');

    setState(() {
      _nombreController.text = 'Juan Manuel';
      _apellidoController.text = 'Lopez';
      _imagen = '/archivos/informacion/individuos/3159055_GJFxe5s.jpg';
      _qr = '/archivos/informacion/individuos/qrcode-31590550.png';
//      _fecha = fecha;
//      _horaInicio = horaInicio;
//      _horaFin = horaFin;
//      _texto = texto;
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
                placeholder: NetworkImage('http://coe.jujuy.gob.ar${_imagen}'),
                fit: BoxFit.cover,
              ),
            ),
            Expanded(
              flex: 1,
              child: FadeInImage(
                image: NetworkImage('http://coe.jujuy.gob.ar${_qr}'),
                placeholder: NetworkImage('http://coe.jujuy.gob.ar${_qr}'),
                fit: BoxFit.cover,
              ),
            )
          ],
        ));
  }

  Widget _crearNombreApellido(BuildContext context) {
    return Container(
        padding: EdgeInsets.symmetric(horizontal: 20.0),
        child: Column(
          mainAxisSize: MainAxisSize.max,
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            TextField(
              controller: _nombreController,
              enabled: false,
            ),
            TextField(
              controller: _apellidoController,
              enabled: false,
            ),
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
            Text('Domicilio: '),
            Text('Barrio: '),
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
            Text('Permiso valido: '),
            Text('Desde: '),
            Text('Hasta: '),
          ],
        ));
  }
}
