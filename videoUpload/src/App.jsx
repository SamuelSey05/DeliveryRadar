import { useState, useEffect } from "react";
import UploadModal from "./UploadModal";
import "./App.css";
import Map from "./Map"; /**Imports all necessary libraries. */

function App() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [isPortrait, setIsPortrait] = useState(
    window.matchMedia("(orientation: portrait)").matches
  );

  /**Hooks for whether the Upload Menu is open, and for whether the screen is portrait-oriented, respectively. */

  useEffect(() => {
    const handleOrientationChange = (e) => {
      setIsPortrait(e.matches);
    };

    window
      .matchMedia("(orientation: portrait)")
      .addEventListener("change", handleOrientationChange);
  }, []);
  /** This will enable a change in site format if the screen orientation changes
   *i.e. if the site is on a phone, which is rotated 90 degrees.*/

  return (
    <div className={isPortrait ? "columnC" : "rowC"}>
      {" "}
      {/**Relative display of the two containers depending on orientation. */}
      <div
        className="app-container dark-theme"
        style={{
          zIndex: 1000,
          left: "5%",
          right: isPortrait ? "5%" : "55%",
          top: isPortrait ? "55%" : "5%",
          bottom: "5%",
        }}
      >
        {/**This stores the upload menu, which is at the bottom for a portrait screen, and the left for a landscape. */}
        <h1 className="app-title">Video Upload Portal</h1>
        <button
          className="upload-button"
          onClick={() => setIsModalOpen(true)}
          style={{ height: "72px" }}
        >
          Upload Video {/**Opens the upload modal if clicked */}
        </button>
        {isModalOpen && <UploadModal onClose={() => setIsModalOpen(false)} />}
        {/**Displays the upload modal if open */}
      </div>
      <div
        className="app-container dark-theme"
        style={{
          zIndex: 1000,
          left: isPortrait ? "5%" : "55%",
          right: "5%",
          top: "5%",
          bottom: isPortrait ? "55%" : "5%",
        }}
      >
        <h1 className="app-title">Heat Map</h1>
        {/**This stores the heatmap, which is at the top for a portrait screen, and the right for a landscape. */}
        <Map></Map>
        {/**Displays the Heatmap component at all times */}
      </div>
    </div>
  );
}

export default App;
