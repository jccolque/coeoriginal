var map;
var minimap;
var Marcas = [];
var mrkPadron;

$(document).ready(function(){
	iniciarGmap();
});

/* ******************* GOOGLE MAPS ******************* */
function defaultLatlng() {
	//Coordenadas por defecto en jujuy capital
	if ($('#latitud').val() == null && $('#longitud').val() == null) {
		return new google.maps.LatLng(-24.185790, -65.299490);
	} else {
		return new google.maps.LatLng($('#latitud').val(), $('#longitud').val());
	}
}

function iniciarGmap() {
	var minimapDiv = document.getElementById("minimap");
	var opcionesMapa = {
		zoom: 10,
		center: defaultLatlng(),
		styles: [{
			"featureType": "poi",
			"stylers": [{ "visibility": "off" }]
		},
		{
			"featureType": "poi.park",
			"stylers": [{ "visibility": "simplified" }]
		}
		],
		mapTypeId: google.maps.MapTypeId.ROADMAP
	};

	minimap = new google.maps.Map(minimapDiv, opcionesMapa);

	minimap.addListener('click', moveMarker);

	mrkPadron = new google.maps.Marker({
		map: minimap,
		position: defaultLatlng(),
		draggable: true,
		animation: google.maps.Animation.DROP,
		title: "",
	});

	mrkPadron.addListener('mousedown', function (mark) {
		originalPos = mark;
	});

	mrkPadron.addListener('mouseup', function (mark) {
		moveMarker(mark);
	});

	if ($('#padron').val() != "") { $('#padron').trigger('input'); }

}

var moveMarker = function (mark) {
	//console.log(mark);
	$('#frmPadron [name="latitud"]').val(mark.latLng.lat());
	$('#frmPadron [name="longitud"]').val(mark.latLng.lng());
	mrkPadron.setPosition(mark.latLng);
	mrkPadron.setMap(minimap);
}