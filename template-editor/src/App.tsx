import React, { useState } from 'react';
import type { TemplateData, EditorState, GeometricShape, TextElement } from './types/template';
import { PreviewPanel } from './components/PreviewPanel';
import { PropertiesPanel } from './components/PropertiesPanel';
import { Toolbar } from './components/Toolbar';

const initialTemplateData: TemplateData = {
  title: 'TECH MAGAZINE',
  subtitle: 'Future Technology Review',
  date: new Date().toLocaleDateString('ja-JP'),
  issueNumber: '001',
  features: [
    'AI Revolution 2024',
    'Quantum Computing',
    'Blockchain Innovation'
  ],
  digitalText: 'DIGITAL_TECH.EXE',
  price: '1,200'
};

const initialShapes: GeometricShape[] = [
  {
    id: 'shape-1',
    type: 'diamond',
    x: 150,
    y: 50,
    width: 80,
    height: 80,
    color: 'linear-gradient(45deg, #00ffff 0%, #ff00ff 100%)',
    opacity: 0.3,
    rotation: 0
  },
  {
    id: 'shape-2',
    type: 'hexagon',
    x: -30,
    y: 160,
    width: 100,
    height: 100,
    color: 'linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%)',
    opacity: 0.2,
    rotation: 0
  },
  {
    id: 'shape-3',
    type: 'star',
    x: 50,
    y: 220,
    width: 60,
    height: 60,
    color: 'linear-gradient(45deg, #ffd700 0%, #ff4500 100%)',
    opacity: 0.25,
    rotation: 0
  }
];

const initialTextElements: TextElement[] = [
  {
    id: 'main-title',
    type: 'title',
    content: 'TECH MAGAZINE',
    x: 15,
    y: 20,
    width: 180,
    height: 60,
    fontSize: 64,
    fontWeight: 900,
    color: '#ffffff',
    textAlign: 'left',
    transform: 'uppercase',
    animation: 'glow'
  },
  {
    id: 'subtitle',
    type: 'subtitle',
    content: 'Future Technology Review',
    x: 15,
    y: 80,
    width: 180,
    height: 30,
    fontSize: 20,
    fontWeight: 300,
    color: '#ffffff',
    backgroundColor: 'rgba(0,0,0,0.6)',
    borderColor: '#00ffff',
    borderWidth: 4,
    padding: 10,
    textAlign: 'left',
    transform: 'uppercase'
  }
];

function App() {
  const [editorState, setEditorState] = useState<EditorState>({
    templateData: initialTemplateData,
    geometricShapes: initialShapes,
    textElements: initialTextElements,
    selectedElement: undefined,
    isEditing: false
  });

  const updateTemplateData = (data: Partial<TemplateData>) => {
    setEditorState(prev => ({
      ...prev,
      templateData: { ...prev.templateData, ...data }
    }));
  };

  const updateGeometricShape = (id: string, updates: Partial<GeometricShape>) => {
    setEditorState(prev => ({
      ...prev,
      geometricShapes: prev.geometricShapes.map(shape =>
        shape.id === id ? { ...shape, ...updates } : shape
      )
    }));
  };

  const updateTextElement = (id: string, updates: Partial<TextElement>) => {
    setEditorState(prev => ({
      ...prev,
      textElements: prev.textElements.map(element =>
        element.id === id ? { ...element, ...updates } : element
      )
    }));
  };

  const selectElement = (id: string) => {
    setEditorState(prev => ({
      ...prev,
      selectedElement: id
    }));
  };

  const exportHTML = () => {
    // HTML エクスポート機能を実装
    console.log('HTML Export', editorState);
  };

  const exportPDF = () => {
    // PDF エクスポート機能を実装
    console.log('PDF Export', editorState);
  };

  return (
    <div className="h-screen bg-gray-900 text-white flex flex-col">
      <Toolbar 
        onExportHTML={exportHTML}
        onExportPDF={exportPDF}
      />
      
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 bg-gray-800 p-4">
          <PreviewPanel
            editorState={editorState}
            onSelectElement={selectElement}
            onUpdateGeometricShape={updateGeometricShape}
            onUpdateTextElement={updateTextElement}
          />
        </div>
        
        <div className="w-80 bg-gray-700 p-4 overflow-y-auto">
          <PropertiesPanel
            editorState={editorState}
            onUpdateTemplateData={updateTemplateData}
            onUpdateGeometricShape={updateGeometricShape}
            onUpdateTextElement={updateTextElement}
            onSelectElement={selectElement}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
