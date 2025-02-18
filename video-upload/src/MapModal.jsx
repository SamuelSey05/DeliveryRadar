import { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './MapModal.css';

// Fix default marker icon issue
import markerIconPng from 'leaflet/dist/images/marker-icon.png';
import markerShadowPng from 'leaflet/dist/images/marker-shadow.png';

const customMarkerIcon = new L.Icon({
  iconUrl: markerIconPng,
  shadowUrl: markerShadowPng,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

function LocationMarker({ position, setPosition }) {
  useMapEvents({
    click(e) {
      setPosition(e.latlng);
    },
  });

  return position === null ? null : (
    <Marker
      position={position}
      icon={customMarkerIcon}
      draggable={true}
      eventHandlers={{
        dragend(e) {
          setPosition(e.target.getLatLng());
        },
      }}
    >
      <Popup>
        Selected Location: <br /> {position.lat.toFixed(5)}, {position.lng.toFixed(5)}
      </Popup>
    </Marker>
  );
}

function MapModal({ onConfirm, onClose }) {
  const [position, setPosition] = useState(null);

  const handleConfirm = () => {
    if (position) {
      onConfirm(position);
    } else {
      alert('Please select a location first!');
    }
  };

  return (
    <div className="map-modal-overlay">
      <div className="map-modal">
        <div className="map-container">
          <MapContainer
            center={[52.205, 0.119]}
            zoom={13}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />
            <LocationMarker position={position} setPosition={setPosition} />
          </MapContainer>
        </div>
        <div className="map-controls">
          <button onClick={handleConfirm} className="confirm-button">
            Confirm Location
          </button>
          <button onClick={onClose} className="close-button">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default MapModal;