export interface TemplateData {
  title: string;
  subtitle?: string;
  date?: string;
  issueNumber?: string;
  features?: string[];
  digitalText?: string;
  price?: string;
}

export interface GeometricShape {
  id: string;
  type: 'diamond' | 'hexagon' | 'star';
  x: number;
  y: number;
  width: number;
  height: number;
  color: string;
  opacity: number;
  rotation: number;
}

export interface TextElement {
  id: string;
  type: 'title' | 'subtitle' | 'feature' | 'date' | 'issueNumber' | 'price' | 'digitalText';
  content: string;
  x: number;
  y: number;
  width: number;
  height: number;
  fontSize: number;
  fontWeight: number;
  color: string;
  backgroundColor?: string;
  borderColor?: string;
  borderWidth?: number;
  borderRadius?: number;
  padding?: number;
  textAlign: 'left' | 'center' | 'right';
  transform?: string;
  animation?: string;
}

export interface EditorState {
  templateData: TemplateData;
  geometricShapes: GeometricShape[];
  textElements: TextElement[];
  selectedElement?: string;
  isEditing: boolean;
}

export interface Position {
  x: number;
  y: number;
}

export interface Size {
  width: number;
  height: number;
} 