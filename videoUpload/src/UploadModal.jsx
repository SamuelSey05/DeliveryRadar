import { useState } from "react";
import MapModal from "./MapModal";
import "./UploadModal.css";
import JSZip from "jszip";

//INFOMODAL 
function InfoModal({ onClose }) {
  return (
    <div className="modal-overlay" style={{ zIndex: 1100, position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}>
      <div className="modal" style={{ width: '100%', height: '100%', padding: '20px' }}>
        <h3>Video Instructions</h3>
        <p>Follow these instructions for reliable video analysis:</p>
        <ul style={{ textAlign: 'left' }}>
          <li>The video must not exceed 50 MB</li>
          <li>The video must be at least 1 second long</li>
          <li>The camera should be kept still while filming</li>
          <li>At least 2 cones should be visible</li>
        </ul>
        <button className="close-button" onClick={onClose}>Close</button>
      </div>
    </div>
  );
}

function UploadModal({ onClose }) {
  const [vehicleType, setVehicleType] = useState("");
  const [year, setYear] = useState("");
  const [month, setMonth] = useState("");
  const [day, setDay] = useState("");
  const [selectedTime, setSelectedTime] = useState("");
  const [video, setVideo] = useState(null);
  const [isMapOpen, setIsMapOpen] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState(null);

  const [isInfoOpen, setIsInfoOpen] = useState(false); //INFOMODAL

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
      const jsonResponse = await response.json();

      //remove console log before final code submission
      console.log("Server response:", jsonResponse);

      //check if response indicates an error
      if (!response.ok) {
        throw new Error();
      }

      alert("Submission successfully uploaded!");
    } catch (error) {

      //remove console log before final code submission
      console.error("Error uploading submission, please try again");
      alert("Upload failed - please try again");
    }
  };

  const handleLocationConfirm = (location) => {
    setSelectedLocation(location);
    setIsMapOpen(false);
  };

  const months = [
    { name: "January", value: "1", days: 31 },
    { name: "February", value: "2", days: 28 },
    { name: "March", value: "3", days: 31 },
    { name: "April", value: "4", days: 30 },
    { name: "May", value: "5", days: 31 },
    { name: "June", value: "6", days: 30 },
    { name: "July", value: "7", days: 31 },
    { name: "August", value: "8", days: 31 },
    { name: "September", value: "9", days: 30 },
    { name: "October", value: "10", days: 31 },
    { name: "November", value: "11", days: 30 },
    { name: "December", value: "12", days: 31 },
  ];

  const getDaysInMonth = () => {
    const selectedMonth = months.find((m) => m.value === month);
    if (selectedMonth) {
      return selectedMonth.days;
    }
    return 31;
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 50 * 1024 * 1024) { // 50MB limit
        alert("File size exceeds size limit - please select a smaller file.");
        e.target.value = ""; // Reset the input field
        setVideo(null);
      } else {
        setVideo(file);
      }
    }
  };

  return (
    <div className="modal-overlay" style={{ zIndex: 1000 }}>
      <div className="modal" style={{ zIndex: "inherit" }}>
        
        <button className="info-button" onClick={() => setIsInfoOpen(true)}>ℹ️</button> 
        
        <h3>Upload Video</h3>
        <form onSubmit={handleSubmit}>
          <label>Vehicle Type:</label>
          <select
            value={vehicleType}
            onChange={(e) => setVehicleType(e.target.value)}
            required
          >
            <option value="">Select...</option>
            <option value="bike">Bicycle</option>
            <option value="scooter">E-Scooter</option>
          </select>

          <label>Date:</label>
          <div className="date-inputs">
            <select value={year} onChange={(e) => setYear(e.target.value)} required>
              {[2020, 2021, 2022, 2023, 2024, 2025].map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
            
            <select value={month} onChange={(e) => setMonth(e.target.value)} required>
              {months.map((m) => (
                <option key={m.value} value={m.value}>{m.name}</option>
              ))}
            </select>

            <select value={day} onChange={(e) => setDay(e.target.value)} required>
              {[...Array(getDaysInMonth()).keys()].map((d) => (
                <option key={d + 1} value={d + 1}>{d + 1}</option>
              ))}
            </select>
          </div>

          <label>Time:</label>
          <select
            value={selectedTime}
            onChange={(e) => setSelectedTime(e.target.value)}
            required
          >
            <option value="">Select Time...</option>
            {Array.from({ length: 48 }).map((_, index) => {
              const hours = Math.floor(index / 2);
              const minutes = index % 2 === 0 ? "00" : "30";
              const formattedTime = `${String(hours).padStart(
                2,
                "0"
              )}:${minutes}`;
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
            {selectedLocation ? "Location Selected" : "Select Location"}
          </button>

          <label>Upload Video:</label>
          <input
            type="file"
            accept="video/*"
            onChange={handleFileChange}
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

      {isInfoOpen && <InfoModal onClose={() => setIsInfoOpen(false)} />}

    </div>
  );
}

export default UploadModal;
