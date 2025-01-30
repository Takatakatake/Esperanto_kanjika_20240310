#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"esp_text_replacement_module.py" から関数・定数等をインポートして、
エスペラント文の文字列(漢字)置換を実行する。
"""
# windowsでは、相対座標がうまく認識されないことがあるので、PATHの設定には注意が必要。何とかこのpythonファイルがあるディレクトリ上で実行する方法を模索する必要がある。
# Multi-processing が実行される行以降を  ""if __name__ == '__main__':"" ブロックインデント内に収め、同ブロック内にmultiprocessing.set_start_method('spawn', force=True)という設定行も追加することでうまく動作した。
# if __name__ == '__main__':
#     multiprocessing.set_start_method('spawn', force=True)

import os
import sys
import re
import json
import time
import multiprocessing
from typing import List, Tuple

# --- 1) ここがポイント: モジュールから必要な要素をインポート ---
from esp_text_replacement_module import (
    # 占位符読み込み
    import_placeholders,
    # 主要な置換ルールを実装した複合関数
    orchestrate_comprehensive_esperanto_text_replacement,
    # 行単位で並列処理するための関数
    parallel_process
)

# --- 2) グローバル設定 (例: プロセス数やテキスト複製回数など) ---
num_processes = 8
text_repeat_times = 10
format_type = 'HTML格式_Ruby文字_大小调整'  # 例: "HTML格式_Ruby文字_大小调整"

# --- 3) JSONファイル および 占位符ファイルのパス ---
JSON_FILE = "最终的な替换用リスト(列表)(合并3个JSON文件).json"
PLACEHOLDER_SKIP_FILE = "占位符(placeholders)_%1854%-%4934%_文字列替换skip用.txt"
PLACEHOLDER_LOCAL_FILE = "占位符(placeholders)_@5134@-@9728@_局部文字列替换结果捕捉用.txt"

# --- 4) 入力テキストファイル (エスペラント文) ---
INPUT_TEXT_FILE = "例句_Esperanto文本.txt"

# --- 5) 出力先HTML ---
OUTPUT_HTML_FILE = "Esperanto_Text_Replacement_Result_Multiprocessing_windows.html"

def main():
    """
    メイン処理:
      1) JSON読み込み → 置換リスト3種を取得
      2) プレースホルダ読み込み (skip用 / localized用)
      3) 入力テキストを取得 (複製回数 text_repeat_times 回)
      4) parallel_process(...) を実行
      5) HTMLとして出力 (format_typeに応じてルビ等を付与)
    """
    # 1) JSONファイルから置換リストをロード
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        combined_3_replacements_lists = json.load(f)

    # キーごとに取得
    replacements_final_list = combined_3_replacements_lists.get(
        "全域替换用のリスト(列表)型配列(replacements_final_list)", []
    )
    replacements_list_for_localized_string = combined_3_replacements_lists.get(
        "局部文字替换用のリスト(列表)型配列(replacements_list_for_localized_string)", []
    )
    replacements_list_for_2char = combined_3_replacements_lists.get(
        "二文字词根替换用のリスト(列表)型配列(replacements_list_for_2char)", []
    )

    # 2) プレースホルダー (skip用 / localized用)
    placeholders_for_skipping_replacements = import_placeholders(PLACEHOLDER_SKIP_FILE)
    placeholders_for_localized_replacement = import_placeholders(PLACEHOLDER_LOCAL_FILE)

    # 3) テキスト読み込み & 繰り返し
    with open(INPUT_TEXT_FILE, "r", encoding="utf-8") as g:
        text0 = g.read() * text_repeat_times

    # 4) マルチプロセスによる文字列(漢字)置換処理を実行
    #    parallel_process(...) はモジュール内の関数。
    replaced_text = parallel_process(
        text=text0,
        num_processes=num_processes,
        placeholders_for_skipping_replacements=placeholders_for_skipping_replacements,
        replacements_list_for_localized_string=replacements_list_for_localized_string,
        placeholders_for_localized_replacement=placeholders_for_localized_replacement,
        replacements_final_list=replacements_final_list,
        replacements_list_for_2char=replacements_list_for_2char,
        format_type=format_type
    )

    # 5) 出力用HTMLの装飾 (format_type の内容によって変化)
    #    以下は元のコードを踏襲したルビ用CSSの追加例です。
    if format_type in ('HTML格式_Ruby文字_大小调整','HTML格式_Ruby文字_大小调整_汉字替换'):
        # html形式におけるルビサイズの変更形式
        ruby_style_head = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ほとんどの環境で動作するルビ表示</title>
<style>

    :root {
    --ruby-color: blue;
    --ruby-font-size: 50%;
    }

    .text-S_S { font-size: 12px; }
    .text-M_M {
    font-size: 16px; 
    font-family: Arial, sans-serif;
    line-height: 1.6 !important; 
    display: block; /* ブロック要素として扱う */
    position: relative;
    }
    .text-L_L { font-size: 20px; }
    .text-X_X { font-size: 24px; }

    /* ▼ ルビ（フレックスでルビを上に表示） */
    ruby {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    vertical-align: top !important;
    line-height: 1.2 !important;
    margin: 0 !important;
    padding: 0 !important;
    }

    /* ▼ ルビサイズクラス（例） */
    .ruby-XXXS_S { --ruby-font-size: 30%; }
    .ruby-XXS_S  { --ruby-font-size: 30%; }
    .ruby-XS_S   { --ruby-font-size: 30%; }
    .ruby-S_S    { --ruby-font-size: 40%; }
    .ruby-M_M    { --ruby-font-size: 50%; }
    .ruby-L_L    { --ruby-font-size: 60%; }
    .ruby-XL_L   { --ruby-font-size: 70%; }
    .ruby-XXL_L  { --ruby-font-size: 80%; }

    /* ▼ 追加マイナス余白（ルビサイズ別に上書き） */
    rt {
    display: block !important;
    font-size: var(--ruby-font-size);
    color: var(--ruby-color);
    line-height: 1.05;/*ルビを改行するケースにおけるルビの行間*/
    text-align: center;
    }
    rt.ruby-XXXS_S {
    margin-top: -0em !important;/*結局ここは0が一番良かった。 */
    transform: translateY(-6.6em) !important;/* ルビの高さ位置はここで調節する。 */
    }    
    rt.ruby-XXS_S {
    margin-top: -0em !important;/*結局ここは0が一番良かった。 */
    transform: translateY(-5.6em) !important;/* ルビの高さ位置はここで調節する。 */
    }
    rt.ruby-XS_S {
    transform: translateY(-4.6em) !important;
    }
    rt.ruby-S_S {
    transform: translateY(-3.7em) !important;
    }
    rt.ruby-M_M {
    transform: translateY(-3.1em) !important;
    }
    rt.ruby-L_L {
    transform: translateY(-2.8em) !important;
    }
    rt.ruby-XL_L {
    transform: translateY(-2.5em) !important;
    }
    rt.ruby-XXL_L {
    transform: translateY(-2.3em) !important;
    }

</style>
</head>
<body>
<p class="text-M_M">
"""
        ruby_style_tail = """</p>
</body>
</html>"""

    elif format_type in ('HTML格式','HTML格式_汉字替换'):
        # ルビのスタイルは最小限
        ruby_style_head = """<style>
ruby rt {
    color: blue;
}
</style>
"""
        ruby_style_tail = "<br>"
    else:
        ruby_style_head = ""
        ruby_style_tail = ""

    replaced_text = ruby_style_head + replaced_text + ruby_style_tail

    # 最終的にファイルへ書き出す
    with open(OUTPUT_HTML_FILE, "w", encoding="utf-8") as h:
        h.write(replaced_text)

    print(f"[完了] 変換結果を '{OUTPUT_HTML_FILE}' に保存しました。")


if __name__ == '__main__':
    # Windows などでマルチプロセスを正常に動かすため
    multiprocessing.set_start_method('spawn', force=True)

    main()
