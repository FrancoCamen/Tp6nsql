// Inicializar el mapa
const map = L.map('map').setView([-34.6037, -58.3816], 3); // Centrado en Argentina, zoom 3
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

// Inicializar el cluster de marcadores
const markers = L.markerClusterGroup();
map.addLayer(markers);

// Obtener y mostrar todos los aeropuertos
fetch('http://127.0.0.1:8000/airports/')
    .then(response => response.json())
    .then(data => {
        data.airports.forEach(airport => {
            const lat = airport.lat;
            const lng = airport.lng;
            const marker = L.marker([lat, lng]);

            marker.bindPopup('Cargando...');
            marker.on('click', () => {
                fetch(`http://127.0.0.1:8000/airports/${airport.iata_faa}/`)
                    .then(response => response.json())
                    .then(data => {
                        const airportData = data.airport;
                        marker.setPopupContent(`
                            <b>${airportData.name}</b><br>
                            Ciudad: ${airportData.city}<br>
                            IATA: ${airportData.iata_faa || 'N/A'}<br>
                            ICAO: ${airportData.icao}<br>
                            Lat: ${airportData.lat}<br>
                            Lng: ${airportData.lng}<br>
                            Alt: ${airportData.alt} m<br>
                            Zona horaria: ${airportData.tz}
                        `);
                        marker.openPopup();
                    })
                    .catch(error => console.error('Error fetching airport details:', error));
            });

            markers.addLayer(marker);
        });
    })
    .catch(error => console.error('Error fetching airports:', error));