import 'package:flutter/material.dart';

class PreventBackRoute extends MaterialPageRoute {
  PreventBackRoute() : super(builder: (context) => PreventBack());
}

class PreventBack extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return WillPopScope(
      child: Scaffold(
        appBar: AppBar(
          title: Text('Page 2'),
        ),
        body: Center(
          child: Text('PAGE 2'),
        ),
      ),
      onWillPop: () {
        print('BAAAACKKKKKK');
        return Future(() => false);
      },
    );
  }
}