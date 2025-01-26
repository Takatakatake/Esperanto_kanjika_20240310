# windowsでは、相対座標がうまく認識されないことがあるので、PATHの設定には注意が必要。何とかこのpythonファイルがあるディレクトリ上で実行する方法を模索する必要がある。
# Multi-processing が実行される行以降を  ""if __name__ == '__main__':"" ブロックインデント内に収め、同ブロック内にmultiprocessing.set_start_method('spawn', force=True)という設定行も追加することでうまく動作した。
# if __name__ == '__main__':
#     multiprocessing.set_start_method('spawn', force=True)

import os
import re
import json
import multiprocessing
from typing import List, Dict, Tuple, Optional  # List, Dict, Tuple, (Optional) など型ヒントを一括でインポート

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
def replace_esperanto_chars(text, char_dict: Dict[str, str]) -> str:
    for original_char, converted_char in char_dict.items():
        text = text.replace(original_char, converted_char)
    return text

# ユーザーに出力形式を選択してもらう
format_type = 'HTML格式_Ruby文字_大小调整'
#'括弧形式'

def unify_halfwidth_spaces(text: str) -> str:
    """全角スペース(U+3000)は変更せず、半角スペースと視覚的に区別がつきにくい空白文字を
        ASCII半角スペース(U+0020)に統一する。連続した空白は1文字ずつ置換する。"""
    pattern = r"[\u00A0\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A]"# 対象とする空白文字をまとめたパターン
    return re.sub(pattern, " ", text)# マッチした部分を標準的な半角スペースに置換

# '%'で囲まれた50文字以内の部分を同定し、文字列(漢字)置換せずにそのまま保存しておくための関数群
def find_strings_in_text(text: str) -> List[str]:
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

def create_replacements_list_for_intact_parts(text: str, placeholders: List[str]) -> List[Tuple[str, str]]:
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

def import_placeholders(filename: str) -> List[str]:# placeholder(占位符)をインポートするためだけの関数
    with open(filename, 'r') as file:
        placeholders = [line.strip() for line in file if line.strip()]
    return placeholders

from bs4 import BeautifulSoup, NavigableString
from bs4.element import Tag

def wrap_text_with_ruby(html_string: str, chunk_size: int = 10) -> str:
    """
    HTML文字列内の「一切HTML修飾がなされていない生テキスト」を対象に、
    10文字ごと(<chunk_size>ごと)に<ruby>で囲む関数。
    
    1) <ruby>や<rt>などのタグ内にある（＝すでに修飾済みの）テキストはスキップ。
    2) テキストが10文字未満の場合も、必ず<ruby>で囲む。
    """
    soup = BeautifulSoup(html_string, 'html.parser')
    
    def process_element(element: Tag) -> None:
        for child in list(element.children):
            # (A) テキストノードかどうか判定
            if isinstance(child, NavigableString):
                text = str(child)
                # 空白や改行のみの場合はスキップ
                if not text.strip():
                    continue

                # (B) 親要素のいずれかが <ruby> や <rt> の場合は「既にHTML修飾あり」とみなしてスキップ
                parents = [p.name for p in child.parents if p.name]
                # 例：['body', 'div', 'ruby'] などのリスト
                # ruby/rt が親階層に含まれていればスキップ
                if any(tag in ['ruby', 'rt'] for tag in parents):
                    continue

                # (C) テキストを chunk_size ごとに分割（10文字未満も1チャンクとしてラッピング）
                chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
                
                # (D) 分割した各チャンクを <ruby>タグで囲み、新しいタグとして置換
                new_tags = []
                for chunk in chunks:
                    # 半角スペースを &nbsp; に、全角スペースを &nbsp;&nbsp; に置換
                    chunk = chunk.replace(" ", "&nbsp;")
                    chunk = chunk.replace("　", "&nbsp;&nbsp;")
                    ruby_tag = soup.new_tag('ruby')
                    ruby_tag.string = chunk
                    new_tags.append(ruby_tag)
                
                # 元のテキストノードを連続する<ruby>タグに置換する
                child.replace_with(*new_tags)

            # (E) <script>や<style>はスキップ
            elif child.name and child.name.lower() in ['script', 'style']:
                continue
            else:
                # 再帰的に子要素を処理
                process_element(child)
    
    # ルート要素から再帰的に処理
    process_element(soup)
    final_str = str(soup).replace("&amp;nbsp;", "&nbsp;")# 
    return final_str


