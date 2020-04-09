import 'package:flutter/material.dart';
import '../main.dart';
import 'codigoSeguridadCuenta.dart';

class RecuperarCuentaPage extends StatelessWidget{
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
        debugShowCheckedModeBanner: false,
        routes: <String, WidgetBuilder>{
        '/login': (BuildContext context) => MyApp(),
          '/codigodeseguridad': (BuildContext context) => CodigoSeguridadCuenta(),
        },
        home: MyRecuperarCuentaPage(),
    );
  }
}

class MyRecuperarCuentaPage extends StatefulWidget{
  @override
  _MyRecuperarCuentaPage createState() => _MyRecuperarCuentaPage();
}

class _MyRecuperarCuentaPage extends State<MyRecuperarCuentaPage>{
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
                      Text(
                        'Ingresá tu correo electrónico y/o DNI y se te enviará un mail con instrucciones para restablecer tu contraseña',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 16.0,
                        ),
                      ),
                      SizedBox(height: 20.0),
                      TextFormField(
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 20.0,
                        ),
                        decoration: const InputDecoration(
                            hintText: 'Ingrese su correo',
                            labelText: 'Correo',
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
                        keyboardType: TextInputType.number,
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 20.0,
                        ),
                        decoration: const InputDecoration(
                            hintText: 'Ingrese su DNI',
                            labelText: 'DNI',
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
                                          .pushNamed('/login');
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
                          )),
                      SizedBox(height: 20.0),
                      Container(
                        padding: EdgeInsets.only(top: 25.0),
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
                              Navigator.of(context)
                                  .pushNamed('/codigodeseguridad');
                            },
                            child: Text(
                              'Recibír mail',
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
                      SizedBox(height: 50.0),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: <Widget>[
                          Container(
                              child: Image.asset(
                                'assets/graphics/GA_logo.png',
                                height: 40,
                              )),
                          Container(
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
            ),
            ),
      ),
    );
  }

}