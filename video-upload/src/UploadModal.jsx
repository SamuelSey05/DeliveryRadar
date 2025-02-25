import { useState } from "react";
import MapModal from "./MapModal";
import "./UploadModal.css";
import JSZip from "jszip";

function UploadModal({ onClose }) {
  const [vehicleType, setVehicleType] = useState("");
  const [year, setYear] = useState("");
  const [month, setMonth] = useState("");
  const [day, setDay] = useState("");
  const [selectedTime, setSelectedTime] = useState(""); // "HH:MM" string
  const [video, setVideo] = useState(null);
  const [isMapOpen, setIsMapOpen] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
  
    const [hour, minute] = selectedTime.split(":").map(Number);
  
    const formData = {
      location: {
        lat: parseFloat((selectedLocation?.lat || 0.0).toFixed(6)),
        lon: parseFloat((selectedLocation?.lng || 0.0).toFixed(6)),
      },
      date: {
        year: parseInt(year, 10) || 1970,
        month: parseInt(month, 10) || 1,
        day: parseInt(day, 10) || 1,
      },
      time: {
        hour: hour || 0,
        minute: minute || 0,
        second: 0, // Always default to 0
      },
      vehicle: vehicleType,
    };
  
    console.log(JSON.stringify(formData, null, 2)); //print formData in inspect -> console in web browser

    const zip = new JSZip();
    zip.file("incident.json", JSON.stringify(formData, null, 2));
    const videoExtension = video.name.split(".").pop();
    zip.file(`upload.${videoExtension}`, video, { binary: true });

    try {
      const zipBlob = await zip.generateAsync({ type: "blob" });
      const formDataToSend = new FormData();
      formDataToSend.append("file", zipBlob, "submission.zip");

      const response = await fetch("/upload", {
        method: "POST",
        body: formDataToSend,
      });

      const jsonResponse = await response.json()
      console.log("Server response:", jsonResponse)

      if (!response.ok) {
        throw new Error("Failed to upload ZIP file");
      }

      //alert("Upload successful - line 62 in jsx")
    } catch (error) {
      console.error("Error generating or uploading ZIP file:", error);
      //alert("Upload failed - line 65 in jsx")
    }

    onClose();
  };

  const handleLocationConfirm = (location) => {
    setSelectedLocation(location);
    setIsMapOpen(false);
  };

  return (
    <div className="modal-overlay" style={{ zIndex: 1000 }}>
      <div className="modal" style={{ zIndex: "inherit" }}>
        <h3>Upload Video</h3>
        <form onSubmit={handleSubmit}>
          <label>Vehicle Type:</label>
          <select value={vehicleType} onChange={(e) => setVehicleType(e.target.value)} required>
            <option value="">Select...</option>
            <option value="bike">Bicycle</option>
            <option value="scooter">E-Scooter</option>
          </select>

          <label>Date:</label>
          <div className="date-inputs">
            <input
              type="number"
              placeholder="YYYY"
              value={year}
              onChange={(e) => setYear(e.target.value)}
              min="1900"
              max="2100"
              required
              style={{ width: '50px' }}
            />
            <input
              type="number"
              placeholder="MM"
              value={month}
              onChange={(e) => setMonth(e.target.value)}
              min="1"
              max="12"
              required
              style={{ width: '40px'}}
            />
            <input
              type="number"
              placeholder="DD"
              value={day}
              onChange={(e) => setDay(e.target.value)}
              min="1"
              max="31"
              required
              style={{ width: '38px'}}
            />
          </div>

          <label>Time:</label>
          <select value={selectedTime} onChange={(e) => setSelectedTime(e.target.value)} required>
            <option value="">Select Time...</option>
            {Array.from({ length: 48 }).map((_, index) => {
              const hours = Math.floor(index / 2);
              const minutes = index % 2 === 0 ? '00' : '30';
              const formattedTime = `${String(hours).padStart(2, '0')}:${minutes}`;
              return (
                <option key={formattedTime} value={formattedTime}>
                  {formattedTime}
                </option>
              );
            })}
          </select>

          <label>Location:</label>
          <button
            type="button"
            className="location-button"
            onClick={() => setIsMapOpen(true)}
          >
            {selectedLocation
              ? "Location Selected" 
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
            <button type="submit" className="submit-button">
              Submit
            </button>
            <button type="button" className="close-button" onClick={onClose}>
              Close
            </button>
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
