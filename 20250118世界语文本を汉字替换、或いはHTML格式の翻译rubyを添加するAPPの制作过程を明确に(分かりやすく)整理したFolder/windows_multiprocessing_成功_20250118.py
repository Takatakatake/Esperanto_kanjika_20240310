# windowsでは、相対座標がうまく認識されないことがあるので、PATHの設定には注意が必要。何とかこのpythonファイルがあるディレクトリ上で実行する方法を模索する必要がある。
# Multi-processing が実行される行以降を  ""if __name__ == '__main__':"" ブロックインデント内に収め、同ブロック内にmultiprocessing.set_start_method('spawn', force=True)という設定行も追加することでうまく動作した。
# if __name__ == '__main__':
#     multiprocessing.set_start_method('spawn', force=True)

import os
import re
import json
import unicodedata
import multiprocessing

num_processes=4
text_repeat_times=10

# 字上符付き文字の表記形式変換用の辞書型配列
x_to_circumflex = {'cx': 'ĉ', 'gx': 'ĝ', 'hx': 'ĥ', 'jx': 'ĵ', 'sx': 'ŝ', 'ux': 'ŭ','Cx': 'Ĉ', 'Gx': 'Ĝ', 'Hx': 'Ĥ', 'Jx': 'Ĵ', 'Sx': 'Ŝ', 'Ux': 'Ŭ'}
circumflex_to_x = {'ĉ': 'cx', 'ĝ': 'gx', 'ĥ': 'hx', 'ĵ': 'jx', 'ŝ': 'sx', 'ŭ': 'ux','Ĉ': 'Cx', 'Ĝ': 'Gx', 'Ĥ': 'Hx', 'Ĵ': 'Jx', 'Ŝ': 'Sx', 'Ŭ': 'Ux'}
x_to_hat = {'cx': 'c^', 'gx': 'g^', 'hx': 'h^', 'jx': 'j^', 'sx': 's^', 'ux': 'u^','Cx': 'C^', 'Gx': 'G^', 'Hx': 'H^', 'Jx': 'J^', 'Sx': 'S^', 'Ux': 'U^'}
hat_to_x = {'c^': 'cx', 'g^': 'gx', 'h^': 'hx', 'j^': 'jx', 's^': 'sx', 'u^': 'ux','C^': 'Cx', 'G^': 'Gx', 'H^': 'Hx', 'J^': 'Jx', 'S^': 'Sx', 'U^': 'Ux'}
hat_to_circumflex = {'c^': 'ĉ', 'g^': 'ĝ', 'h^': 'ĥ', 'j^': 'ĵ', 's^': 'ŝ', 'u^': 'ŭ','C^': 'Ĉ', 'G^': 'Ĝ', 'H^': 'Ĥ', 'J^': 'Ĵ', 'S^': 'Ŝ', 'U^': 'Ŭ'}
circumflex_to_hat = {'ĉ': 'c^', 'ĝ': 'g^', 'ĥ': 'h^', 'ĵ': 'j^', 'ŝ': 's^', 'ŭ': 'u^','Ĉ': 'C^', 'Ĝ': 'G^', 'Ĥ': 'H^', 'Ĵ': 'J^', 'Ŝ': 'S^', 'Ŭ': 'U^'}

# 字上符付き文字の表記形式変換用の関数
def replace_esperanto_chars(text,letter_dictionary):
    for esperanto_char, x_char in letter_dictionary.items():
        text = text.replace(esperanto_char, x_char)
    return text

# ユーザーに出力形式を選択してもらう
format_type = 'HTML格式_Ruby文字_大小调整'
#'括弧形式'

# multiprocessingのための関数群　テキストを行数によって設定プロセス数(num_processes)に等分割して、それぞれのプロセスで並列に置換処理を実行してから、再度分割したテキストを結合する。
import multiprocessing
def process_segment(lines, replacements, imported_data_replacements_list_for_2char):
    # 文字列のリストを結合してから置換処理を実行 linesには\nが含まれていない状態の文字列群が格納されている。
    segment = '\n'.join(lines)
    segment = enhanced_safe_replace_func_expanded_for_2char_roots(segment, replacements, imported_data_replacements_list_for_2char)# ここでenhanced_safe_replace_func_expanded_for_2char_roots関数の実行
    return segment
