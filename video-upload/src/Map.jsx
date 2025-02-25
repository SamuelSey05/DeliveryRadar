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

export default function Map() {
  let i;
  for (i = 0; i < 10; i++) {
    points.push([centre[0], centre[1] + 0.0001 * i, 0.0001]);
  }
  return <div className="map-container"><MapContainer center={ centre } zoom={20} style = { mapContainerStyle } scrollWheelZoom = {true}>
    <LayersControl style = {layersControlStyle}>
      <LayersControl.BaseLayer name="Base" checked style = {{layersControlStyle}}>
    <TileLayer
    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      url= "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" style = {{layersControlStyle}}>
    </TileLayer>
    </LayersControl.BaseLayer>
    <LayersControl.Overlay name="Heatmap" checked style = {{layersControlStyle}}>
      <HeatmapLayer fitBoundsOnLoad fitBoundsOnUpdate points={points} longitudeExtractor={m => m[1]} latitudeExtractor={m => m[0]} intensityExtractor={m => parseFloat(m[2])} style = {{layersControlStyle}}>

      </HeatmapLayer>
      
      
    </LayersControl.Overlay>
    </LayersControl>
  </MapContainer>
  </div>
}
