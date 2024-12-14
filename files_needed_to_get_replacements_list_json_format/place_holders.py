# 範囲を指定
start_number = 18542  # 開始の数字
end_number = 19834   # 終了の数字

# 出力するファイル名
output_file = f"placeholders_${start_number}$-${end_number}$.txt"

# テキスト生成
lines = [f"${num}$" for num in range(start_number, end_number + 1)]

# ファイルに保存
with open(output_file, "w", encoding="utf-8") as file:
    file.write("\n".join(lines))

print(f"ファイル '{output_file}' にテキストが保存されました。")

