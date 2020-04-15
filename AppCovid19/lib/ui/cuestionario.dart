import 'package:flutter/material.dart';
import 'resultados.dart';
import 'package:back_button_interceptor/back_button_interceptor.dart';

class CuestionarioPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: MyCuestionarioPage(),
    );
  }
}

class MyCuestionarioPage extends StatefulWidget {
  @override
  _MyCuestionarioPageState createState() => _MyCuestionarioPageState();
}

class _MyCuestionarioPageState extends State<MyCuestionarioPage> {
  var preguntas = [
    '¿En los últimos 14 días estuvo fuera de la provincia de Jujuy?',
    '¿En los últimos 14 días ha estado en contacto con alguien al que se le haya diagnosticado o sea sospechoso de tener coronavirus?',
    '¿Tiene fiebre mayor a 38ºC?',
    '¿Tiene tos seca?',
    '¿Tiene dificultad para respirar?',
  ];
  var i = 0;
  var _respuestas = List<int>();


  @override
  void initState() {
    BackButtonInterceptor.add(myInterceptor);
  }


  @override
  void dispose() {
    BackButtonInterceptor.remove(myInterceptor);
    super.dispose();
  }

  bool myInterceptor(bool stopDefaultButtonEvent) {
    print("BACK BUTTON!"); // Do some stuff.
    return true;
  }

  @override
  Widget build(BuildContext context) {
    return WillPopScope(
      onWillPop: () async => false,
      child: Scaffold(
        resizeToAvoidBottomInset: false,
//      floatingActionButton: volver(context),
//      floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
        body: Container(
          child: Container(
              decoration: BoxDecoration(
                  gradient: LinearGradient(
                begin: Alignment.bottomCenter,
                end: Alignment.topCenter,
                colors: [Colors.blue[900], Colors.lightBlue],
              )),
            height: /*MediaQuery.of(context).orientation == Orientation.portrait
                ? MediaQuery.of(context).size.height
                : MediaQuery.of(context).size.width,*/
            MediaQuery.of(context).size.height,
            child: SafeArea(
              child: SingleChildScrollView(
              child: Column(
                children: <Widget>[
                  SizedBox(height: 20.0),
                  Center(
                      child: Text(
                        'Responda todas las preguntas',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                            color: Colors.white,
                            fontSize: 22.0,
                            fontWeight: FontWeight.bold,
                            fontFamily: 'Montserrat'),
                      ),
                    ),
                  Column(
                    children: <Widget>[
                      Container(
                        padding: EdgeInsets.only(left: 20.0, top: 20.0, right: 20.0),
                        child: Center(
                          child: Text(
                            i < preguntas.length? preguntas[i]:'',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                                color: Colors.white,
                                fontSize: 30.0,
                                fontWeight: FontWeight.bold,
                                fontFamily: 'Montserrat'),
                          ),
                        ),
                      ),
                      Center(
                        child: Column(
                          children: <Widget>[
                            SizedBox(height: 20.0),
                            Container(
                              width: MediaQuery.of(context).size.width/2,
                              child: RaisedButton(
                                color: Colors.lightGreen,
                                splashColor: Colors.blueAccent,
                                elevation: 4,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(24.0),
                                ),
                                onPressed: () {
                                  if (i < preguntas.length) {
                                    setState(() {
                                      _respuestas.add(1);
                                      ++i;
                                    });
                                    if(i == preguntas.length){
                                      setState(() {
                                        _respuestas.add(0);
                                      });
                                      var route = MaterialPageRoute(
                                        builder: (BuildContext context) =>
                                            ResultadosPage(data: _respuestas),
                                      );
                                      Navigator.of(context).push(route);
                                    }
                                  }
                                },
                                child: Text(
                                  'SI',
                                  textAlign: TextAlign.center,
                                  style: TextStyle(
                                      color: Colors.white,
                                      fontSize: 100.0,
                                      fontWeight: FontWeight.bold,
                                      fontFamily: 'Montserrat'),
                                ),
                              ),
                            ),
                            SizedBox(height: 20.0),
                            Container(
                              width: MediaQuery.of(context).size.width/2,
                              child: RaisedButton(
                                color: Colors.red,
                                splashColor: Colors.blueAccent,
                                elevation: 4,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(24.0),
                                ),
                                onPressed: () {
                                  if (i < preguntas.length) {
                                    setState(() {
                                      _respuestas.add(0);
                                      ++i;
                                    });
                                    if(i == preguntas.length){
                                      setState(() {
                                        _respuestas.add(0);
                                      });
                                      var route = MaterialPageRoute(
                                        builder: (BuildContext context) =>
                                            ResultadosPage(data: _respuestas),
                                      );
                                      Navigator.of(context).push(route);
                                    }
                                  }
                                },
                                child: Text(
                                  'NO',
                                  textAlign: TextAlign.center,
                                  style: TextStyle(
                                      color: Colors.white,
                                      fontSize: 100.0,
                                      fontWeight: FontWeight.bold,
                                      fontFamily: 'Montserrat'),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 50.0),
                  /*Row(
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
                  )*/
                ],
              ),),
            ),
          )),
        ),
    );
  }

  Widget volver(BuildContext context) {
    return FloatingActionButton(
      backgroundColor: Colors.blue,
      onPressed: () {
        Navigator.of(context).pushNamed('/main');
      },
      tooltip: 'Volver',
      child: Icon(Icons.arrow_back),

    );
  }
}
