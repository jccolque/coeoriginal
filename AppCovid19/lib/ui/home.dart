import 'package:covidjujuy_app/ui/recuperarCuenta.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class HomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
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
                          'COVID-19',
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
                        padding: EdgeInsets.fromLTRB(70.0, 80.0, 0.0, 0.0),
                        child: Text(
                          'Jujuy',
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
                      ),
                    ],
                  ),
                ),
                SizedBox(height: 40.0),
                Container(
                  padding: EdgeInsets.only(left: 20.0, right: 20.0),
                  child: Text(
                      'Toda la información aquí provista, está avalada por el Comando Operativo de Emergencia de Jujuy',
                      textAlign: TextAlign.center,
                    style: TextStyle(
                        color: Colors.white,
                      ),
                  ),
                ),
                SizedBox(height: 40.0),
                Container(
                  padding: EdgeInsets.only(left: 20.0, right: 20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      Container(
                        width: MediaQuery.of(context).size.width,
                        height: 30.0,
                        decoration: BoxDecoration(
                          color: Colors.blueAccent,
                          borderRadius: BorderRadius.only(topLeft: Radius.circular(20.0), topRight: Radius.circular(20.0)),
                        ),
                        child: Text(
                          'Consejos',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                              color: Colors.white,
                              fontSize: 18.0),
                        ),
                      ),
                      Container(
                        height: 50.0,
                        width: MediaQuery.of(context).size.width,
                        color: Colors.black,
                        child: RaisedButton(
                          color: Colors.white,
                          splashColor: Colors.blueAccent,

                          onPressed: () {},
                          child: Text(
                            'Limpiar la casa',
                            style: TextStyle(
                                color: Colors.black,
                                fontSize: 18.0,
                                fontFamily: 'Montserrat'),
                          ),
                        ),
                      ),
                      Container(
                        height: 50.0,
                        width: MediaQuery.of(context).size.width,
                        color: Colors.black,
                        child: RaisedButton(
                          color: Colors.white,
                          splashColor: Colors.blueAccent,

                          onPressed: () {},
                          child: Text(
                            'Comprar alimentos',
                            style: TextStyle(
                                color: Colors.black,
                                fontSize: 18.0,
                                fontFamily: 'Montserrat'),
                          ),
                        ),
                      ),
                      Container(
                        height: 50.0,
                        width: MediaQuery.of(context).size.width,
                        color: Colors.black,
                        child: RaisedButton(
                          color: Colors.white,
                          splashColor: Colors.blueAccent,

                          onPressed: () {},
                          child: Text(
                            'Cuidar a los mayores',
                            style: TextStyle(
                                color: Colors.black,
                                fontSize: 18.0,
                                fontFamily: 'Montserrat'),
                          ),
                        ),
                      ),
                      Container(
                        height: 50.0,
                        width: MediaQuery.of(context).size.width,
                        color: Colors.black,
                        child: RaisedButton(
                          color: Colors.white,
                          splashColor: Colors.blueAccent,

                          onPressed: () {},
                          child: Text(
                            'Sobrellevar la cuarentena',
                            style: TextStyle(
                                color: Colors.black,
                                fontSize: 18.0,
                                fontFamily: 'Montserrat'),
                          ),
                        ),
                      ),
                      Container(
                        height: 20.0,
                        decoration: BoxDecoration(
                          color: Colors.blueAccent,
                          borderRadius: BorderRadius.only(bottomLeft: Radius.circular(20.0), bottomRight: Radius.circular(20.0)),
                        ),
                      )
                    ],
                  ),
                ),
                SizedBox(height: 40.0),
                Container(
                  padding: EdgeInsets.only(left: 20.0, right: 20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      Container(
                        width: MediaQuery.of(context).size.width,
                        height: 30.0,
                        decoration: BoxDecoration(
                          color: Colors.blueAccent,
                          borderRadius: BorderRadius.only(topLeft: Radius.circular(20.0), topRight: Radius.circular(20.0)),
                        ),
                        child: Text(
                          'Contactos importantes',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                              color: Colors.white,
                              fontSize: 18.0),
                        ),
                      ),
                      Container(
                        height: 50.0,
                        width: MediaQuery.of(context).size.width,
                        color: Colors.black,
                        child: RaisedButton(
                          color: Colors.white,
                          splashColor: Colors.blueAccent,

                          onPressed: () {},
                          child: Text(
                            'Comando operativo de emergencia',
                            style: TextStyle(
                                color: Colors.black,
                                fontSize: 18.0,
                                fontFamily: 'Montserrat'),
                          ),
                        ),
                      ),
                      Container(
                        height: 50.0,
                        width: MediaQuery.of(context).size.width,
                        color: Colors.black,
                        child: RaisedButton(
                          color: Colors.white,
                          splashColor: Colors.blueAccent,

                          onPressed: () {},
                          child: Text(
                            'Urgencias 107',
                            style: TextStyle(
                                color: Colors.black,
                                fontSize: 18.0,
                                fontFamily: 'Montserrat'),
                          ),
                        ),
                      ),
                      Container(
                        height: 50.0,
                        width: MediaQuery.of(context).size.width,
                        color: Colors.black,
                        child: RaisedButton(
                          color: Colors.white,
                          splashColor: Colors.blueAccent,

                          onPressed: () {},
                          child: Text(
                            'Denuncias 911',
                            style: TextStyle(
                                color: Colors.black,
                                fontSize: 18.0,
                                fontFamily: 'Montserrat'),
                          ),
                        ),
                      ),
                      Container(
                        height: 20.0,
                        decoration: BoxDecoration(
                          color: Colors.blueAccent,
                          borderRadius: BorderRadius.only(bottomLeft: Radius.circular(20.0), bottomRight: Radius.circular(20.0)),
                        ),
                      )
                    ],
                  ),
                ),
                SizedBox(height: 40.0),
                Container(
                  padding: EdgeInsets.only(left: 20.0, right: 20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      Container(
                        width: MediaQuery.of(context).size.width,
                        height: 30.0,
                        decoration: BoxDecoration(
                          color: Colors.blueAccent,
                          borderRadius: BorderRadius.only(topLeft: Radius.circular(20.0), topRight: Radius.circular(20.0)),
                        ),
                        child: Text(
                          'Medidades del gobierno nacional',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                              color: Colors.white,
                              fontSize: 18.0),
                        ),
                      ),
                      Container(
                        height: 50.0,
                        width: MediaQuery.of(context).size.width,
                        color: Colors.black,
                        child: RaisedButton(
                          color: Colors.white,
                          splashColor: Colors.blueAccent,

                          onPressed: () {},
                          child: Text(
                            '*Cuarentena hasta el 31 de Marzo',
                            style: TextStyle(
                                color: Colors.black,
                                fontSize: 18.0,
                                fontFamily: 'Montserrat'),
                          ),
                        ),
                      ),
                      Container(
                        height: 50.0,
                        width: MediaQuery.of(context).size.width,
                        color: Colors.black,
                        child: RaisedButton(
                          color: Colors.white,
                          splashColor: Colors.blueAccent,

                          onPressed: () {},
                          child: Text(
                            '*Cierre de fronteras',
                            style: TextStyle(
                                color: Colors.black,
                                fontSize: 18.0,
                                fontFamily: 'Montserrat'),
                          ),
                        ),
                      ),
                      Container(
                        height: 50.0,
                        width: MediaQuery.of(context).size.width,
                        color: Colors.black,
                        child: RaisedButton(
                          color: Colors.white,
                          splashColor: Colors.blueAccent,

                          onPressed: () {},
                          child: Text(
                            '*Aplicación Test COVID-19',
                            style: TextStyle(
                                color: Colors.black,
                                fontSize: 18.0,
                                fontFamily: 'Montserrat'),
                          ),
                        ),
                      ),
                      Container(
                        height: 20.0,
                        decoration: BoxDecoration(
                          color: Colors.blueAccent,
                          borderRadius: BorderRadius.only(bottomLeft: Radius.circular(20.0), bottomRight: Radius.circular(20.0)),
                        ),
                      )
                    ],
                  ),
                ),
                SizedBox(height: 40.0),
              ],
            )),
      ),
    );
  }
}
