/*var mymap = L.map('mapid')//.setView([40.7530392755199 , -73.9934996106009], 12);
L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/streets-v10/tiles/256/{z}/{x}/{y}?access_token=[ACCESS_TOKEN]', {
	attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
	maxZoom: 18,
	accessToken: '[ACCESS_TOKEN]'
}).addTo(mymap);

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

latlongs = [[40.75303928,-73.99349961],[40.75303928,-73.99349961],[40.75303928,-73.99349961],[40.75303928,-73.99349961],[40.75303928,-73.99349961],[40.75303928,-73.99349961],[40.75303928,-73.99349961],[40.75316818,-73.99348298],[40.75328664,-73.99346769],[40.75463194,-73.9937774],[40.75464674,-73.99378616],[40.75463194,-73.993749],[40.75463194,-73.99420346],[40.75463194,-73.99330114],[40.75463194,-73.99329492],[40.75463194,-73.99329448],[40.75463194,-73.99329404],[40.75463194,-73.99329404],[40.75463194,-73.99329404],[40.75463194,-73.99329404],[40.75463194,-73.99329404],[40.75463194,-73.99329404],[40.75463194,-73.99329404],[40.75463194,-73.99329404],[40.75463194,-73.99329404],[40.75463194,-73.99374948],[40.75463194,-73.99374948],[40.75463194,-73.99374948],[40.75463194,-73.99385164],[40.69183001,-73.98584312],[40.69173645,-73.98625812],[40.6916709,-73.9862998],[40.69162911,-73.98632638],[40.69160247,-73.98634332],[40.69178687,-73.98581834],[40.69178569,-73.98582116]]


async function draw(){
	markers = [L.marker(latlongs[0])]

	for(var i = 0; i < latlongs.length-1; i++){
		markers[i+1] = L.marker(latlongs[i+1])
		var group = new L.featureGroup(markers);
		mymap.fitBounds(group.getBounds());
		await sleep(500)
		L.polygon([latlongs[i], latlongs[i+1]]).addTo(mymap);
	}
}

draw();*/





/*markers = []

for(var idx in latlongs){
	markers[idx] = L.marker(latlongs[idx])
}

var group = new L.featureGroup(markers);
mymap.fitBounds(group.getBounds());*/