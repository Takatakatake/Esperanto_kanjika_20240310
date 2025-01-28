# windowsでは、相対座標がうまく認識されないことがあるので、PATHの設定には注意が必要。何とかこのpythonファイルがあるディレクトリ上で実行する方法を模索する必要がある。
# Multi-processing が実行される行以降を  ""if __name__ == '__main__':"" ブロックインデント内に収め、同ブロック内にmultiprocessing.set_start_method('spawn', force=True)という設定行も追加することでうまく動作した。
# if __name__ == '__main__':
#     multiprocessing.set_start_method('spawn', force=True)

import os
import re
import json
import multiprocessing
from typing import List, Dict, Tuple, Optional  # List, Dict, Tuple, (Optional) など型ヒントを一括でインポート
from bs4 import BeautifulSoup, NavigableString
from bs4.element import Tag
import time

num_processes=8
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

def convert_to_circumflex(text: str) -> str:
    """テキストを字上符形式（ĉ, ĝ, ĥ, ĵ, ŝ, ŭなど）に統一します。"""
    text = replace_esperanto_chars(text, hat_to_circumflex)# 2. ^表記 (c^, g^...) → ĉ, ĝ... に変換
    text = replace_esperanto_chars(text, x_to_circumflex)# 3. x表記 (cx, gx...) → ĉ, ĝ... に変換
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
# 関数外（モジュールのグローバルスコープ）でコンパイル
PERCENT_PATTERN = re.compile(r'%(.{1,50}?)%')
def find_strings_in_text(text: str) -> List[str]:
    # 正規表現パターンを定義
    PERCENT_PATTERN = re.compile(r'%(.{1,50}?)%')# re.DOTALLで、任意の文字列に"改行"も含むようにできる。(今はしない。)
    matches = []
    used_indices = set()

    # 正規表現のマッチを見つける
    for match in PERCENT_PATTERN.finditer(text):
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

# ブラウザで表示した際の文字の高さを揃えるために、HTML形式の都合上、rubyタグがかかっていないメインテキストについても、<ruby>〜</ruby>で囲む必要が生じた。
# BeautifulSoup4を使用して実装することにした。streamlit cloud でもrequirements.txtに書き込んで、インストールすれば使用できることを確認。
def wrap_text_with_ruby(html_string: str, chunk_size: int = 10) -> str:
    soup = BeautifulSoup(html_string, 'lxml')  # 'html.parser' より高速で、streamlitにもインストールできた。

    def process_element(element: Tag, in_ruby: bool = False) -> None:
        # 現在の要素が <ruby> または <rt> なら、その下はすべて「既にruby内」
        if element.name in ['ruby', 'rt']:
            in_ruby = True

        for child in list(element.children):
            if isinstance(child, NavigableString):
                text = str(child)
                # 空白や改行のみの場合はスキップ
                if not text.strip():
                    continue

                # 親階層が <ruby> か、あるいは現在 <ruby>/<rt> の内側なら処理スキップ
                if in_ruby:
                    continue

                # テキストを chunk_size ごとに分割
                chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

                new_tags = []
                for chunk in chunks:
                    chunk = chunk.replace(" ", "&nbsp;").replace("　", "&nbsp;&nbsp;")
                    ruby_tag = soup.new_tag('ruby')
                    ruby_tag.string = chunk
                    new_tags.append(ruby_tag)

                child.replace_with(*new_tags)

            elif child.name and child.name.lower() in ['script', 'style']:
                # <script> / <style> 内は処理しない
                continue
            else:
                # 子要素を再帰的に処理。in_rubyフラグを引き継ぐ
                process_element(child, in_ruby)

    # メインの処理を呼び出す
    process_element(soup, in_ruby=False)

    # <html> と <body> を除去
    if soup.html:
        soup.html.unwrap()
    if soup.body:
        soup.body.unwrap()
        # 先頭の <p> タグと末尾の </p> タグを削除
    if soup.contents[0].name == "p":  # 先頭の <p>
        first_p = soup.contents[0]
        first_p.unwrap()
    if soup.contents[-1].name == "p":  # 末尾の </p>
        last_p = soup.contents[-1]
        last_p.unwrap()
    # 変換後のHTML文字列を取得し、&amp;nbsp;を&amp;nbsp;に置換
    final_str = str(soup).replace("&amp;nbsp;", "&nbsp;")

    return final_str


