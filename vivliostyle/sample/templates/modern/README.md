# Modern Templates

このフォルダには、モダンなデザインのテンプレートが含まれています。

## 構造

```
modern/
├── single/          # 単ページテンプレート
│   └── _modern-minimal-single/
├── spread/          # 見開きページテンプレート  
│   ├── _modern-balanced-spread/
│   ├── horizontal-text-spread/
│   ├── landscape-quote-spread/
│   └── vertical-image-tategaki-spread/
└── title/           # タイトルページテンプレート
    ├── _modern-title-page/
    ├── modern-horizontal-cover/
    └── modern-vertical-cover/
```

## テンプレート一覧

### Single Page Templates
- **_modern-minimal-single**: ミニマルでモダンなデザインの単ページテンプレート

### Spread Page Templates  
- **_modern-balanced-spread**: バランスの取れたモダンな見開きテンプレート
- **horizontal-text-spread**: 横書きテキストとミラー効果を使った見開きテンプレート
- **landscape-quote-spread**: 風景画像と縦書き格言を配置した見開きテンプレート
- **vertical-image-tategaki-spread**: 左に縦画像、右に縦書き３段組みテキストの見開きテンプレート

### Title Page Templates
- **_modern-title-page**: モダンなタイトルページテンプレート
- **modern-vertical-cover**: 縦書きテキストと全面画像の表紙テンプレート
- **modern-horizontal-cover**: 横書きテキストと全面画像の表紙テンプレート

## 使用方法

各テンプレートは以下のファイルで構成されています：
- `index.html`: メインのHTMLテンプレート
- `style.css`: CSS スタイルファイル

テンプレートを使用する際は、適切なHTMLとCSSファイルを参照してください。

## 特別な機能

### vertical-image-tategaki-spread の特徴
- **縦画像表示**: 左ページに縦向きの画像を全面表示
- **縦書き３段組み**: 右ページに日本語縦書きで３段組みレイアウト
- **段落下げ**: 改行時に自動的に段落をインデント
- **美しい日本語表示**: 明朝体を使用し、句読点や数字の表示を最適化
- **レスポンシブ対応**: 画面サイズに応じてスケーリング調整
