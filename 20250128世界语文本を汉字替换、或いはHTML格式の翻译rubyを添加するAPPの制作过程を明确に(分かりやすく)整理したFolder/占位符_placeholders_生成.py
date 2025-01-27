# 数字の範囲を指定
start = 20897  # 開始の数字
end = 499999    # 終了の数字

# プレースホルダーのカスタム文字列
prefix = "$"  # プレースホルダーの前の文字列
suffix = "$"  # プレースホルダーの後の文字列

# プレースホルダーを生成
placeholders = [f"{prefix}{num}{suffix}" for num in range(start, end + 1)]

# テキストファイルに出力
output_file = "占位符(placeholders)_$20987$-$499999$_全域替换用.txt"  # 出力ファイル名
with open(output_file, "w") as file:
    file.write("\n".join(placeholders))

print(f"プレースホルダーが {output_file} に保存されました！")


# 数字の範囲を指定
start = 13246  # 開始の数字
end = 19834    # 終了の数字

# プレースホルダーのカスタム文字列
prefix = "$"  # プレースホルダーの前の文字列
suffix = "$"  # プレースホルダーの後の文字列

# プレースホルダーを生成
placeholders = [f"{prefix}{num}{suffix}" for num in range(start, end + 1)]

# テキストファイルに出力
output_file = "占位符(placeholders)_$13246$-$19834$_二文字词根替换用.txt"  # 出力ファイル名
with open(output_file, "w") as file:
    file.write("\n".join(placeholders))

print(f"プレースホルダーが {output_file} に保存されました！")


# 数字の範囲を指定
start = 1854  # 開始の数字
end = 4934    # 終了の数字

# プレースホルダーのカスタム文字列
prefix = "%"  # プレースホルダーの前の文字列
suffix = "%"  # プレースホルダーの後の文字列

# プレースホルダーを生成
placeholders = [f"{prefix}{num}{suffix}" for num in range(start, end + 1)]

# テキストファイルに出力
output_file = "占位符(placeholders)_%1854%-%4934%_文字列替换skip用.txt"  # 出力ファイル名
with open(output_file, "w") as file:
    file.write("\n".join(placeholders))

print(f"プレースホルダーが {output_file} に保存されました！")


# 数字の範囲を指定
start = 20374  # 開始の数字
end = 97648    # 終了の数字

# プレースホルダーのカスタム文字列
prefix = "@"  # プレースホルダーの前の文字列
suffix = "@"  # プレースホルダーの後の文字列

# プレースホルダーを生成
placeholders = [f"{prefix}{num}{suffix}" for num in range(start, end + 1)]

# テキストファイルに出力
output_file = "占位符(placeholders)_@20374@-@97648@_局部文字列替换用.txt"  # 出力ファイル名
with open(output_file, "w") as file:
    file.write("\n".join(placeholders))

print(f"プレースホルダーが {output_file} に保存されました！")


# 数字の範囲を指定
start = 5134  # 開始の数字
end = 9728    # 終了の数字

# プレースホルダーのカスタム文字列
prefix = "@"  # プレースホルダーの前の文字列
suffix = "@"  # プレースホルダーの後の文字列

# プレースホルダーを生成
placeholders = [f"{prefix}{num}{suffix}" for num in range(start, end + 1)]

# テキストファイルに出力
output_file = "占位符(placeholders)_@5134@-@9728@_局部文字列替换结果捕捉用.txt"  # 出力ファイル名
with open(output_file, "w") as file:
    file.write("\n".join(placeholders))

print(f"プレースホルダーが {output_file} に保存されました！")

