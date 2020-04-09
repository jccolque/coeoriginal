import 'package:covidjujuy_app/ui/recuperarCuenta.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'registrarse.dart';
import 'cuestionario.dart';
import 'recuperarCuenta.dart';
import 'home.dart';


class LoginPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      routes: <String, WidgetBuilder>{
        '/registrarse': (BuildContext context) => RegistrarsePage(),
        '/cuestionario': (BuildContext context) => CuestionarioPage(),
        '/recuperarcuenta': (BuildContext context ) => RecuperarCuentaPage(),
      },
      home: MyLoginPage(),
    );
  }
}

class MyLoginPage extends StatefulWidget {
  @override
  _MyLoginPageState createState() => _MyLoginPageState();
}

class _MyLoginPageState extends State<MyLoginPage> {
  @override
  Widget build(BuildContext context) {
    SystemChrome.setSystemUIOverlayStyle(SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
    ));
    return Scaffold(
      resizeToAvoidBottomInset: false,
      body: SingleChildScrollView(
        child: Container(
            decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.bottomCenter,
                  end: Alignment.topCenter,
                  colors: [Colors.blue[900], Colors.lightBlue],
                )),
            width: MediaQuery.of(context).size.width,
            child: Column(
              children: <Widget>[
                Container(
                    padding: EdgeInsets.fromLTRB(0.0, 80.0, 0.0, 0.0),
                    child: Center(
                      child: Image.asset('assets/graphics/Bandera.png'),
                    )),
                Container(
                  child: Stack(
                    children: <Widget>[
                      Center(
                        //padding: EdgeInsets.fromLTRB(15.0, 20.0, 0.0, 0.0),
                        child: Text(
                          'Cuestionario',
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
                      Container(
                        padding: EdgeInsets.fromLTRB(40.0, 80.0, 0.0, 0.0),
                        child: Text(
                          'COVID-19',
                          style: TextStyle(
                            fontSize: 35.0,
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
                      )
                    ],
                  ),
                ),
                // INPUTS
                Container(
                  padding: EdgeInsets.only(top: 20.0, left: 20.0, right: 20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: <Widget>[
                      TextFormField(
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 20.0,
                        ),
                        decoration: const InputDecoration(
                            hintText: 'Ingrese su correo electrónico',
                            labelText: 'Correo electrónico',
                            labelStyle: TextStyle(
                              fontFamily: 'Montserrat',
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                            focusedBorder: UnderlineInputBorder(
                                borderSide: BorderSide(color: Colors.white))),
                        validator: (String value) {
                          return value.contains('@')
                              ? 'Do not use the @ char.'
                              : null;
                        },
                      ),
                      SizedBox(height: 20.0),
                      TextFormField(
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 20.0,
                        ),
                        obscureText: true,
                        decoration: const InputDecoration(
                            hintText: 'Ingrese su contraseña',
                            labelText: 'Contraseña',
                            labelStyle: TextStyle(
                              fontFamily: 'Montserrat',
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                            focusedBorder: UnderlineInputBorder(
                                borderSide: BorderSide(color: Colors.white))),
                      ),
                      SizedBox(height: 5.0),
                      Container(
                          child: Row(
                            children: <Widget>[
                              Container(
                                padding: EdgeInsets.only(top: 20.0),
                                child: InkWell(
                                    onTap: () {
                                      Navigator.of(context)
                                          .pushNamed('/registrarse');
                                    },
                                    child: Text(
                                      'Registrarse',
                                      style: TextStyle(
                                          color: Colors.white,
                                          fontSize: 18.0,
                                          fontWeight: FontWeight.bold,
                                          fontFamily: 'Montserrat',
                                          decoration: TextDecoration.underline),
                                    )),
                              ),
                              Container(
                                alignment: Alignment(1.0, 0.0),
                                padding: EdgeInsets.only(top: 25.0, left: 50.0),
                                child: InkWell(
                                    onTap: () {
                                      Navigator.of(context).pushNamed('/recuperarcuenta');
                                    },
                                    child: Text(
                                      '¿Olvidó su contraseña?',
                                      style: TextStyle(
                                          color: Colors.lightGreenAccent,
                                          fontSize: 12.0,
                                          fontWeight: FontWeight.bold,
                                          fontFamily: 'Montserrat',
                                          decoration: TextDecoration.underline),
                                    )),
                              )
                            ],
                          )),
                      SizedBox(height: 40.0),
                      Container(
                        padding: EdgeInsets.only(top: 55.0),
                        child: Center(
                          child: RaisedButton(
                            padding: EdgeInsets.only(
                                top: 10.0,
                                bottom: 10.0,
                                left: 100.0,
                                right: 100.0),
                            color: Colors.deepOrangeAccent,
                            splashColor: Colors.blueAccent,
                            elevation: 4,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(25.0),
                            ),
                            onPressed: () {
                              _handleFirsGeoConfirmation();
                            },
                            child: Text(
                              'Ingresar ',
                              style: TextStyle(
                                  shadows: [
                                    Shadow(
                                      blurRadius: 10.0,
                                      color: Colors.black.withOpacity(0.4),
                                      offset: Offset(0.0, 3.0),
                                    ),
                                  ],
                                  color: Colors.white,
                                  fontSize: 22.0,
                                  fontWeight: FontWeight.bold,
                                  fontFamily: 'Montserrat'),
                            ),
                          ),
                        ),
                      ),
                      SizedBox(height: 15.0),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: <Widget>[
                          Container(
                              padding: EdgeInsets.only(top: 60.0),
                              child: Image.asset(
                                'assets/graphics/GA_logo.png',
                                height: 40,
                              )),
                          Container(
                              padding: EdgeInsets.only(top: 60.0),
                              child: Text(
                                '@GA_ide',
                                style: TextStyle(color: Colors.white),
                              )),
                        ],
                      ),
                      SizedBox(height: 10.0)
                    ],
                  ),
                ),
              ],
            )),
      ),
    );
  }

  void _handleFirsGeoConfirmation() {
    confirmGeolocalizationDialog(context).then((bool value) {
      if (value) {
        Navigator.of(context).pushNamed('/cuestionario');
      }
    });
  }
}

Future<bool> confirmGeolocalizationDialog(BuildContext context) {
  return showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          shape:
          RoundedRectangleBorder(borderRadius: BorderRadius.circular(24.0)),
          title: Text(
            'Si realmente desea usar la aplicación, permítanos conocer su ubicación',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.black,
            ),
          ),
          elevation: 7.0,
          //backgroundColor: Colors.grey,
          actions: <Widget>[
            Row(
              children: <Widget>[
                Container(
                  child: FlatButton(
                    child: Text(
                      'Cancelar',
                      style: TextStyle(
                        color: Colors.red,
                        fontWeight: FontWeight.bold,
                        fontSize: 25.0,
                      ),
                    ),
                    onPressed: () {
                      Navigator.of(context).pop(false);
                    },
                  ),
                ),
                Container(
                  padding: EdgeInsets.only(right: 20.0),
                  child: FlatButton(
                    child: Text(
                      'Permitir',
                      style: TextStyle(
                        color: Colors.green,
                        fontWeight: FontWeight.bold,
                        fontSize: 25.0,
                      ),
                    ),
                    onPressed: () {
                      Navigator.of(context).pop(true);
                    },
                  ),
                )
              ],
            )
          ],
        );
      });
}
