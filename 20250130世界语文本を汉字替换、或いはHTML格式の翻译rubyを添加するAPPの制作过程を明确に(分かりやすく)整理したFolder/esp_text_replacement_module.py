"""
esp_text_replacement_module.py

このモジュールは「エスペラント文章の文字列(漢字)置換」を包括的に扱うツール集です。
主な機能：
1. エスペラント独自の文字形式（ĉ, ĝなど）への変換 → convert_to_circumflex
2. 特殊な半角スペースの統一（ASCIIスペースに） → unify_halfwidth_spaces
3. HTMLルビ（<ruby>タグ）付与 → wrap_text_with_ruby
4. %や@で囲まれたテキストのスキップ・局所変換 → (create_replacements_list_for_...)
5. 大域的なプレースホルダー置換 → safe_replace
6. それらをまとめて実行する複合置換関数 → orchestrate_comprehensive_esperanto_text_replacement
7. multiprocessing を用いた行単位の並列実行 → parallel_process / process_segment
"""
# Pythonファイル単独でモジュールとして扱う想定。トップレベルに各関数を定義しておく。

import re
import json
from typing import List, Tuple, Dict
import multiprocessing
from bs4 import BeautifulSoup, NavigableString
from bs4.element import Tag

# ================================
# 1) エスペラント文字変換用の辞書
# ================================
# 字上符付き文字の表記形式変換用の辞書型配列
x_to_circumflex = {'cx': 'ĉ', 'gx': 'ĝ', 'hx': 'ĥ', 'jx': 'ĵ', 'sx': 'ŝ', 'ux': 'ŭ','Cx': 'Ĉ', 'Gx': 'Ĝ', 'Hx': 'Ĥ', 'Jx': 'Ĵ', 'Sx': 'Ŝ', 'Ux': 'Ŭ'}
circumflex_to_x = {'ĉ': 'cx', 'ĝ': 'gx', 'ĥ': 'hx', 'ĵ': 'jx', 'ŝ': 'sx', 'ŭ': 'ux','Ĉ': 'Cx', 'Ĝ': 'Gx', 'Ĥ': 'Hx', 'Ĵ': 'Jx', 'Ŝ': 'Sx', 'Ŭ': 'Ux'}
x_to_hat = {'cx': 'c^', 'gx': 'g^', 'hx': 'h^', 'jx': 'j^', 'sx': 's^', 'ux': 'u^','Cx': 'C^', 'Gx': 'G^', 'Hx': 'H^', 'Jx': 'J^', 'Sx': 'S^', 'Ux': 'U^'}
hat_to_x = {'c^': 'cx', 'g^': 'gx', 'h^': 'hx', 'j^': 'jx', 's^': 'sx', 'u^': 'ux','C^': 'Cx', 'G^': 'Gx', 'H^': 'Hx', 'J^': 'Jx', 'S^': 'Sx', 'U^': 'Ux'}
hat_to_circumflex = {'c^': 'ĉ', 'g^': 'ĝ', 'h^': 'ĥ', 'j^': 'ĵ', 's^': 'ŝ', 'u^': 'ŭ','C^': 'Ĉ', 'G^': 'Ĝ', 'H^': 'Ĥ', 'J^': 'Ĵ', 'S^': 'Ŝ', 'U^': 'Ŭ'}
circumflex_to_hat = {'ĉ': 'c^', 'ĝ': 'g^', 'ĥ': 'h^', 'ĵ': 'j^', 'ŝ': 's^', 'ŭ': 'u^','Ĉ': 'C^', 'Ĝ': 'G^', 'Ĥ': 'H^', 'Ĵ': 'J^', 'Ŝ': 'S^', 'Ŭ': 'U^'}

# ================================
# 2) 基本の文字形式変換関数
# ================================

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

def unify_halfwidth_spaces(text: str) -> str:
    """全角スペース(U+3000)は変更せず、半角スペースと視覚的に区別がつきにくい空白文字を
        ASCII半角スペース(U+0020)に統一する。連続した空白は1文字ずつ置換する。"""
    pattern = r"[\u00A0\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A]"# 対象とする空白文字をまとめたパターン
    return re.sub(pattern, " ", text)# マッチした部分を標準的な半角スペースに置換

# ================================
# 3) HTMLルビタグの補助関数
# ================================
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

# ================================
# 4) 占位符(placeholder)関連
# ================================

# 置換に用いる関数。正規表現、C++など様々な形式の置換を試したが、pythonでplaceholder(占位符)を用いる形式の置換が、最も処理が高速であった。(しかも大変シンプルでわかりやすい。)
def safe_replace(text: str, replacements: List[Tuple[str, str, str]]) -> str:# Tupleは狭義のList
    """(old, new, placeholder) のタプルを含むリストを受け取り、
        text中の old → placeholder → new の段階置換を行う。 """
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
def import_placeholders(filename: str) -> List[str]:# placeholder(占位符)をインポートするためだけの関数
    with open(filename, 'r') as file:
        placeholders = [line.strip() for line in file if line.strip()]
    return placeholders

