import { useState } from "react";
import MapModal from "./MapModal";
import "./UploadModal.css";
import JSZip from "jszip";

function UploadModal({ onClose }) {
  const [vehicleType, setVehicleType] = useState("");
  const [year, setYear] = useState("");
  const [month, setMonth] = useState("");
  const [day, setDay] = useState("");
  const [selectedTime, setSelectedTime] = useState(""); 
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
        second: 0, //default to 0
      },
      vehicle: vehicleType,
    };
    
    //print formData in inspect -> console in web browser
    console.log(JSON.stringify(formData, null, 2)); 

    //create a new ZIP archive
    const zip = new JSZip();

    //add the user's input data (formData) as a JSON named 'incident.json' to the ZIP archive
    zip.file("incident.json", JSON.stringify(formData, null, 2));

    //extract the file extension from the uploaded video file 
    const videoExtension = video.name.split(".").pop();

    //add file (renamed to upload) to the zip ARCHIVE, keeping the original video file extension 
    zip.file(`upload.${videoExtension}`, video, { binary: true });

    try {
      //generate the ZIP file
      const zipBlob = await zip.generateAsync({ type: "blob" });

      //create formData object and append the ZIP file, under the name "file"
      const formDataToSend = new FormData();
      formDataToSend.append("file", zipBlob, "submission.zip");

      //send ZIP to server via POST request to '/upload' endpoint (in app.py)
      const response = await fetch("/upload", {
        method: "POST",
        body: formDataToSend,
      });

      //receive the JSON response from the server, and print to console 
      const jsonResponse = await response.json()
      console.log("Server response:", jsonResponse)

      //check if response indicates an error
      if (!response.ok) {
        throw new Error();
      }

    } catch (error) {
      console.error("Error uploading submission, please try again");
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
