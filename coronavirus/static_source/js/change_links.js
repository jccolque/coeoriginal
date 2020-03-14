function changelinks(eleccion_id) {
    var links, i;
    links = document.getElementsByClassName("btn_link");
    for (i = 0; i < links.length; i++) {
    links[i].href = '/' + links[i].href.split(["/"])[3] + '/' + eleccion_id
  }
}