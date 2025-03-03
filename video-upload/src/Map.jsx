import {useState, useEffect} from 'react';
import "leaflet/dist/leaflet.css";
import { LayersControl, MapContainer, TileLayer} from "react-leaflet";
import HeatmapLayerFactory from "@vgrid/react-leaflet-heatmap-layer/cjs/HeatmapLayer";
//import Rcslider from "rc-slider";
import 'rc-slider/assets/index.css'

const HeatmapLayer = HeatmapLayerFactory();

const layersControlStyle = {position: "fixed", zIndex: "inherit"
};

const centre = [52.211, 0.092];

{/*isPortrait*/}
function Map( ) {

  const mapContainerStyle = {
    position: "absolute",
    top: "10px",
    bottom: "10px",
    left: "10px",
    right: "10px",
    display: "block",
    zIndex: 1000,
  };

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  {/*const [vehicleType, setVehicleType] = useState("all");

  const [time, setTime] = useState(0);

  const handleSliderChange = (t) => {
    setTime(t);
  }

  const convertMinutesToFormatted = (minutes) => {
    const hours = minutes/60;
    const mins = minutes%60;
    return String(hours) + ":" + String(mins);
  }*/}

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
  {/*<div style={{position: "absolute", bottom: "2%", left: "2%", right: "2%", margin: "800px", zIndex: 1000}}>
    <p>Selected time: {convertMinutesToFormatted(time)}</p>
  <Rcslider min={0} max={1440} step={15} value={time} onChange={handleSliderChange} 
  style={{position: "absolute", display: "flex",  zIndex: "inherit"}}></Rcslider>
  </div>*/}
  </div>
}

export default Map;