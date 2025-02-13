import "./App.css";
import Header from "./Components/Header";
import Map from "./Components/Map";

function App() {
  return (
    <>
      <div className="container">
        <Header></Header>
      </div>
      <div className="container"><Map></Map></div>
      
    </>
  );
}

export default App;