# 文字列(漢字)置換に用いる'replacements'リストと占位符(placeholders)を呼び出す。
with open("最终的な替换用リスト(列表)(合并3个JSON文件).json", "r", encoding="utf-8") as f:
    combined_3_replacements_lists = json.load(f)
replacements_final_list = combined_3_replacements_lists.get("全域替换用のリスト(列表)型配列(replacements_final_list)", None)
replacements_list_for_localized_string = combined_3_replacements_lists.get("局部文字替换用のリスト(列表)型配列(replacements_list_for_localized_string)", None)
replacements_list_for_2char = combined_3_replacements_lists.get("二文字词根替换用のリスト(列表)型配列(replacements_list_for_2char)", None)

placeholders_for_skipping_replacements = import_placeholders('占位符(placeholders)_%1854%-%4934%_文字列替换skip用.txt')# placeholderに'%'が含まれる必要は全く無いが、雰囲気を揃えるために敢えて入れた。
placeholders_for_localized_replacement = import_placeholders('占位符(placeholders)_@5134@-@9728@_局部文字列替换结果捕捉用.txt')# placeholderに'@'が含まれる必要は全く無いが、雰囲気を揃えるために敢えて入れた。


# 時間測定

"""
エスペラント文を段階的に文字列(漢字)置換するためのメイン関数。

【概要】
    1) unify_halfwidth_spaces():
        - 半角スペースと紛らわしい特殊空白文字を標準的なASCII半角スペース(U+0020)に統一する。（全角スペースは対象外。）
    2) convert_to_circumflex():
        - エスペラント特有の文字表記の揺れ(例えばx方式や^方式など)を字上符形式に統一する。
    3) '%'で囲まれた「置換せずにそのまま保つ箇所」をplaceholders_for_skipping_replacementsで定義された
        placeholderに一時的に置換する。- これにより、後続の置換処理がこれらの箇所を誤って書き換えないように保護する。
    4) '@'で囲まれた箇所を局所置換(replacements_list_for_localized_string で指定)し、その結果を保存した後、 
        placeholders_for_localized_replacementで定義されたplaceholderに置換する。
    5) replacements_final_listを用いて「メインの置換対象部分」をplaceholderに置換する。
    6) replacements_list_for_2charを用いて「2文字語根」をplaceholderに置換する。
        - このとき連続・隣接する2文字語根にも対応できるよう、2段階(2回分)のplaceholder置換を実施する。
        - まず一度目に2文字語根をplaceholderに変換し、さらに再度同じ置換を行い、別のplaceholderを割り当てている。これにより、隣接した2文字語根も正しく置換できるようになる。
        
    7) 上記の処理でplaceholderが置かれた箇所を、置換後の文字列に復元していく。
        - 2文字語根の2回目placeholder → 2文字語根の1回目placeholder → メイン置換のplaceholder → 局所置換対象('@'で囲まれた部分)のplaceholder → 
        → スキップ対象('%'で囲まれた部分)のplaceholder   のように、placeholderを置く処理とは逆の順番で置換後の文字列に復元していく(逆順置換)。
    8) 最後にformat_typeが"HTML"であれば、改行を<br>へ変換したり、連続スペースを&nbsp;に変換するなど、HTMLに適した整形を行う。

【引数】
    text : str
        置換対象の元テキスト。
    placeholders_for_skipping_replacements : List[str]
        '%'で囲まれた置換せずにそのまま保つ箇所に対応するplaceholder。
    replacements_list_for_localized_string : List[Tuple[str, str, str]]
        '@'で囲まれた箇所を局所的に置換するための(old, new, placeholder)のリスト。
    placeholders_for_localized_replacement : List[str]
        '@'で囲まれた箇所を保護するためのplaceholder。
    replacements_final_list : List[Tuple[str, str, str]]
        本命の(最も重要な)置換を行うための(old, new, placeholder)のリスト。
    replacements_list_for_2char : List[Tuple[str, str, str]]
        2文字の語根を置換するための(old, new, placeholder)のリスト。
    format_type : str
        "HTML格式_Ruby文字_大小调整"などを指定すると、改行や連続スペースをHTMLタグへ変換する。

【戻り値】
    すべての置換が完了した最終的な文字列。format_typeが"HTML格式_Ruby文字_大小调整"などの場合は改行や空白変換等のHTML整形を施したうえで出力する。
"""

