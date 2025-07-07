import React from 'react';
import { Download, FileText, Printer, Save, Undo, Redo } from 'lucide-react';

interface ToolbarProps {
  onExportHTML: () => void;
  onExportPDF: () => void;
  onSave?: () => void;
  onUndo?: () => void;
  onRedo?: () => void;
}

export const Toolbar: React.FC<ToolbarProps> = ({
  onExportHTML,
  onExportPDF,
  onSave,
  onUndo,
  onRedo
}) => {
  return (
    <div className="bg-gray-800 border-b border-gray-600 px-4 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-bold text-white">Template Editor</h1>
          <div className="text-sm text-gray-400">
            技術雑誌表紙テンプレート
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {onUndo && (
            <button
              onClick={onUndo}
              className="p-2 bg-gray-700 hover:bg-gray-600 rounded text-white transition-colors"
              title="元に戻す"
            >
              <Undo size={16} />
            </button>
          )}
          
          {onRedo && (
            <button
              onClick={onRedo}
              className="p-2 bg-gray-700 hover:bg-gray-600 rounded text-white transition-colors"
              title="やり直し"
            >
              <Redo size={16} />
            </button>
          )}
          
          {onSave && (
            <button
              onClick={onSave}
              className="p-2 bg-gray-700 hover:bg-gray-600 rounded text-white transition-colors"
              title="保存"
            >
              <Save size={16} />
            </button>
          )}
          
          <div className="w-px h-6 bg-gray-600" />
          
          <button
            onClick={onExportHTML}
            className="flex items-center space-x-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white transition-colors"
            title="HTMLとしてエクスポート"
          >
            <FileText size={16} />
            <span>HTML</span>
          </button>
          
          <button
            onClick={onExportPDF}
            className="flex items-center space-x-2 px-3 py-2 bg-green-600 hover:bg-green-700 rounded text-white transition-colors"
            title="PDFとしてエクスポート"
          >
            <Printer size={16} />
            <span>PDF</span>
          </button>
        </div>
      </div>
    </div>
  );
}; 