import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import axios from "axios";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Fix for default marker icon issue in React-Leaflet with Webpack
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png"),
});

const ISSMap = () => {
  const [position, setPosition] = useState([0, 0]);

  const fetchISSData = async () => {
    try {
      // Fetch ISS location from our Flask backend
      const response = await axios.get("http://localhost:5000/iss-location");
      const { iss_position } = response.data;
      const lat = parseFloat(iss_position.latitude);
      const lon = parseFloat(iss_position.longitude);
      setPosition([lat, lon]);
    } catch (error) {
      console.error("Error fetching ISS location:", error);
    }
  };

  useEffect(() => {
    fetchISSData();
    // Update ISS location every 5 seconds
    const interval = setInterval(fetchISSData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <MapContainer
      center={position}
      zoom={3}
      style={{ height: "500px", width: "100%" }}
    >
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <Marker position={position}>
        <Popup>ISS Current Location</Popup>
      </Marker>
    </MapContainer>
  );
};

export default ISSMap;