def orchestrate_comprehensive_esperanto_text_replacement(
    text, 
    placeholders_for_skipping_replacements: List[str] = placeholders_for_skipping_replacements, 
    replacements_list_for_localized_string: List[Tuple[str, str, str]] = replacements_list_for_localized_string, 
    placeholders_for_localized_replacement: List[str] = placeholders_for_localized_replacement, 
    replacements_final_list: List[Tuple[str, str, str]] = replacements_final_list, 
    replacements_list_for_2char: List[Tuple[str, str, str]] = replacements_list_for_2char, 
    format_type: str = format_type
    )-> str:
    # ---- 全体の処理時間を測定開始 ----
    global_start_time = time.time()

    # 1, 2) 半角スペースを標準化し、エスペラント文字表現を字上符形式に統一
    step1_start = time.time()
    text = unify_halfwidth_spaces(text)# 半角スペースと視覚的に区別がつきにくい特殊な空白文字を標準的なASCII半角スペース(U+0020)に置換する。 ただし、全角スペース(U+3000)は置換対象に含めていない。
    text = convert_to_circumflex(text)# テキストを字上符形式（ĉ, ĝ, ĥ, ĵ, ŝ, ŭなど）に統一。
    step1_end = time.time()
    print(f"[計測] Step1(半角スペース正規化 + convert_to_circumflex): {step1_end - step1_start:.6f} 秒")

    # 3) '%'で囲まれた置換禁止部分を保護(placeholderに置換)
    step2_start = time.time()
    replacements_list_for_intact_parts = create_replacements_list_for_intact_parts(text, placeholders_for_skipping_replacements)
    sorted_replacements_list_for_intact_parts = sorted(replacements_list_for_intact_parts, key=lambda x: len(x[0]), reverse=True)
    for original, place_holder_ in sorted_replacements_list_for_intact_parts:
        text = text.replace(original, place_holder_)# いいのか→多分大丈夫。
    step2_end = time.time()
    print(f"[計測] Step2('%'で囲まれた置換禁止部分を保護): {step2_end - step2_start:.6f} 秒")

    # 4) '@'で囲まれた箇所を局所置換(replacements_list_for_localized_string で指定)し、その結果を保存した後、 
    #    placeholders_for_localized_replacementで定義されたplaceholderに置換
    step3_start = time.time()
    tmp_replacements_list_for_localized_string_2 = create_replacements_list_for_localized_replacement(
        text, 
        placeholders_for_localized_replacement, 
        replacements_list_for_localized_string
    )
    sorted_replacements_list_for_localized_string = sorted(tmp_replacements_list_for_localized_string_2, key=lambda x: len(x[0]), reverse=True)
    for original, place_holder_, replaced_original in sorted_replacements_list_for_localized_string:
        text = text.replace(original, place_holder_)
    step3_end = time.time()
    print(f"[計測] Step3('@'で囲まれた部分の局所置換): {step3_end - step3_start:.6f} 秒")

    # 5) メインとなる置換対象文字列をplaceholderへ置換
    step4_start = time.time()
    valid_replacements = {}
    for old, new, placeholder in replacements_final_list:
        if old in text:
            text = text.replace(old, placeholder)# 置換前の文字列を一旦プレースホルダーに置き換える。
            valid_replacements[placeholder] = new
    step4_end = time.time()
    print(f"[計測] Step4(メイン置換対象をプレースホルダーに置換): {step4_end - step4_start:.6f} 秒")

    # 6) replacements_list_for_2charを用いて「2文字語根」をplaceholderに置換する (2回実施)
    step5_start = time.time()
    valid_replacements_for_2char_roots = {}
    for old, new, placeholder in replacements_list_for_2char:
        if old in text:
            text = text.replace(old, placeholder)
            valid_replacements_for_2char_roots[placeholder] = new

    # 2周目用に別のplaceholderを割り当てる
    valid_replacements_for_2char_roots_2 = {}
    for old, new, placeholder in replacements_list_for_2char:
        if old in text:
            place_holder_second="!"+placeholder+"!"# 2回目のplace_holderは少し変更を加えたほうが良いはず。
            text = text.replace(old, place_holder_second)
            valid_replacements_for_2char_roots_2[place_holder_second] = new

    # print(text)# ⇑ここまでがplaceholderによる置換作業。以降⇓は、placeholderを置換後の文字列に置き換える作業。

    # 7) ここからplaceholderを最終的な文字列に復元していく
    for place_holder_second, new in reversed(valid_replacements_for_2char_roots_2.items()):# ここで、reverseにすることがポイント。 但し、完璧な対策ではない？
        text = text.replace(place_holder_second, new)# プレースホルダーを置換後の文字列に置き換える。
    for placeholder, new in reversed(valid_replacements_for_2char_roots.items()):
        text = text.replace(placeholder, new)# プレースホルダーを置換後の文字列に置き換える。
    step5_end = time.time()
    print(f"[計測] Step5(2文字語根の置換処理・復元まで含む): {step5_end - step5_start:.6f} 秒")

    step6_start = time.time()
    for placeholder, new in valid_replacements.items():
        text = text.replace(placeholder, new)
    step6_end = time.time()
    print(f"[計測] Step6(メイン置換プレースホルダーを元文字に復元): {step6_end - step6_start:.6f} 秒")

    step7_start = time.time()
    for original, place_holder_, replaced_original in sorted_replacements_list_for_localized_string:
        text = text.replace(place_holder_, replaced_original.replace("@",""))
    step7_end = time.time()
    print(f"[計測] Step7('@'で囲まれた箇所の復元): {step7_end - step7_start:.6f} 秒")

    step8_start = time.time()
    for original, place_holder_ in sorted_replacements_list_for_intact_parts:
        text = text.replace(place_holder_, original.replace("%",""))
    step8_end = time.time()
    print(f"[計測] Step8('%'で囲まれた置換禁止部分の復元): {step8_end - step8_start:.6f} 秒")

    # 8) 必要に応じてHTML用の整形を実施
    step9_start = time.time()
    if "HTML" in format_type:
        text = text.replace("\n", "<br>\n")
        text = wrap_text_with_ruby(text, chunk_size=10)
        text = re.sub(r"   ", "&nbsp;&nbsp;&nbsp;", text)  # 3つ以上の空白を変換
        text = re.sub(r"  ", "&nbsp;&nbsp;", text)  # 2つ以上の空白を変換
    step9_end = time.time()
    print(f"[計測] Step9(HTML整形): {step9_end - step9_start:.6f} 秒")

    # ---- 全体の処理時間を計測 ----
    global_end_time = time.time()
    total_time = global_end_time - global_start_time
    print(f"[計測] 関数全体の処理時間: {total_time:.6f} 秒")

    return text


