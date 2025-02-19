import { useState } from "react";
import MapModal from "./MapModal";
import "./UploadModal.css";

function UploadModal({ onClose }) {
  const [vehicleType, setVehicleType] = useState("");
  const [time, setTime] = useState("");
  const [video, setVideo] = useState(null);
  const [isMapOpen, setIsMapOpen] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Vehicle Type:", vehicleType);
    console.log("Time:", time);
    console.log("Video:", video);
    console.log("Location:", selectedLocation);
    onClose();
  };

  const handleLocationConfirm = (location) => {
    setSelectedLocation(location);
    setIsMapOpen(false);
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h3>Upload Video</h3>
        <form onSubmit={handleSubmit}>
          <label>Vehicle Type:</label>
          <select value={vehicleType} onChange={(e) => setVehicleType(e.target.value)} required>
            <option value="">Select...</option>
            <option value="bicycle">Bicycle</option>
            <option value="e-scooter">E-Scooter</option>
          </select>

          <label>Time:</label>
          <input
            type="text"
            placeholder="Enter time"
            value={time}
            onChange={(e) => setTime(e.target.value)}
            required
          />

          <label>Location:</label>
          <button
            type="button"
            className="location-button"
            onClick={() => setIsMapOpen(true)}
          >
            {selectedLocation
              ? `Selected: ${selectedLocation.lat.toFixed(5)}, ${selectedLocation.lng.toFixed(5)}`
              : "Select Location"}
          </button>

          <label>Upload Video:</label>
          <input
            type="file"
            accept="video/*"
            onChange={(e) => setVideo(e.target.files[0])}
            required
          />

          <div className="button-container">
            <button type="submit" className="submit-button">Submit</button>
            <button type="button" className="close-button" onClick={onClose}>Close</button>
          </div>
        </form>

        {isMapOpen && (
          <MapModal
            onConfirm={handleLocationConfirm}
            onClose={() => setIsMapOpen(false)}
          />
        )}
      </div>
    </div>
  );
}

export default UploadModal;