# '%'で囲まれた50文字以内の部分を同定し、文字列(漢字)置換せずにそのまま保存しておくための関数群
# 関数外（モジュールのグローバルスコープ）でコンパイル
PERCENT_PATTERN = re.compile(r'%(.{1,50}?)%')
def find_percent_enclosed_strings_for_skipping_replacement(text: str) -> List[str]:
    """'%foo%' の形を全て抽出。50文字以内。"""
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
    matches = find_percent_enclosed_strings_for_skipping_replacement(text)
    replacements_list_for_intact_parts = []
    # プレースホルダーとマッチを対応させる
    for i, match in enumerate(matches):
        if i < len(placeholders):
            replacements_list_for_intact_parts.append([f"%{match}%", placeholders[i]])
        else:
            break  # プレースホルダーが足りなくなった場合は終了
    return replacements_list_for_intact_parts


# 関数外（モジュールのグローバルスコープ）でコンパイル
AT_PATTERN = re.compile(r'@(.{1,18}?)@')
def find_at_enclosed_strings_for_localized_replacement(text: str) -> List[str]:
    """'@foo@' の形を全て抽出。18文字以内。"""
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

def create_replacements_list_for_localized_replacement(text, placeholders: List[str], 
                                                       replacements_list_for_localized_string: List[Tuple[str, str, str]])-> List[List[str]]:
    # テキストから@で囲まれた部分を抽出
    matches = find_at_enclosed_strings_for_localized_replacement(text)
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


# ================================
# 5) メインの複合文字列(漢字)置換関数
# ================================

def orchestrate_comprehensive_esperanto_text_replacement(
    text, 
    placeholders_for_skipping_replacements: List[str], 
    replacements_list_for_localized_string: List[Tuple[str, str, str]] , 
    placeholders_for_localized_replacement: List[str] , 
    replacements_final_list: List[Tuple[str, str, str]] , 
    replacements_list_for_2char: List[Tuple[str, str, str]] , 
    format_type: str 
    )-> str:
    """
    複数の変換ルールに従ってエスペラント文を文字列(漢字)置換するメイン関数。

    ステップ:
      1) unify_halfwidth_spaces(text)     : 特殊な空白を半角スペースへ
      2) convert_to_circumflex(text)      : ĉ, ĝ, ĥ, ĵ, ŝ, ŭ への統一
      3) %...% で囲まれた部分を置換スキップ (placeholders_for_skipping_replacements で保護)
      4) @...@ で囲まれた部分を局所置換 (replacements_list_for_localized_string)
      5) 大域置換 (replacements_final_list)
      6) 二文字語根の置換を2回実施 (replacements_list_for_2char)
      7) プレースホルダーの復元
      8) もし format_type に "HTML" が含まれるなら、wrap_text_with_ruby(...) 等でHTML整形

    Args:
        text: 変換対象のエスペラント文
        placeholders_for_skipping_replacements:  %...% 用のプレースホルダー一覧
        replacements_list_for_localized_string:  @...@ 用の置換ルール (old, new, placeholder)
        placeholders_for_localized_replacement:  @...@ 用のプレースホルダー一覧
        replacements_final_list:                 大域置換用の (old, new, placeholder) のリスト
        replacements_list_for_2char:             2文字語根用の (old, new, placeholder) リスト
        format_type:  "HTML" が含まれているとHTMLルビ化などの処理を行う

    Returns:
        置換後のテキスト（HTML形式の場合もある）
    """

    # 1, 2) 半角スペースを標準化し、エスペラント文字表現を字上符形式に統一
    text = unify_halfwidth_spaces(text)# 半角スペースと視覚的に区別がつきにくい特殊な空白文字を標準的なASCII半角スペース(U+0020)に置換する。 ただし、全角スペース(U+3000)は置換対象に含めていない。
    text = convert_to_circumflex(text)# テキストを字上符形式（ĉ, ĝ, ĥ, ĵ, ŝ, ŭなど）に統一。
    # 3) '%'で囲まれた置換禁止部分を保護(placeholderに置換)
    replacements_list_for_intact_parts = create_replacements_list_for_intact_parts(text, placeholders_for_skipping_replacements)
    sorted_replacements_list_for_intact_parts = sorted(replacements_list_for_intact_parts, key=lambda x: len(x[0]), reverse=True)
    for original, place_holder_ in sorted_replacements_list_for_intact_parts:
        text = text.replace(original, place_holder_)# いいのか→多分大丈夫。
    # 4) '@'で囲まれた箇所を局所的に置換・保存した後、placeholderに置換
    tmp_replacements_list_for_localized_string_2 = create_replacements_list_for_localized_replacement(text, placeholders_for_localized_replacement, replacements_list_for_localized_string)
    sorted_replacements_list_for_localized_string = sorted(tmp_replacements_list_for_localized_string_2, key=lambda x: len(x[0]), reverse=True)
    for original, place_holder_, replaced_original in sorted_replacements_list_for_localized_string:
        text = text.replace(original, place_holder_)
    # 5) メインとなる置換対象文字列をplaceholderへ置換
    valid_replacements = {}
    for old, new, placeholder in replacements_final_list:
        if old in text:
            text = text.replace(old, placeholder)# 置換前の文字列を一旦プレースホルダーに置き換える。
            valid_replacements[placeholder] = new
    # 6)ここで、2文字の語根の文字列(漢字)置換を(2回)実施することとした。Placeholderに隣接した2文字語根については置換可能と考えたためである。(202412の変更)。
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
    for placeholder, new in valid_replacements.items():
        text = text.replace(placeholder, new)
    # 7) 局所置換箇所(@...@)・置換禁止箇所(%...%)も復元
    for original, place_holder_, replaced_original in sorted_replacements_list_for_localized_string:
        text = text.replace(place_holder_, replaced_original.replace("@",""))
    for original, place_holder_ in sorted_replacements_list_for_intact_parts:
        text = text.replace(place_holder_, original.replace("%",""))
    # 8) 必要に応じてHTML用の整形を実施
    if "HTML" in format_type:
        text = text.replace("\n", "<br>\n")
        text = wrap_text_with_ruby(text, chunk_size=10)
        text = re.sub(r"   ", "&nbsp;&nbsp;&nbsp;", text)  # 3つ以上の空白を変換
        text = re.sub(r"  ", "&nbsp;&nbsp;", text)  # 2つ以上の空白を変換
    
    return text

