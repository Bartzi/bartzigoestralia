
var map;

jQuery(document).ready(function(){

    // create the map
    var mapOptions = {
        center: new google.maps.LatLng(-29.270263, 152.361818),
        zoom: 5,
        mapTypeId: google.maps.MapTypeId.HYBRID
    };
    map = new google.maps.Map(document.getElementById('map_canvas'),
        mapOptions);

    // get all data from the server

    jQuery.get('/map/data',
        function(data, textStatus, jqXHR){
            data = JSON.parse(data);
            var points = data.points;
            createPoints(points);
            createLines(data.lines);
            var last_element = points[points.length - 1];
            //map.panTo(new google.maps.LatLng(last_element.latitude, last_element.longitude));
        });


});

function createPoints(points) {
    var infowindow = new google.maps.InfoWindow();

    jQuery(points).each(function(index, element){

        // create invisible object to determine the width of the label
        var helper = jQuery("<span>" + element.name + "</span>");
        helper.style = {display: "inline-block"};
        var body = jQuery('body');
        body.append(helper);
        var width = helper.width();
        helper.remove();



        var marker = new MarkerWithLabel({
            position: new google.maps.LatLng(element.latitude, element.longitude),
            map: map,
            labelContent: element.name,
            labelAnchor: new google.maps.Point((width - 5) / 2 , 60),
            labelClass: "label",

        });
        var contentString = '<div id="content">' +
            '<h1>' + element.name + '</h1>' +
            '<div class="flexbox">' + 
                '<div class="left-part flex-item"><b>Beschreibung:</b></div>' +
                '<div class="right-part flex-item">' + element.description + '</div>' +
            '</div>' +
            '<div class="flexbox">' + 
                '<div class="left-part flex-item"><b>Zeitpunkt:</b></div>' +
                '<div class="right-part flex-item">' + element.timestamp + '</div>' +
            '</div></div>';
        
        google.maps.event.addListener(marker, 'click', function(event) {
            infowindow.setContent(contentString);
            infowindow.open(map, marker);
        });
    });

}

function createLines(lines) {

    jQuery(lines).each(function(index, element){
        var line = new google.maps.Polyline({
            path: [
                new google.maps.LatLng(element.start_latitude, element.start_longitude),
                new google.maps.LatLng(element.end_latitude, element.end_longitude)],
            map: map,
            geodesic: true,
        });
    });

}