# 文字列(漢字)置換に用いる'replacements'リストと占位符(placeholders)を呼び出す。
with open("最终的な替换用リスト(列表)(合并3个JSON文件).json", "r", encoding="utf-8") as f:
    combined_3_replacements_lists = json.load(f)
replacements_final_list = combined_3_replacements_lists.get("全域替换用のリスト(列表)型配列(replacements_final_list)", None)
replacements_list_for_localized_string = combined_3_replacements_lists.get("局部文字替换用のリスト(列表)型配列(replacements_list_for_localized_string)", None)
replacements_list_for_2char = combined_3_replacements_lists.get("二文字词根替换用のリスト(列表)型配列(replacements_list_for_2char)", None)

placeholders_for_skipping_replacements = import_placeholders('占位符(placeholders)_%1854%-%4934%_文字列替换skip用.txt')# placeholderに'%'が含まれる必要は全く無いが、雰囲気を揃えるために敢えて入れた。
placeholders_for_localized_replacement = import_placeholders('占位符(placeholders)_@5134@-@9728@_局部文字列替换结果捕捉用.txt')# placeholderに'@'が含まれる必要は全く無いが、雰囲気を揃えるために敢えて入れた。


def orchestrate_comprehensive_esperanto_text_replacement(
    text, placeholders_for_skipping_replacements: List[str] = placeholders_for_skipping_replacements, replacements_list_for_localized_string: List[Tuple[str, str, str]] = replacements_list_for_localized_string, 
    placeholders_for_localized_replacement: List[str] = placeholders_for_localized_replacement, replacements_final_list: List[Tuple[str, str, str]] = replacements_final_list, 
    replacements_list_for_2char: List[Tuple[str, str, str]] = replacements_list_for_2char, format_type: str = format_type)-> str:
    text = unify_halfwidth_spaces(text)# 半角スペースと視覚的に区別がつきにくい特殊な空白文字を標準的なASCII半角スペース(U+0020)に置換する。 ただし、全角スペース(U+3000)は置換対象に含めていない。
    text = replace_esperanto_chars(text,hat_to_circumflex)
    text = replace_esperanto_chars(text,x_to_circumflex)

    replacements_list_for_intact_parts = create_replacements_list_for_intact_parts(text, placeholders_for_skipping_replacements)
    sorted_replacements_list_for_intact_parts = sorted(replacements_list_for_intact_parts, key=lambda x: len(x[0]), reverse=True)
    for original, place_holder_ in sorted_replacements_list_for_intact_parts:
        text = text.replace(original, place_holder_)# いいのか→多分大丈夫。

    tmp_replacements_list_for_localized_string_2 = create_replacements_list_for_localized_replacement(text, placeholders_for_localized_replacement, replacements_list_for_localized_string)
    sorted_replacements_list_for_localized_string = sorted(tmp_replacements_list_for_localized_string_2, key=lambda x: len(x[0]), reverse=True)
    for original, place_holder_, replaced_original in sorted_replacements_list_for_localized_string:
        text = text.replace(original, place_holder_)

    valid_replacements = {}
    for old, new, placeholder in replacements_final_list:
        if old in text:
            text = text.replace(old, placeholder)# 置換前の文字列を一旦プレースホルダーに置き換える。
            valid_replacements[placeholder] = new
    # ここで、2文字の語根の文字列(漢字)置換を実施することとした(202412の変更)。  &%
    valid_replacements_for_2char_roots = {}
    for old, new, placeholder in replacements_list_for_2char:
        if old in text:
            text = text.replace(old, placeholder)
            valid_replacements_for_2char_roots[placeholder] = new
    valid_replacements_for_2char_roots_2 = {}
    for old, new, placeholder in replacements_list_for_2char:
        if old in text:
            place_holder_second="!"+placeholder+"!"# 2回目のplace_holderは少し変更を加えたほうが良いはず。
            text = text.replace(old, place_holder_second)
            valid_replacements_for_2char_roots_2[place_holder_second] = new
    # print(text)
    for place_holder_second, new in reversed(valid_replacements_for_2char_roots_2.items()):# ここで、reverseにすることがポイント。
        text = text.replace(place_holder_second, new)# プレースホルダーを置換後の文字列に置き換える。
    for placeholder, new in reversed(valid_replacements_for_2char_roots.items()):
        text = text.replace(placeholder, new)# プレースホルダーを置換後の文字列に置き換える。
    for placeholder, new in valid_replacements.items():
        text = text.replace(placeholder, new)

    for original, place_holder_, replaced_original in sorted_replacements_list_for_localized_string:
        text = text.replace(place_holder_, replaced_original.replace("@",""))

    for original, place_holder_ in sorted_replacements_list_for_intact_parts:
        text = text.replace(place_holder_, original.replace("%",""))
    if "HTML" in format_type:
        text = text.replace("\n", "<br>\n")
        text = wrap_text_with_ruby(text, chunk_size=10)
        text = re.sub(r"   ", "&nbsp;&nbsp;&nbsp;", text)  # 3つ以上の空白を変換
        text = re.sub(r"  ", "&nbsp;&nbsp;", text)  # 2つ以上の空白を変換
    
    return text