# multiprocessingのための関数群　テキストを行数によって設定プロセス数(num_processes)に等分割して、それぞれのプロセスで並列に置換処理を実行してから、再度分割したテキストを結合する。
import multiprocessing
def process_segment(lines: List[str],
                    
    placeholders_for_skipping_replacements: List[str] = placeholders_for_skipping_replacements, replacements_list_for_localized_string: List[Tuple[str, str, str]] = replacements_list_for_localized_string, 
    placeholders_for_localized_replacement: List[str] = placeholders_for_localized_replacement, replacements_final_list: List[Tuple[str, str, str]] = replacements_final_list, 
    replacements_list_for_2char: List[Tuple[str, str, str]] = replacements_list_for_2char, format_type: str = format_type ) -> str:# orchestrate_comprehensive_esperanto_text_replacementの引数をそのまま持って来た。

    # 文字列のリストを結合してから置換処理を実行 linesには\nが含まれていない状態の文字列群が格納されている。
    segment = '\n'.join(lines)
    segment = orchestrate_comprehensive_esperanto_text_replacement(
    segment, placeholders_for_skipping_replacements, replacements_list_for_localized_string, 
    placeholders_for_localized_replacement, replacements_final_list, replacements_list_for_2char, format_type)# ここでメインの文字列(漢字)置換関数'orchestrate_comprehensive_esperanto_text_replacement'の実行!

    return segment

