import { What3wordsMap } from "@what3words/react-components";
import { HeatmapLayer } from "@react-google-maps/api";
import { useRef, useState } from "react";
/*import {
  ConvertToCoordinatesClient,
  ConvertToCoordinatesOptions,
  LocationJsonResponse,
} from "@what3words/api";*/

const API_KEY = "Z1VKLOER";
const MAP_API_KEY = "AIzaSyCWylScZOqL0i7UXdqZJo1LIBYOwAFSnM4";

const sampleAddresses = [
  "chop.waddle.filed",
  "blown.plank.gurgled",
  "bounty.jets.pipes",
];

let sample3w = [];

/*const client: ConvertToCoordinatesClient =
  ConvertToCoordinatesClient.init(API_KEY);

const options: ConvertToCoordinatesOptions = { words: sampleAddresses[0] };
client
  .run({ ...options, format: "json" })
  .then((res: LocationJsonResponse) => sample3w.push(res));*/

export default function Map() {
  /*const handleCoordinatesChanged = () => {
    getGrid();
  }*/
  const useWhat3WordsMap = useRef(null);

  //const heatMapData = [new google.maps.LatLng(37.782, -122.485)];

  const overlayGrid = (map: any) => {
    const bounds = map.getBounds();
    const northEast = map.getNorthEast();
  };

  return (
    <What3wordsMap
      id="w3w-map"
      api_key={API_KEY}
      map_api_key={MAP_API_KEY}
      disable_default_ui={true}
      fullscreen_control={true}
      map_type_control={false}
      zoom_control={true}
      current_location_control_position={9}
      fullscreen_control_position={3}
      search_control_position={2}
      words="filled.count.soap"
    >
      <div slot="map" style={{ width: "100vw", height: "100vh" }} />
      <div slot="search-control" style={{ margin: "10px 0 0 10px" }}></div>
      <div slot="current-location-control" style={{ margin: "0 10px 10px 0" }}>
        <button>Current Location</button>
      </div>
      {/*<HeatmapLayer data={heatMapData}></HeatmapLayer>*/}
    </What3wordsMap>
  );
}
