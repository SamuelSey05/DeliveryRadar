import { useState } from "react";
import UploadModal from "./UploadModal";
import "./App.css";

function App() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div className="app-container dark-theme">
      <h1 className="app-title">Video Upload Portal</h1>
      <button className="upload-button" onClick={() => setIsModalOpen(true)}>
        Upload Video
      </button>
      {isModalOpen && <UploadModal onClose={() => setIsModalOpen(false)} />}
    </div>
  );
}

export default App;