def parallel_process(text, num_processes,replacements_final_list, imported_data_replacements_list_for_2char):
    # テキストを行で分割
    lines = text.split('\n')
    num_lines = len(lines)
    lines_per_process = num_lines // num_processes
    # 各プロセスに割り当てる行のリストを決定
    ranges = [(i * lines_per_process, (i + 1) * lines_per_process) for i in range(num_processes)]
    ranges[-1] = (ranges[-1][0], num_lines)  # 最後のプロセスが残り全てを処理
    with multiprocessing.Pool(processes=num_processes) as pool:
        # 並列処理を実行
        results = pool.starmap(process_segment, [(lines[start:end], replacements_final_list, imported_data_replacements_list_for_2char) for start, end in ranges])
    # 結果を結合
    return '\n'.join(result for result in results)

def unify_halfwidth_spaces(text):
    """全角スペース(U+3000)は変更せず、半角スペースと視覚的に区別がつきにくい空白文字を
        ASCII半角スペース(U+0020)に統一する。連続した空白は1文字ずつ置換する。"""
    pattern = r"[\u00A0\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A]"# 対象とする空白文字をまとめたパターン
    return re.sub(pattern, " ", text)# マッチした部分を半角スペースに置換

# '%'で囲まれた50文字以内の部分を同定し、文字列(漢字)置換せずにそのまま保存しておくための関数群
def find_strings_in_text(text):
    # 正規表現パターンを定義
    pattern = re.compile(r'%(.{1,50}?)%')# re.DOTALLで、任意の文字列に"改行"も含むようにできる。(今はしない。)
    matches = []
    used_indices = set()

    # 正規表現のマッチを見つける
    for match in pattern.finditer(text):
        start, end = match.span()
        # 重複する%を避けるためにインデックスをチェック
        if start not in used_indices and end-2 not in used_indices:  # end-2 because of double %
            matches.append(match.group(1))
            # インデックスを使用済みセットに追加
            used_indices.update(range(start, end))
    return matches

def create_replacements_list_for_intact_parts(text, placeholders):
    # テキストから%で囲まれた部分を抽出
    matches = find_strings_in_text(text)
    replacements_list_for_intact_parts = []
    # プレースホルダーとマッチを対応させる
    for i, match in enumerate(matches):
        if i < len(placeholders):
            replacements_list_for_intact_parts.append([f"%{match}%", placeholders[i]])
        else:
            break  # プレースホルダーが足りなくなった場合は終了
    return replacements_list_for_intact_parts

def import_placeholders(filename):
    with open(filename, 'r') as file:
        placeholders = [line.strip() for line in file if line.strip()]
    return placeholders

# プレースホルダーを用いた文字列(漢字)置換関数
def enhanced_safe_replace_func_expanded_for_2char_roots(text, replacements, imported_data_replacements_list_for_2char):
    valid_replacements = {}
    for old, new, placeholder in replacements:
        if old in text:
            text = text.replace(old, placeholder)# 置換前の文字列を一旦プレースホルダーに置き換える。
            valid_replacements[placeholder] = new
# ここで、2文字の語根の文字列(漢字)置換を実施することとした(202412の変更)。  &%
    valid_replacements_for_2char_roots = {}
    for old, new, placeholder in imported_data_replacements_list_for_2char:
        if old in text:
            text = text.replace(old, placeholder)
            valid_replacements_for_2char_roots[placeholder] = new
    valid_replacements_for_2char_roots_2 = {}
    for old, new, placeholder in imported_data_replacements_list_for_2char:
        if old in text:
            place_holder_second="!"+placeholder+"!"# 2回目のplace_holderは少し変更を加えたほうが良いはず。
            text = text.replace(old, place_holder_second)
            valid_replacements_for_2char_roots_2[place_holder_second] = new
    for place_holder_second, new in reversed(valid_replacements_for_2char_roots_2.items()):# ここで、reverseにすることがポイント。
        text = text.replace(place_holder_second, new)# プレースホルダーを置換後の文字列に置き換える。
    for placeholder, new in reversed(valid_replacements_for_2char_roots.items()):
        text = text.replace(placeholder, new)# プレースホルダーを置換後の文字列に置き換える。
    for placeholder, new in valid_replacements.items():
        text = text.replace(placeholder, new)
    return text


