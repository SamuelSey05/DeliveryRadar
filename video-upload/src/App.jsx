import { useState, useEffect } from "react";
import UploadModal from "./UploadModal";
import "./App.css";
import Map from "./Map";

function App() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [isPortrait, setIsPortrait] = useState(window.matchMedia("(orientation: portrait)").matches);

  useEffect(() => {
    const handleOrientationChange = (e) => {
      setIsPortrait(e.matches);
    };

    window.matchMedia("(orientation: portrait)").addEventListener('change', handleOrientationChange);
  }, []);

  return (
    <div className={isPortrait ? "columnC" : "rowC"}>
    <div className="app-container dark-theme" style={{zIndex: 1000, left: "5%", right: (isPortrait? "5%" : "55%"), top: (isPortrait ? "55%" : "5%"), bottom: "5%"}}>
      <h1 className="app-title">Video Upload Portal</h1>
      <button className="upload-button" onClick={() => setIsModalOpen(true)} style={{height: "72px"}}>
        Upload Video
      </button>
      {isModalOpen && <UploadModal onClose={() => setIsModalOpen(false)} />}
    </div>
    <div className="app-container dark-theme" style={{zIndex: 1000, left: (isPortrait? "5%" : "55%"), right: "5%", top: "5%", bottom: (isPortrait ? "55%" : "5%")}}>
      <Map isPortrait={isPortrait}></Map>
    </div>
    </div>

  );
}

export default App;