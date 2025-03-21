import { useState, useEffect } from "react";
import "leaflet/dist/leaflet.css";
import { LayersControl, MapContainer, TileLayer, useMap } from "react-leaflet";
import HeatmapLayerFactory from "@vgrid/react-leaflet-heatmap-layer/cjs/HeatmapLayer";
/*imports of all necessary packages*/

const layersControlStyle = { position: "fixed", zIndex: "inherit" };

function Map() {
  const HeatmapLayer = HeatmapLayerFactory();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] =
    useState(null); /*hooks, which define various aspect of the map's state*/

  const centre = [52.205, 0.119];
  const zoom = useState(13)[0];

  const mapContainerStyle = {
    position: "absolute",
    top: "10px",
    bottom: "10px",
    left: "10px",
    right: "10px",
    display: "block",
    zIndex: 1000,
  }; /*styling of the layers and map*/

  useEffect(() => {
    fetch("https://cstdeliveryradar.soc.srcf.net/heatmap-data")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Heatmap data is unavailable for some reason.");
        }
        return response.json();
      })
      .then((data) => {
        setData(data);
        setLoading(false);
      })
      .catch((error) => {
        setError(error);
        setLoading(false);
      });
  }, []);
  /* A HTTP GET request to the database, with error handling and an initial state.
   *This handler, on a successful request, will receive a series of JSON objects,
   * convert them to JavaScript without a call to JSON.parse, and store them in the list "data" */

  function MapTester() {
    const map = useMap();

    useEffect(() => {
      map.setView(centre, zoom);
    }, []); //Keeps the map's focus on Cambridge
  }

  if (loading) return <div>Data is loading, wait a sec...</div>;
  if (error)
    return <div>Error: {error.message}</div>; /* Returns in case of an error */

  return (
    <div className="map-container">
      <MapContainer
        center={centre}
        zoom={zoom}
        style={mapContainerStyle}
        scrollWheelZoom={true}
      >
        <LayersControl style={layersControlStyle}>
          {/*These objects are imported. The map uses one layer on another. */}
          <LayersControl.BaseLayer
            name="Base"
            checked
            style={layersControlStyle}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              style={{ layersControlStyle }}
            >
              {/*The "TileLayer" is the actual map - this is requested as needed from the Leaflet Server, and displayed. */}
            </TileLayer>
          </LayersControl.BaseLayer>
          <LayersControl.Overlay
            name="Heatmap"
            checked
            style={layersControlStyle}
          >
            <HeatmapLayer
              fitBoundsOnLoad
              fitBoundsOnUpdate
              points={data}
              longitudeExtractor={(m) => m.location.lon}
              latitudeExtractor={(m) => m.location.lat}
              intensityExtractor={(m) => m.speed / 3}
              style={{ layersControlStyle }}
              blur={5}
              radius={10}
            >
              {/*The "HeatMapLayer" takes the objects requested and stored in "data", 
      and extracts the relevant information from each object in the list. */}
            </HeatmapLayer>
          </LayersControl.Overlay>
        </LayersControl>
        <MapTester />
      </MapContainer>
    </div>
  );
}

export default Map;
