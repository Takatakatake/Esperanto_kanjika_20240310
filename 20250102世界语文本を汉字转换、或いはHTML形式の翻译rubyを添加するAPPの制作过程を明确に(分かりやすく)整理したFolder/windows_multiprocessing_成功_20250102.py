import os
import re
import json
import unicodedata
import multiprocessing

# 字上符付き文字の表記形式変換用の辞書型配列
esperanto_to_x = { "ĉ": "cx", "ĝ": "gx", "ĥ": "hx", "ĵ": "jx", "ŝ": "sx", "ŭ": "ux",
                "Ĉ": "Cx", "Ĝ": "Gx", "Ĥ": "Hx", "Ĵ": "Jx", "Ŝ": "Sx", "Ŭ": "Ux",
                "c^": "cx", "g^": "gx", "h^": "hx", "j^": "jx", "s^": "sx", "u^": "ux",
                    "C^": "Cx", "G^": "Gx", "H^": "Hx", "J^": "Jx", "S^": "Sx", "U^": "Ux"}
x_to_jijofu={'cx': 'ĉ', 'gx': 'ĝ', 'hx': 'ĥ', 'jx': 'ĵ', 'sx': 'ŝ', 'ux': 'ŭ', 'Cx': 'Ĉ',
            'Gx': 'Ĝ', 'Hx': 'Ĥ', 'Jx': 'Ĵ', 'Sx': 'Ŝ', 'Ux': 'Ŭ'}
x_to_hat={'cx': 'c^', 'gx': 'g^', 'hx': 'h^', 'jx': 'j^', 'sx': 's^', 'ux': 'u^', 'Cx': 'C^',
        'Gx': 'G^', 'Hx': 'H^', 'Jx': 'J^', 'Sx': 'S^', 'Ux': 'U^'}
# 字上符付き文字の表記形式変換用の関数
def replace_esperanto_chars(text,letter_dictionary):
    for esperanto_char, x_char in letter_dictionary.items():
        text = text.replace(esperanto_char, x_char)
    return text

# ユーザーに出力形式を選択してもらう
format_type = 'HTML形式＿ルビサイズ調節'
#'括弧形式'

## multiprocessingのための関数群　テキストを行数によって設定プロセス数(num_processes)に等分割して、それぞれのプロセスで並列に置換処理を実行してから、再度分割したテキストを結合する。
def process_segment(lines, replacements, imported_data_replacements_list_for_2char):
    # 文字列のリストを結合してから置換処理を実行 linesには\nが含まれていない状態の文字列群が格納されている。
    segment = '\n'.join(lines)
    segment = enhanced_safe_replace_func_expanded_for_2char_roots(segment, replacements, imported_data_replacements_list_for_2char)#ここでenhanced_safe_replace_func_expanded_for_2char_roots関数の実行
    return segment
def parallel_process(text, num_processes,replacements, imported_data_replacements_list_for_2char):
    #テキストを行で分割
    lines = text.split('\n')
    num_lines = len(lines)
    lines_per_process = num_lines // num_processes
    #各プロセスに割り当てる行のリストを決定
    ranges = [(i * lines_per_process, (i + 1) * lines_per_process) for i in range(num_processes)]
    ranges[-1] = (ranges[-1][0], num_lines)  #最後のプロセスが残り全てを処理
    with multiprocessing.Pool(processes=num_processes) as pool:
        # 並列処理を実行
        results = pool.starmap(process_segment, [(lines[start:end], replacements, imported_data_replacements_list_for_2char) for start, end in ranges])
    # 結果を結合
    return '\n'.join(result for result in results)

def find_strings_in_text(text):
    # 正規表現パターンを定義
    pattern = re.compile(r'%%(.{1,50}?)%%')
    matches = []
    used_indices = set()
    # 正規表現のマッチを見つける
    for match in pattern.finditer(text):
        start, end = match.span()
        # 重複する%%を避けるためにインデックスをチェック
        if start not in used_indices and end-2 not in used_indices:  # end-2 because of double %%
            matches.append(match.group(1))
            # インデックスを使用済みセットに追加
            used_indices.update(range(start, end))
    return matches

def import_placeholders(filename):
    with open(filename, 'r') as file:
        placeholders = [line.strip() for line in file if line.strip()]
    return placeholders

def create_replacements(text, placeholders):
    # テキストから%%で囲まれた部分を抽出
    matches = find_strings_in_text(text)
    replacements_list_for_intact_parts = []
    # プレースホルダーとマッチを対応させる
    for i, match in enumerate(matches):
        if i < len(placeholders):
            replacements_list_for_intact_parts.append([f"%%{match}%%", placeholders[i]])
        else:
            break  # プレースホルダーが足りなくなった場合は終了
    return replacements_list_for_intact_parts