# multiprocessingのための関数群　テキストを行数によって設定プロセス数(num_processes)に等分割して、それぞれのプロセスで並列に置換処理を実行してから、再度分割したテキストを結合する。
import multiprocessing
def process_segment(lines: List[str],
                    
    placeholders_for_skipping_replacements: List[str] = placeholders_for_skipping_replacements, replacements_list_for_localized_string: List[Tuple[str, str, str]] = replacements_list_for_localized_string, 
    placeholders_for_localized_replacement: List[str] = placeholders_for_localized_replacement, replacements_final_list: List[Tuple[str, str, str]] = replacements_final_list, 
    replacements_list_for_2char: List[Tuple[str, str, str]] = replacements_list_for_2char, format_type: str = format_type ) -> str:

    # 文字列のリストを結合してから置換処理を実行 linesには\nが含まれていない状態の文字列群が格納されている。
    segment = '\n'.join(lines)
    segment = orchestrate_comprehensive_esperanto_text_replacement(
    segment, placeholders_for_skipping_replacements, replacements_list_for_localized_string, 
    placeholders_for_localized_replacement, replacements_final_list, replacements_list_for_2char, format_type)# ここでorchestrate_comprehensive_esperanto_text_replacement関数の実行!

    return segment

# def orchestrate_comprehensive_esperanto_text_replacement(
#     text, placeholders_for_skipping_replacements: List[str] = placeholders_for_skipping_replacements, replacements_list_for_localized_string: List[Tuple[str, str, str]] = replacements_list_for_localized_string, 
#     placeholders_for_localized_replacement: List[str] = placeholders_for_localized_replacement, replacements_final_list: List[Tuple[str, str, str]] = replacements_final_list, 
#     replacements_list_for_2char: List[Tuple[str, str, str]] = replacements_list_for_2char, format_type: str = format_type)-> str:

def parallel_process(text: str, num_processes: int = num_processes, 

    placeholders_for_skipping_replacements: List[str] = placeholders_for_skipping_replacements, replacements_list_for_localized_string: List[Tuple[str, str, str]] = replacements_list_for_localized_string, 
    placeholders_for_localized_replacement: List[str] = placeholders_for_localized_replacement, replacements_final_list: List[Tuple[str, str, str]] = replacements_final_list, 
    replacements_list_for_2char: List[Tuple[str, str, str]] = replacements_list_for_2char, format_type: str = format_type  ) -> str:

    # テキストを行で分割
    lines = text.split('\n')
    num_lines = len(lines)
    lines_per_process = num_lines // num_processes
    # 各プロセスに割り当てる行のリストを決定
    ranges = [(i * lines_per_process, (i + 1) * lines_per_process) for i in range(num_processes)]
    ranges[-1] = (ranges[-1][0], num_lines)  # 最後のプロセスが残り全てを処理
    with multiprocessing.Pool(processes=num_processes) as pool:
        # 並列処理を実行
        results = pool.starmap(process_segment, [(lines[start:end],) for start, end in ranges])
    # 結果を結合
    return '\n'.join(result for result in results)


