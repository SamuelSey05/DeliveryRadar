import { useState } from "react";
import UploadModal from "./UploadModal";
import "./App.css";
import Map from "./Map";

function App() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div className="rowC">
    <div className="app-container dark-theme" style={{zIndex: 1000}}>
      <h1 className="app-title">Video Upload Portal</h1>
      <button className="upload-button" onClick={() => setIsModalOpen(true)}>
        Upload Video
      </button>
      {isModalOpen && <UploadModal onClose={() => setIsModalOpen(false)} />}
    </div>
    <div className="app-container dark-theme" style={{zIndex: 0}}>
      <Map></Map>
    </div>
    </div>

  );
}

export default App;