import React, { useState } from 'react';
import { Plus, X, Edit2, Palette, Move, Type } from 'lucide-react';
import type { EditorState, TemplateData, GeometricShape, TextElement } from '../types/template';

interface PropertiesPanelProps {
  editorState: EditorState;
  onUpdateTemplateData: (data: Partial<TemplateData>) => void;
  onUpdateGeometricShape: (id: string, updates: Partial<GeometricShape>) => void;
  onUpdateTextElement: (id: string, updates: Partial<TextElement>) => void;
  onSelectElement: (id: string) => void;
}

export const PropertiesPanel: React.FC<PropertiesPanelProps> = ({
  editorState,
  onUpdateTemplateData,
  onUpdateGeometricShape,
  onUpdateTextElement,
  onSelectElement
}) => {
  const { templateData, geometricShapes, textElements, selectedElement } = editorState;
  const [activeTab, setActiveTab] = useState<'basic' | 'shapes' | 'text'>('basic');
  
  const selectedShape = geometricShapes.find(s => s.id === selectedElement);
  const selectedTextElement = textElements.find(t => t.id === selectedElement);

  const updateFeature = (index: number, value: string) => {
    const newFeatures = [...(templateData.features || [])];
    newFeatures[index] = value;
    onUpdateTemplateData({ features: newFeatures });
  };

  const addFeature = () => {
    const newFeatures = [...(templateData.features || []), '新しい特集'];
    onUpdateTemplateData({ features: newFeatures });
  };

  const removeFeature = (index: number) => {
    const newFeatures = templateData.features?.filter((_, i) => i !== index) || [];
    onUpdateTemplateData({ features: newFeatures });
  };

  const renderBasicTab = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-2">タイトル</label>
        <input
          type="text"
          value={templateData.title}
          onChange={(e) => onUpdateTemplateData({ title: e.target.value })}
          className="w-full p-2 bg-gray-600 border border-gray-500 rounded text-white"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium mb-2">サブタイトル</label>
        <input
          type="text"
          value={templateData.subtitle || ''}
          onChange={(e) => onUpdateTemplateData({ subtitle: e.target.value })}
          className="w-full p-2 bg-gray-600 border border-gray-500 rounded text-white"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium mb-2">日付</label>
        <input
          type="text"
          value={templateData.date || ''}
          onChange={(e) => onUpdateTemplateData({ date: e.target.value })}
          className="w-full p-2 bg-gray-600 border border-gray-500 rounded text-white"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium mb-2">号数</label>
        <input
          type="text"
          value={templateData.issueNumber || ''}
          onChange={(e) => onUpdateTemplateData({ issueNumber: e.target.value })}
          className="w-full p-2 bg-gray-600 border border-gray-500 rounded text-white"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium mb-2">価格</label>
        <input
          type="text"
          value={templateData.price || ''}
          onChange={(e) => onUpdateTemplateData({ price: e.target.value })}
          className="w-full p-2 bg-gray-600 border border-gray-500 rounded text-white"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium mb-2">デジタルテキスト</label>
        <input
          type="text"
          value={templateData.digitalText || ''}
          onChange={(e) => onUpdateTemplateData({ digitalText: e.target.value })}
          className="w-full p-2 bg-gray-600 border border-gray-500 rounded text-white"
        />
      </div>
      
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium">特集記事</label>
          <button
            onClick={addFeature}
            className="p-1 bg-blue-600 hover:bg-blue-700 rounded text-white"
          >
            <Plus size={16} />
          </button>
        </div>
        <div className="space-y-2">
          {templateData.features?.map((feature, index) => (
            <div key={index} className="flex items-center space-x-2">
              <input
                type="text"
                value={feature}
                onChange={(e) => updateFeature(index, e.target.value)}
                className="flex-1 p-2 bg-gray-600 border border-gray-500 rounded text-white"
              />
              <button
                onClick={() => removeFeature(index)}
                className="p-1 bg-red-600 hover:bg-red-700 rounded text-white"
              >
                <X size={16} />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderShapesTab = () => (
    <div className="space-y-4">
      <div className="text-sm font-medium mb-4">幾何学的図形</div>
      
      {geometricShapes.map((shape) => (
        <div
          key={shape.id}
          className={`p-3 rounded border cursor-pointer ${
            selectedElement === shape.id
              ? 'border-blue-400 bg-blue-900/20'
              : 'border-gray-600 bg-gray-800/50'
          }`}
          onClick={() => onSelectElement(shape.id)}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">{shape.type}</span>
            <div className="flex items-center space-x-2">
              <Move size={14} />
              <Palette size={14} />
            </div>
          </div>
          
          {selectedElement === shape.id && (
            <div className="space-y-2 mt-3">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs text-gray-300 mb-1">X位置</label>
                  <input
                    type="number"
                    value={shape.x}
                    onChange={(e) => onUpdateGeometricShape(shape.id, { x: Number(e.target.value) })}
                    className="w-full p-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-300 mb-1">Y位置</label>
                  <input
                    type="number"
                    value={shape.y}
                    onChange={(e) => onUpdateGeometricShape(shape.id, { y: Number(e.target.value) })}
                    className="w-full p-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs text-gray-300 mb-1">幅</label>
                  <input
                    type="number"
                    value={shape.width}
                    onChange={(e) => onUpdateGeometricShape(shape.id, { width: Number(e.target.value) })}
                    className="w-full p-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-300 mb-1">高さ</label>
                  <input
                    type="number"
                    value={shape.height}
                    onChange={(e) => onUpdateGeometricShape(shape.id, { height: Number(e.target.value) })}
                    className="w-full p-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-xs text-gray-300 mb-1">透明度</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={shape.opacity}
                  onChange={(e) => onUpdateGeometricShape(shape.id, { opacity: Number(e.target.value) })}
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="block text-xs text-gray-300 mb-1">回転角度</label>
                <input
                  type="range"
                  min="0"
                  max="360"
                  value={shape.rotation}
                  onChange={(e) => onUpdateGeometricShape(shape.id, { rotation: Number(e.target.value) })}
                  className="w-full"
                />
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );

  const renderTextTab = () => (
    <div className="space-y-4">
      <div className="text-sm font-medium mb-4">テキスト要素</div>
      
      {textElements.map((element) => (
        <div
          key={element.id}
          className={`p-3 rounded border cursor-pointer ${
            selectedElement === element.id
              ? 'border-blue-400 bg-blue-900/20'
              : 'border-gray-600 bg-gray-800/50'
          }`}
          onClick={() => onSelectElement(element.id)}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">{element.type}</span>
            <div className="flex items-center space-x-2">
              <Type size={14} />
              <Edit2 size={14} />
            </div>
          </div>
          
          {selectedElement === element.id && (
            <div className="space-y-2 mt-3">
              <div>
                <label className="block text-xs text-gray-300 mb-1">内容</label>
                <input
                  type="text"
                  value={element.content}
                  onChange={(e) => onUpdateTextElement(element.id, { content: e.target.value })}
                  className="w-full p-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs text-gray-300 mb-1">X位置</label>
                  <input
                    type="number"
                    value={element.x}
                    onChange={(e) => onUpdateTextElement(element.id, { x: Number(e.target.value) })}
                    className="w-full p-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-300 mb-1">Y位置</label>
                  <input
                    type="number"
                    value={element.y}
                    onChange={(e) => onUpdateTextElement(element.id, { y: Number(e.target.value) })}
                    className="w-full p-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs text-gray-300 mb-1">フォントサイズ</label>
                  <input
                    type="number"
                    value={element.fontSize}
                    onChange={(e) => onUpdateTextElement(element.id, { fontSize: Number(e.target.value) })}
                    className="w-full p-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-300 mb-1">フォントの太さ</label>
                  <input
                    type="number"
                    value={element.fontWeight}
                    onChange={(e) => onUpdateTextElement(element.id, { fontWeight: Number(e.target.value) })}
                    className="w-full p-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-xs text-gray-300 mb-1">色</label>
                <input
                  type="color"
                  value={element.color}
                  onChange={(e) => onUpdateTextElement(element.id, { color: e.target.value })}
                  className="w-full h-8 bg-gray-600 border border-gray-500 rounded"
                />
              </div>
              
              <div>
                <label className="block text-xs text-gray-300 mb-1">テキスト整列</label>
                <select
                  value={element.textAlign}
                  onChange={(e) => onUpdateTextElement(element.id, { textAlign: e.target.value as 'left' | 'center' | 'right' })}
                  className="w-full p-1 bg-gray-600 border border-gray-500 rounded text-white text-sm"
                >
                  <option value="left">左揃え</option>
                  <option value="center">中央揃え</option>
                  <option value="right">右揃え</option>
                </select>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );

  return (
    <div className="h-full flex flex-col">
      <div className="flex border-b border-gray-600">
        <button
          onClick={() => setActiveTab('basic')}
          className={`px-4 py-2 text-sm font-medium ${
            activeTab === 'basic'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          基本設定
        </button>
        <button
          onClick={() => setActiveTab('shapes')}
          className={`px-4 py-2 text-sm font-medium ${
            activeTab === 'shapes'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          図形
        </button>
        <button
          onClick={() => setActiveTab('text')}
          className={`px-4 py-2 text-sm font-medium ${
            activeTab === 'text'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          テキスト
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
        {activeTab === 'basic' && renderBasicTab()}
        {activeTab === 'shapes' && renderShapesTab()}
        {activeTab === 'text' && renderTextTab()}
      </div>
    </div>
  );
}; 