import re
def find_strings_in_text_for_localized_replacement(text):
    # 正規表現パターンを定義
    pattern = re.compile(r'@(.{1,18}?)@')
    matches = []
    used_indices = set()

    # 正規表現のマッチを見つける
    for match in pattern.finditer(text):
        start, end = match.span()
        # 重複する@を避けるためにインデックスをチェック
        if start not in used_indices and end-2 not in used_indices:  # end-2 because of double @
            matches.append(match.group(1))
            # インデックスを使用済みセットに追加
            used_indices.update(range(start, end))
    return matches
# 置換に用いる関数。正規表現、C++など様々な形式の置換を試したが、pythonでplaceholder(占位符)を用いる形式の置換が、最も処理が高速であった。(しかも大変シンプルでわかりやすい。)
def safe_replace(text, replacements):
    valid_replacements = {}
    # 置換対象(old)をplaceholderに一時的に置換
    for old, new, placeholder in replacements:
        if old in text:
            text = text.replace(old, placeholder)
            valid_replacements[placeholder] = new# 後で置換後の文字列(new)に置換し直す必要があるplaceholderを辞書(valid_replacements)に記録しておく。
    # placeholderを置換後の文字列(new)に置換)
    for placeholder, new in valid_replacements.items():
        text = text.replace(placeholder, new)
    return text
def create_replacements_list_for_localized_replacement(text, placeholders, replacements_list_for_localized_string):
    # テキストから@で囲まれた部分を抽出
    matches = find_strings_in_text_for_localized_replacement(text)
    tmp_replacements_list_for_localized_string = []
    # プレースホルダーとマッチを対応させる
    for i, match in enumerate(matches):
        if i < len(placeholders):
            replaced_match=safe_replace(match, replacements_list_for_localized_string)# ここで、まず１つplaceholdersが要る。
            # print(match,replaced_match)
            tmp_replacements_list_for_localized_string.append([f"@{match}@", placeholders[i],replaced_match])# ここに、置換後の
        else:
            break  # プレースホルダーが足りなくなった場合は終了
    return tmp_replacements_list_for_localized_string


placeholders_for_skipping_replacements = import_placeholders('占位符(placeholders)_%1854%-%4934%_文字列替换skip用.txt')# placeholderに'%'が含まれる必要は全く無いが、雰囲気を揃えるために敢えて入れた。
placeholders_for_localized_replacement = import_placeholders('占位符(placeholders)_@5134@-@9728@_局部文字列替换结果捕捉用.txt')# placeholderに'@'が含まれる必要は全く無いが、雰囲気を揃えるために敢えて入れた。

with open('./最终的な替换用のリスト(列表)型配列(replacements_final_list).json', 'r', encoding='utf-8') as f:
    replacements_final_list = json.load(f)
with open('./局部文字替换用のリスト(列表)型配列(replacements_list_for_localized_string).json', 'r', encoding='utf-8') as f:
    replacements_list_for_localized_string = json.load(f)
with open('./二文字词根替换用のリスト(列表)型配列(replacements_list_for_2char).json', 'r', encoding='utf-8') as f:
    imported_data_replacements_list_for_2char = json.load(f)

# windowsでは、相対座標がうまく認識されないことがあるので、PATHの設定には注意が必要。何とかこのpythonファイルがあるディレクトリ上で実行する方法を模索する必要がある。
with open('例句_Esperanto文本.txt','r', encoding='utf-8') as g:
    text0=g.read()*text_repeat_times
text = unify_halfwidth_spaces(text0)# 半角スペースと視覚的に区別がつきにくい特殊な空白文字を標準的なASCII半角スペース(U+0020)に置換する。 ただし、全角スペース(U+3000)は置換対象に含めていない。
text=replace_esperanto_chars(text0,x_to_circumflex)
text=replace_esperanto_chars(text,hat_to_circumflex)

