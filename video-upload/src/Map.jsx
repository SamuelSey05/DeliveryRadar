import {useState, useEffect} from 'react';
import "leaflet/dist/leaflet.css";
import { LayersControl, MapContainer, TileLayer} from "react-leaflet";
import HeatmapLayerFactory from "@vgrid/react-leaflet-heatmap-layer/cjs/HeatmapLayer";

const HeatmapLayer = HeatmapLayerFactory();

const layersControlStyle = {position: "fixed", zIndex: "inherit"
};

const centre = [52.211, 0.092];


function Map( {isPortrait}) {

  const mapContainerStyle = {
    position: "absolute",
    top: "2%",
    bottom: "2%",
    left: "2%",
    width: isPortrait ? "330px" :"400px",
    display: "flex",
    zIndex: 1000,
  };

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [vehicleType, setVehicleType] = useState("all");

  const [time, setTime] = useState(NaN);

  useEffect(() => {
    fetch('https://cstdeliveryradar.soc.srcf.net/heatmap-data')
      .then(response => {
        if(!response.ok) {
          throw new Error("Heatmap data is unavailable for some reason.");
        }
        return response.json();
      })
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(error => {
        setError(error);
        setLoading(false);
      })

  }, []);

  if (loading) return <div>Data is loading, wait a sec...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return <div className="map-container">
    <MapContainer center={ centre } zoom={20} style = { mapContainerStyle } scrollWheelZoom = {true}>
      <LayersControl style = {layersControlStyle}>
        <LayersControl.BaseLayer name="Base" checked style = {layersControlStyle}>
          <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      url= "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" style = {{layersControlStyle}}>
    </TileLayer>
    </LayersControl.BaseLayer>
    <LayersControl.Overlay name="Heatmap" checked style = {layersControlStyle}>
      <HeatmapLayer fitBoundsOnLoad fitBoundsOnUpdate points={data} longitudeExtractor={m => m.location.lon} latitudeExtractor={m => m.location.lat} intensityExtractor={m => m.speed} style = {{layersControlStyle}} blur = {5}>

      </HeatmapLayer>
      
      
    </LayersControl.Overlay>
    </LayersControl>
  </MapContainer>
  </div>
}

export default Map;