# def orchestrate_comprehensive_esperanto_text_replacement(
#     text, placeholders_for_skipping_replacements: List[str] = placeholders_for_skipping_replacements, replacements_list_for_localized_string: List[Tuple[str, str, str]] = replacements_list_for_localized_string, 
#     placeholders_for_localized_replacement: List[str] = placeholders_for_localized_replacement, replacements_final_list: List[Tuple[str, str, str]] = replacements_final_list, 
#     replacements_list_for_2char: List[Tuple[str, str, str]] = replacements_list_for_2char, format_type: str = format_type)-> str:

def parallel_process(text: str, num_processes: int = num_processes, 

    placeholders_for_skipping_replacements: List[str] = placeholders_for_skipping_replacements, replacements_list_for_localized_string: List[Tuple[str, str, str]] = replacements_list_for_localized_string, 
    placeholders_for_localized_replacement: List[str] = placeholders_for_localized_replacement, replacements_final_list: List[Tuple[str, str, str]] = replacements_final_list, 
    replacements_list_for_2char: List[Tuple[str, str, str]] = replacements_list_for_2char, format_type: str = format_type  ) -> str:# orchestrate_comprehensive_esperanto_text_replacementの引数をそのまま持って来た。

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

# '@'で囲まれた18文字(PEJVOに収録されている最長語根の文字数)以内の部分を同定し、局所的な文字列(漢字)置換を実行するための関数群
# 関数外（モジュールのグローバルスコープ）でコンパイル
AT_PATTERN = re.compile(r'@(.{1,18}?)@')
def find_strings_in_text_for_localized_replacement(text: str) -> List[str]:
    # 正規表現パターンを定義
    AT_PATTERN = re.compile(r'@(.{1,18}?)@')# re.DOTALLで、任意の文字列に"改行"も含むようにできる。(今はしない。)
    matches = []
    used_indices = set()

    # 正規表現のマッチを見つける
    for match in AT_PATTERN.finditer(text):
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


with open('例句_Esperanto文本.txt','r', encoding='utf-8') as g:
    text0=g.read()*text_repeat_times

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn', force=True)
    text1=parallel_process(text0)

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
        .ruby-XXS_S { --ruby-font-size: 30%; }
        .ruby-XS_S  { --ruby-font-size: 30%; }
        .ruby-S_S   { --ruby-font-size: 40%; }
        .ruby-M_M   { --ruby-font-size: 50%; }
        .ruby-L_L   { --ruby-font-size: 60%; }
        .ruby-XL_L  { --ruby-font-size: 70%; }
        .ruby-XXL_L { --ruby-font-size: 80%; }

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