replacements_list_for_intact_parts = create_replacements_list_for_intact_parts(text, placeholders_for_skipping_replacements)
sorted_replacements_list_for_intact_parts = sorted(replacements_list_for_intact_parts, key=lambda x: len(x[0]), reverse=True)
for original, place_holder_ in sorted_replacements_list_for_intact_parts:
    text = text.replace(original, place_holder_)# いいのか→多分大丈夫。

tmp_replacements_list_for_localized_string_2 = create_replacements_list_for_localized_replacement(text, placeholders_for_localized_replacement, replacements_list_for_localized_string)
sorted_replacements_list_for_localized_string = sorted(tmp_replacements_list_for_localized_string_2, key=lambda x: len(x[0]), reverse=True)
for original, place_holder_, replaced_original in sorted_replacements_list_for_localized_string:
    text = text.replace(original, place_holder_)


if __name__ == '__main__':
    multiprocessing.set_start_method('spawn', force=True)
    # 必要なファイルを読み込み
    text=parallel_process(text, num_processes,replacements_final_list, imported_data_replacements_list_for_2char)

    for original, place_holder_, replaced_original in sorted_replacements_list_for_localized_string:
        text = text.replace(place_holder_, replaced_original.replace("@",""))

    for original, place_holder_ in sorted_replacements_list_for_intact_parts:
        text = text.replace(place_holder_, original.replace("%",""))

    if format_type in ('HTML格式_Ruby文字_大小调整','HTML格式_Ruby文字_大小调整_汉字替换','HTML格式','HTML格式_汉字替换'):
        # 改行を <br> に変換
        text = text.replace("\n", "<br>\n")
        # 連続する空白を &nbsp; に変換
        text = re.sub(r"   ", "&nbsp;&nbsp;&nbsp;", text)  # 3つ以上の空白を変換
        text = re.sub(r"  ", "&nbsp;&nbsp;", text)  # 2つ以上の空白を変換

    if format_type in ('HTML格式_Ruby文字_大小调整','HTML格式_Ruby文字_大小调整_汉字替换'):
        # html形式におけるルビサイズの変更形式
        ruby_style_head="""<style>
    .text-S_S_S {font-size: 12px;}
    .text-M_M_M {font-size: 16px;}
    .text-L_L_L {font-size: 20px;}
    .text-X_X_X {font-size: 24px;}
    .ruby-XS_S_S { font-size: 0.30em; } /* Extra Small */
    .ruby-S_S_S  { font-size: 0.40em; } /* Small */
    .ruby-M_M_M  { font-size: 0.50em; } /* Medium */
    .ruby-L_L_L  { font-size: 0.60em; } /* Large */
    .ruby-XL_L_L { font-size: 0.70em; } /* Extra Large */
    .ruby-XXL_L_L { font-size: 0.80em; } /* Double Extra Large */

    ruby {
    display: inline-block;
    position: relative; /* 相対位置 */
    white-space: nowrap; /* 改行防止 */
    line-height: 1.9;
    }
    rt {
    position: absolute;
    top: -0.75em;
    left: 50%; /* 左端を親要素の中央に合わせる */
    transform: translateX(-50%); /* 中央に揃える */
    line-height: 2.1;
    color: blue; 
    }
    rt.ruby-XS_S_S { top: -0.20em; } /* ルビサイズに応じて、ルビを表示する高さを変える。 */
    rt.ruby-S_S_S  { top: -0.30em; }
    rt.ruby-M_M_M  { top: -0.40em; }
    rt.ruby-L_L_L  { top: -0.50em; }
    rt.ruby-XL_L_L { top: -0.65em; }
    rt.ruby-XXL_L_L{ top: -0.80em; }

    </style>
    <p class="text-M_M_M">
    """
        ruby_style_tail = "<br>\n</p>"

    elif format_type in ('HTML格式','HTML格式_汉字替换'):
        # ルビのスタイルは最小限
        ruby_style_head = """<style>
    ruby rt {
    color: blue;
    }
    </style>
    """
        ruby_style_tail="<br>"
    else:
        ruby_style_head=""
        ruby_style_tail=""

    text=ruby_style_head+text+ruby_style_tail


    # text3=parallel_procepre_replacements_dict_1(text2*1,1, replacements_final_list)
    with open('Esperanto文本_替换结果_多重处理_windows.html','w', encoding='utf-8') as h:
        h.write(text)