import re
def find_strings_in_text_for_localized_replacement(text: str) -> List[str]:
    # 正規表現パターンを定義
    pattern = re.compile(r'@(.{1,18}?)@')# re.DOTALLで、任意の文字列に"改行"も含むようにできる。(今はしない。)
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
def safe_replace(text: str, replacements: List[Tuple[str, str, str]]) -> str:# Tupleは狭義のList
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
def create_replacements_list_for_localized_replacement(text, placeholders: List[str], 
                                                       replacements_list_for_localized_string: List[Tuple[str, str, str]] = replacements_list_for_localized_string)-> List[List[str]]:
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




# windowsでは、相対座標がうまく認識されないことがあるので、PATHの設定には注意が必要。何とかこのpythonファイルがあるディレクトリ上で実行する方法を模索する必要がある。
format_type = 'HTML格式_Ruby文字_大小调整'

with open('例句_Esperanto文本.txt','r', encoding='utf-8') as g:
    text0=g.read()*text_repeat_times

text1=parallel_process(text0, num_processes, format_type)

# parallel_process(text: str, num_processes: int = num_processes, 
#     placeholders_for_skipping_replacements: List[str] = placeholders_for_skipping_replacements, replacements_list_for_localized_string: List[Tuple[str, str, str]] = replacements_list_for_localized_string, 
#     placeholders_for_localized_replacement: List[str] = placeholders_for_localized_replacement, replacements_final_list: List[Tuple[str, str, str]] = replacements_final_list, 
#     replacements_list_for_2char: List[Tuple[str, str, str]] = replacements_list_for_2char, format_type: str = format_type  )

if format_type in ('HTML格式_Ruby文字_大小调整','HTML格式_Ruby文字_大小调整_汉字替换'):
    # html形式におけるルビサイズの変更形式
    ruby_style_head="""<!DOCTYPE html>
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

    .text-S_S_S { font-size: 12px; }
    .text-M_M_M {
      font-size: 16px; 
      font-family: Arial, sans-serif;
      line-height: 1.6 !important; 
      display: block; /* ブロック要素として扱う */
      position: relative;
    }
    .text-L_L_L { font-size: 20px; }
    .text-X_X_X { font-size: 24px; }

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
    .ruby-XXS_S_S { --ruby-font-size: 30%; }
    .ruby-XS_S_S  { --ruby-font-size: 30%; }
    .ruby-S_S_S   { --ruby-font-size: 40%; }
    .ruby-M_M_M   { --ruby-font-size: 50%; }
    .ruby-L_L_L   { --ruby-font-size: 60%; }
    .ruby-XL_L_L  { --ruby-font-size: 70%; }
    .ruby-XXL_L_L { --ruby-font-size: 80%; }

    /* ▼ 追加マイナス余白（ルビサイズ別に上書き） */
    rt {
      display: block !important;
      font-size: var(--ruby-font-size);
      color: var(--ruby-color);
      line-height: 1.05;/*ルビを改行するケースにおけるルビの行間*/
      text-align: center;
      /* margin-top: 0.2em !important;   
      transform: translateY(0.4em) !important; */
    }
    rt.ruby-XXS_S_S {
      margin-top: -0em !important;/*結局ここは0が一番良かった。 */
      transform: translateY(-5.6em) !important;/* ルビの高さ位置はここで調節する。 */
    }
    rt.ruby-XS_S_S {
      transform: translateY(-4.6em) !important;
    }
    rt.ruby-S_S_S {
      transform: translateY(-3.7em) !important;
    }
    rt.ruby-M_M_M {
      transform: translateY(-3.1em) !important;
    }
    rt.ruby-L_L_L {
      transform: translateY(-2.8em) !important;
    }
    rt.ruby-XL_L_L {
      transform: translateY(-2.5em) !important;
    }
    rt.ruby-XXL_L_L {
      transform: translateY(-2.3em) !important;
    }

  </style>
</head>
<body>
  <p class="text-M_M_M">
"""
    ruby_style_tail = """  </p>

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
    ruby_style_tail="<br>"
else:
    ruby_style_head=""
    ruby_style_tail=""

text1 = ruby_style_head+text1+ruby_style_tail


with open('Esperanto_Text_Replacement_Result_Multiprocessing_windows.html','w', encoding='utf-8') as h:
    h.write(text1)