# ================================
# 6) multiprocessing 関連
# ================================
def process_segment(lines: List[str],
                    
    placeholders_for_skipping_replacements: List[str] , replacements_list_for_localized_string: List[Tuple[str, str, str]] , 
    placeholders_for_localized_replacement: List[str] , replacements_final_list: List[Tuple[str, str, str]] , 
    replacements_list_for_2char: List[Tuple[str, str, str]] , format_type: str ) -> str:# orchestrate_comprehensive_esperanto_text_replacementの引数をそのまま持って来た。

    # 文字列のリストを結合してから置換処理を実行 linesには\nが含まれていない状態の文字列群が格納されている。
    segment = '\n'.join(lines)
    result = orchestrate_comprehensive_esperanto_text_replacement(
    segment, placeholders_for_skipping_replacements, replacements_list_for_localized_string, 
    placeholders_for_localized_replacement, replacements_final_list, replacements_list_for_2char, format_type)# ここでメインの文字列(漢字)置換関数'orchestrate_comprehensive_esperanto_text_replacement'の実行!

    return result


def parallel_process(text: str, num_processes: int , 

    placeholders_for_skipping_replacements: List[str] , replacements_list_for_localized_string: List[Tuple[str, str, str]] , 
    placeholders_for_localized_replacement: List[str] , replacements_final_list: List[Tuple[str, str, str]] , 
    replacements_list_for_2char: List[Tuple[str, str, str]] , format_type: str ) -> str:# orchestrate_comprehensive_esperanto_text_replacementの引数をそのまま持って来た。
    """
    与えられた text を行単位で分割し、'process_segment' をマルチプロセスで並列実行した結果を結合。
    """
    lines = text.split('\n')
    num_lines = len(lines)
    if num_processes < 1:
        num_processes = 1

    # 行数が 0または1 の場合は単純に処理して返す (エラー回避の安全策)
    # （text.split('\n')で空でも [""] になるため num_lines=1 になるケースが多いです）
    if num_lines <= 1:
        # 並列化の意味がほぼないので、そのまま処理
        return process_segment(
            lines, 
            placeholders_for_skipping_replacements,
            replacements_list_for_localized_string,
            placeholders_for_localized_replacement,
            replacements_final_list,
            replacements_list_for_2char,
            format_type
        )

    # 通常ケース: 行数が2以上
    lines_per_process = max(num_lines // num_processes, 1)
    # 各プロセスに割り当てる行のリストを決定
    ranges = [(i * lines_per_process, (i + 1) * lines_per_process) for i in range(num_processes)]
    # 最後に残り全部を割り当て
    ranges[-1] = (ranges[-1][0], num_lines)  # 最後のプロセスが残り全てを処理

    with multiprocessing.Pool(processes=num_processes) as pool:
        # 並列処理を実行
        results = pool.starmap(process_segment,
            [(lines[start:end],
                placeholders_for_skipping_replacements,replacements_list_for_localized_string,placeholders_for_localized_replacement,
                replacements_final_list,replacements_list_for_2char,format_type)  
                for (start, end) in ranges])
    # 結果を結合
    return '\n'.join(results)
