#!/bin/bash

# 一時ファイルクリーンアップスクリプト
# auto-designerのtempディレクトリ内の古いファイルを削除

TEMP_DIR="./temp"
MAX_AGE_HOURS=24  # 24時間以上古いファイルを削除

echo "🧹 一時ファイルクリーンアップ開始"
echo "対象ディレクトリ: $TEMP_DIR"
echo "削除対象: ${MAX_AGE_HOURS}時間以上古いファイル"

if [ ! -d "$TEMP_DIR" ]; then
    echo "✅ tempディレクトリが存在しません。クリーンアップ完了。"
    exit 0
fi

# 古いファイルを検索して削除
find "$TEMP_DIR" -type f -mtime +$((MAX_AGE_HOURS/24)) -name "*.pdf" -o -name "*.html" | while read file; do
    echo "🗑️  削除: $file"
    rm -f "$file"
done

echo "✅ クリーンアップ完了"

# 現在のファイル一覧を表示
echo ""
echo "📋 現在のtempディレクトリ内容:"
if [ -z "$(ls -A $TEMP_DIR 2>/dev/null)" ]; then
    echo "   (空)"
else
    ls -la "$TEMP_DIR"
fi 