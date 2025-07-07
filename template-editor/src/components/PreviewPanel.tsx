import React from 'react';
import type { EditorState, GeometricShape, TextElement } from '../types/template';

interface PreviewPanelProps {
  editorState: EditorState;
  onSelectElement: (id: string) => void;
  onUpdateGeometricShape: (id: string, updates: Partial<GeometricShape>) => void;
  onUpdateTextElement: (id: string, updates: Partial<TextElement>) => void;
}

export const PreviewPanel: React.FC<PreviewPanelProps> = ({
  editorState,
  onSelectElement,
  onUpdateGeometricShape,
  onUpdateTextElement
}) => {
  const { templateData, geometricShapes, textElements, selectedElement } = editorState;

  const renderGeometricShape = (shape: GeometricShape) => {
    const getClipPath = () => {
      switch (shape.type) {
        case 'diamond':
          return 'polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)';
        case 'hexagon':
          return 'polygon(20% 0%, 80% 0%, 100% 60%, 80% 100%, 20% 100%, 0% 60%)';
        case 'star':
          return 'polygon(50% 0%, 100% 38%, 82% 100%, 18% 100%, 0% 38%)';
        default:
          return 'none';
      }
    };

    return (
      <div
        key={shape.id}
        className={`absolute cursor-pointer transition-all duration-200 animate-rotate ${
          selectedElement === shape.id ? 'ring-2 ring-blue-400' : ''
        }`}
        style={{
          left: `${shape.x}mm`,
          top: `${shape.y}mm`,
          width: `${shape.width}mm`,
          height: `${shape.height}mm`,
          background: shape.color,
          clipPath: getClipPath(),
          opacity: shape.opacity,
          transform: `rotate(${shape.rotation}deg)`,
        }}
        onClick={() => onSelectElement(shape.id)}
      />
    );
  };

  const renderTextElement = (element: TextElement) => {
    const isTitle = element.type === 'title';
    
    return (
      <div
        key={element.id}
        className={`absolute cursor-pointer transition-all duration-200 ${
          selectedElement === element.id ? 'ring-2 ring-blue-400' : ''
        } ${isTitle ? 'gradient-text cyber-glow' : ''}`}
        style={{
          left: `${element.x}mm`,
          top: `${element.y}mm`,
          width: `${element.width}mm`,
          height: `${element.height}mm`,
          fontSize: `${element.fontSize}pt`,
          fontWeight: element.fontWeight,
          color: isTitle ? 'transparent' : element.color,
          backgroundColor: element.backgroundColor,
          borderColor: element.borderColor,
          borderWidth: element.borderWidth ? `${element.borderWidth}px` : 'none',
          borderStyle: element.borderWidth ? 'solid' : 'none',
          borderRadius: element.borderRadius ? `${element.borderRadius}px` : '0',
          padding: element.padding ? `${element.padding}mm` : '0',
          textAlign: element.textAlign,
          textTransform: element.transform as any,
          lineHeight: element.type === 'title' ? '0.9' : '1.4',
          letterSpacing: element.type === 'title' ? '-3px' : '1px',
          backdropFilter: element.backgroundColor?.includes('rgba') ? 'blur(10px)' : 'none',
          boxShadow: element.borderColor ? `0 0 20px ${element.borderColor}30` : 'none',
        }}
        onClick={() => onSelectElement(element.id)}
      >
        {element.content}
      </div>
    );
  };

  return (
    <div className="w-full h-full bg-gray-100 rounded-lg shadow-lg overflow-hidden">
      <div className="w-full h-full relative magazine-cover overflow-hidden">
        {/* A4サイズの表紙コンテナ */}
        <div
          className="relative mx-auto magazine-cover shadow-2xl editor-scale"
          style={{
            width: '210mm',
            height: '297mm',
          }}
        >
          {/* 幾何学的背景 */}
          <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 via-purple-500/10 to-yellow-500/10" />
          
          {/* 幾何学的図形 */}
          {geometricShapes.map(renderGeometricShape)}
          
          {/* テキスト要素 */}
          {textElements.map(renderTextElement)}
          
          {/* 日付・号数 */}
          <div className="absolute top-4 right-4 glass-effect p-4 border border-cyan-400">
            <div className="text-cyan-400 text-xs font-semibold uppercase tracking-wide">
              {templateData.date}
            </div>
            {templateData.issueNumber && (
              <div className="text-white text-2xl font-black mt-1 cyber-glow">
                #{templateData.issueNumber}
              </div>
            )}
          </div>
          
          {/* 特集記事リスト */}
          {templateData.features && templateData.features.length > 0 && (
            <div className="absolute bottom-20 left-4 right-4 space-y-2">
              {templateData.features.map((feature, index) => (
                <div
                  key={index}
                  className="glass-effect p-3 border-l-4 text-white font-semibold uppercase tracking-wide"
                  style={{
                    borderLeftColor: ['#00ffff', '#ff00ff', '#ffff00'][index % 3],
                    boxShadow: `0 0 20px ${['#00ffff', '#ff00ff', '#ffff00'][index % 3]}30`
                  }}
                >
                  {feature}
                </div>
              ))}
            </div>
          )}
          
          {/* デジタル風テキスト */}
          {templateData.digitalText && (
            <div className="absolute bottom-28 right-4 glass-effect p-2 border border-green-400 text-green-400 font-mono text-xs uppercase tracking-wide">
              {templateData.digitalText}
            </div>
          )}
          
          {/* QRコード風装飾 */}
          <div className="absolute bottom-12 right-4 w-8 h-8 bg-gradient-to-br from-white/30 to-transparent opacity-30">
            <div className="w-full h-full bg-repeat" style={{
              backgroundImage: 'linear-gradient(90deg, #ffffff 2px, transparent 2px), linear-gradient(#ffffff 2px, transparent 2px)',
              backgroundSize: '4px 4px'
            }} />
          </div>
          
          {/* 価格 */}
          {templateData.price && (
            <div className="absolute bottom-4 right-4 bg-gradient-to-r from-cyan-400 to-purple-400 text-black px-4 py-2 font-black text-lg uppercase tracking-wide">
              ¥{templateData.price}
            </div>
          )}
          
          {/* バーコード領域 */}
          <div className="absolute bottom-4 left-4 glass-effect text-cyan-400 p-2 border border-cyan-400 text-xs font-mono uppercase tracking-wide">
            ISSN: 1234-5678 | JAN: 1234567890123
          </div>
        </div>
      </div>
    </div>
  );
}; 