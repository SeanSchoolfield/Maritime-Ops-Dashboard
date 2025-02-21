import { useState } from "react";
import CustomGeometry from "./utilities/CustomGeometry";
import UIControls from "./utilities/UIControls";
import './App.css';

function App() {
  const [isDrawing, setIsDrawing] = useState(false);
  const [shapeType, setShapeType] = useState("polygon");
  const [geometries, setGeometries] = useState([]);

  const handleToggleDrawing = () => {
    setIsDrawing(!isDrawing);
  };

  const handleUndo = () => {
    setGeometries((prev) => {
      if (prev.length === 0) return prev;
      const updated = [...prev];
      updated[updated.length - 1].positions.pop();
      return updated;
    });
  };

  const handleClear = () => {
    setGeometries([]);
  };

  const handleSelectShape = (shape) => {
    setShapeType(shape);
  };

  return (
    <div>
      <UIControls
        onToggleDrawing={handleToggleDrawing}
        onUndo={handleUndo}
        onClear={handleClear}
        onSelectShape={handleSelectShape}
      />
      <CustomGeometry 
        isDrawing={isDrawing} 
        shapeType={shapeType}
        geometries={geometries}
        setGeometries={setGeometries} 
      />
    </div>
  );
}

export default App;