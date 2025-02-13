import "leaflet/dist/leaflet.css";
import { LayersControl, MapContainer, TileLayer} from "react-leaflet";
//import Heatmap from "./Heatmap";

const mapContainerStyle = {
  width: "100vw",
  height: "100vh",
  display: "block",
  marginLeft: "auto",
  marginRight: "auto",
  marginTop: "auto",
  marginBottom: "auto"
};

const centre = [52.211, 0.092];

export default function Map() {
  return <div className="map-container"><MapContainer center={ centre } zoom={20} style = { mapContainerStyle } scrollWheelZoom = {true}>
    <LayersControl>
      <LayersControl.BaseLayer name="Base" checked>
    <TileLayer
    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      url= "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png">
    </TileLayer>
    </LayersControl.BaseLayer>
    <LayersControl.Overlay>
      
      
    </LayersControl.Overlay>
    </LayersControl>
  </MapContainer>;
  </div>
}
