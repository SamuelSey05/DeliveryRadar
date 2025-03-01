import {useState, useEffect} from 'react';
import "leaflet/dist/leaflet.css";
import { LayersControl, MapContainer, TileLayer} from "react-leaflet";
import HeatmapLayerFactory from "@vgrid/react-leaflet-heatmap-layer/cjs/HeatmapLayer";

const HeatmapLayer = HeatmapLayerFactory();

const mapContainerStyle = {
  position: "relative",
  width: "40vw",
  height: "80vh",
  display: "block",
  marginLeft: "auto",
  marginRight: "auto",
  marginTop: "auto",
  marginBottom: "auto",
  zIndex: 0,
};

const layersControlStyle = {position: "fixed", zIndex: "inherit"
};

const centre = [52.211, 0.092];

const points = []


function Map() {

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [vehicleType, setVehicleType] = useState("all");

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


  let i;
  for (i = 0; i < 10; i++) {
    points.push([{
      long: centre[0], 
      lat: centre[1] + 0.0001 * i,
      intensity: 0.0001}]);
  }

  if (loading) return <div>Data is loading, wait a sec...</div>;
  if (error) return <div>Error: {error.message}</div>;


  return <div className="map-container"><MapContainer center={ centre } zoom={20} style = { mapContainerStyle } scrollWheelZoom = {true}>
    <LayersControl style = {layersControlStyle}> {/* */}
      <LayersControl.BaseLayer name="Base" checked style = {{layersControlStyle}}>
    <TileLayer
    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      url= "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" style = {{layersControlStyle}}>
    </TileLayer>
    </LayersControl.BaseLayer>
    <LayersControl.Overlay name="Heatmap" checked style = {{layersControlStyle}}>
      <HeatmapLayer fitBoundsOnLoad fitBoundsOnUpdate points={{/*JSON.parse(data)*/points}} longitudeExtractor={m => m.long} latitudeExtractor={m => m.lat} intensityExtractor={m => parseFloat(m.intensity)} style = {{layersControlStyle}}>

      </HeatmapLayer>
      
      
    </LayersControl.Overlay>
    </LayersControl>
  </MapContainer>
  </div>
}

export default Map;