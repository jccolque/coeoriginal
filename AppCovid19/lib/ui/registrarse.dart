import 'package:covidjujuy_app/main.dart';
import 'package:flutter/material.dart';
import 'cuestionario.dart';

class RegistrarsePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      routes: <String, WidgetBuilder>{
        '/main': (BuildContext context) => MyApp(),
        '/cuestionario': (BuildContext context) => CuestionarioPage(),
      },
      home: MyRegistrarsePage(),
    );
  }
}

class MyRegistrarsePage extends StatefulWidget {
  @override
  _MyRegistrarsePageState createState() => _MyRegistrarsePageState();
}

class _MyRegistrarsePageState extends State<MyRegistrarsePage> {
  @override
  Widget build(BuildContext context) {
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
            width: MediaQuery
                .of(context)
                .size
                .width,
            child:
            Column(
              children: <Widget>[
                Container(
                    padding: EdgeInsets.fromLTRB(0.0, 80.0, 0.0, 0.0),
                    child: Center(
                      child: Image.asset(
                          'assets/graphics/Bandera.png'
                      ),
                    )
                ),
                Container(
                  child: Stack(
                    children: <Widget>[
                      Center(
                        child: Text(
                          'Registrarse',
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
                    ],
                  ),
                ),
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
                                borderSide: BorderSide(color: Colors.white)
                            )
                        ),
                        validator: (String value) {
                          return value.contains('@') ? 'Do not use the @ char.' : null;
                        },
                      ),
                      SizedBox(height: 20.0),
                      TextFormField(
                        keyboardType: TextInputType.number,
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 20.0,
                        ),
                        decoration: const InputDecoration(
                            hintText: 'Ingrese su dni',
                            labelText: 'DNI',
                            labelStyle: TextStyle(
                              fontFamily: 'Montserrat',
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                            focusedBorder: UnderlineInputBorder(
                                borderSide: BorderSide(color: Colors.white)
                            )
                        ),
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
                                borderSide: BorderSide(color: Colors.white)
                            )
                        ),
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
                            labelText: 'Re ingrese su contraseña',
                            labelStyle: TextStyle(
                              fontFamily: 'Montserrat',
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                            focusedBorder: UnderlineInputBorder(
                                borderSide: BorderSide(color: Colors.white)
                            )
                        ),
                      ),
                      SizedBox(height: 5.0),
                      Container(
                          child: Row(
                            children: <Widget>[
                              Container (
                                padding: EdgeInsets.only(top:20.0,),
                                child: InkWell(
                                    onTap: () {
                                      Navigator.of(context).pushNamed('/main');
                                    },
                                    child: Text(
                                      'Loguearse',
                                      style: TextStyle(
                                          color: Colors.white,
                                          fontSize: 18.0,
                                          fontWeight: FontWeight.bold,
                                          fontFamily: 'Montserrat',
                                          decoration: TextDecoration.underline),
                                    )),
                              ),
                            ],
                          )
                      ),
                      SizedBox(height: 40.0),
                      Container(
                        padding: EdgeInsets.only(top: 10.0),
                        child: Center(
                          child: RaisedButton(
                            padding: EdgeInsets.only(
                                top: 10.0, bottom: 10.0, left: 100.0, right: 100.0),
                            color: Colors.deepOrangeAccent,
                            splashColor: Colors.blueAccent,
                            elevation: 4,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(25.0),
                            ),
                            onPressed: () {
                              _handleCuentaCreadaDialog();
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
                      SizedBox(height: 10.0),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: <Widget>[
                          Container(
                              child: Image.asset(
                                'assets/graphics/GA_logo.png',
                                height: 40,
                              )
                          ),
                          Container(
                              child: Text(
                                '@GA_ide',
                                style: TextStyle(
                                    color: Colors.white
                                ),
                              )
                          ),
                        ],
                      ),
                      SizedBox(height: 10.0)
                    ],
                  ),
                ),
              ],
            )
        ),
      ),
    );
  }

  void _handleCuentaCreadaDialog() {
    cuentaCreadaDialog(context).then((bool value) {
      if (value) {
        Navigator.of(context).pushNamed('/cuestionario');
      }
    });
  }
}
Future<bool> cuentaCreadaDialog(BuildContext context) {
  return showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          shape:
          RoundedRectangleBorder(borderRadius: BorderRadius.circular(24.0)),
          title: Text(
            '¡Felicidades! su cuenta fue creada con exito',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.black,
            ),
          ),
          elevation: 7.0,
          //backgroundColor: Colors.grey,
          actions: <Widget>[
                Container(
                  padding: EdgeInsets.only(right: 75.0),
                  child: FlatButton(
                    child: Text(
                      'Aceptar',
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
                ),
          ],
        );
      });
}