# プレースホルダーを用いた文字列置換関数
def enhanced_safe_replace_func_expanded_for_2char_roots(text, replacements, imported_data_replacements_list_for_2char):
    valid_replacements = {}
    for old, new, placeholder in replacements:
        if old in text:
            text = text.replace(old, placeholder)# 置換前の文字列を一旦プレースホルダーに置き換える。
            valid_replacements[placeholder] = new
# ここで、2文字の語根の置換を実施することとした(202412の変更)。  &%
    valid_replacements_for_2char_roots = {}
    for old, new, placeholder in imported_data_replacements_list_for_2char:
        if old in text:
            text = text.replace(old, placeholder)
            valid_replacements_for_2char_roots[placeholder] = new
    valid_replacements_for_2char_roots_2 = {}
    for old, new, placeholder in imported_data_replacements_list_for_2char:
        if old in text:
            place_holder_second="!"+placeholder+"!"##2回目のplace_holderは少し変更を加えたほうが良いはず。
            text = text.replace(old, place_holder_second)
            valid_replacements_for_2char_roots_2[place_holder_second] = new
    for place_holder_second, new in reversed(valid_replacements_for_2char_roots_2.items()):##ここで、reverseにすることがポイント。
        text = text.replace(place_holder_second, new)# プレースホルダーを置換後の文字列に置き換える。
    for placeholder, new in reversed(valid_replacements_for_2char_roots.items()):
        text = text.replace(placeholder, new)# プレースホルダーを置換後の文字列に置き換える。
    for placeholder, new in valid_replacements.items():
        text = text.replace(placeholder, new)
    return text

# windowsでは、相対座標がうまく認識されないことがあるので、PATHの設定には注意が必要。# 'C:/Users/n_c-k/Documents/20241231世界语文本を汉字转换、或いはHTML形式の翻译rubyを添加するAPPの制作过程を明确に(分かりやすく)整理したFolder/
with open('./例文4.txt','r', encoding='utf-8') as g:
    ll=g.read()
text2=replace_esperanto_chars(ll,esperanto_to_x)
placeholders = import_placeholders('./placeholders_&%1854&%-&%9834&%_文字列置換skip用.txt')
replacements_list_for_intact_parts = create_replacements(text2, placeholders)
sorted_replacements_list_for_intact_parts = sorted(replacements_list_for_intact_parts, key=lambda x: len(x[0]), reverse=True)
for original, place_holder_ in sorted_replacements_list_for_intact_parts:
    text2 = text2.replace(original, place_holder_)
    
if __name__ == '__main__':
    multiprocessing.set_start_method('spawn', force=True)
    # 必要なファイルを読み込み
    with open('./最終的な置換用のリスト(replacements_final_list).json', 'r', encoding='utf-8') as f:
        replacements_final_list_2 = json.load(f)
    with open('./replacements_list_for_2char.json', 'r', encoding='utf-8') as f:
        imported_data_replacements_list_for_2char = json.load(f)
    with open('./例文4.txt', 'r', encoding='utf-8') as f:
        input_text = f.read()

    text3=parallel_process(text2, 2,replacements_final_list_2, imported_data_replacements_list_for_2char)

    for original, place_holder_ in sorted_replacements_list_for_intact_parts:
        text3 = text3.replace(place_holder_, original.replace("%%",""))
    # 改行を <br> に変換
    text3 = text3.replace("\n", "<br>\n")
    text3 = replace_esperanto_chars(text3,x_to_jijofu)
    # 連続する空白を &nbsp; に変換
    text3 = re.sub(r"  ", "&nbsp;&nbsp;", text3)  # 2つ以上の空白を変換
    # html形式におけるルビサイズの変更形式
    ruby_style="""<style>
        .text-S_S_S {font-size: 12px;}
        .text-M_M_M {font-size: 16px;}
        .text-L_L_L {font-size: 20px;}
        .text-X_X_X {font-size: 24px;}
        .ruby-S_S_S { font-size: 0.33em; }
        .ruby-M_M_M { font-size: 0.45em; }
        .ruby-L_L_L { font-size: 0.60em; }
        .ruby-X_X_X { font-size: 0.70em; }

        ruby {
        display: inline-block;
        position: relative; /* 相対位置 */
        white-space: nowrap; /* 改行防止 */
    }
    rt {
    position: absolute;
    top: -0.80em;
    left: 50%; /* 左端を親要素の中央に合わせる */
    transform: translateX(-50%); /* 中央に揃える */
    line-height: 2.1;
    }

    </style>
    <p class="text-M_M_M">
    """
    ruby_style_tail="""

    </p>
    """
    text4=ruby_style+text3+ruby_style_tail

    with open('./出力_windows_multipleprocessing.html','w', encoding='utf-8') as h:
        h.write(text4)