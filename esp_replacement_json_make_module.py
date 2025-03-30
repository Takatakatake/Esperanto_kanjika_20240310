"""
esp_replacement_json_make_module.py

エスペラント文字の変換や、ルビサイズ調整、置換処理用の関数などをまとめたモジュール。

【構成】
1) 文字変換用の辞書定義 (字上符形式への変換など)
2) 基本の文字形式変換関数 (replace_esperanto_chars, convert_to_circumflex, など)
3) 文字幅計測＆<br>挿入関数 (measure_text_width_Arial16, insert_br_at_half_width, insert_br_at_third_width)
4) 出力フォーマット (output_format) 関連
5) 文字列判定・placeholder インポートなどの補助関数
6) multiprocessing 関連の並列置換用関数 (process_chunk_for_pre_replacements, parallel_build_pre_replacements_dict)
"""

import re
import json
import multiprocessing
import pandas as pd
import os
from typing import List, Dict, Tuple, Optional  # List, Dict, Tuple, (Optional) など型ヒントを一括でインポート

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

# ================================
# 3) 文字幅計測 & <br> 挿入関数
# ================================
def measure_text_width_Arial16(text, char_widths_dict: Dict[str, int]) -> int:
    """
    JSONで読み込んだ  {文字: 幅(px)} の辞書 (char_widths_dict) を用いて、
    与えられた文字列 text の幅を合計して返す。
    """
    total_width = 0
    for ch in text:
        # JSONにない文字の場合は幅 8 とみなす（または別の処理）
        char_width = char_widths_dict.get(ch, 8)
        total_width += char_width
    return total_width

# HTML形式におけるルビ文字列内での改行のために、適切な位置に"<br>"を挿入する関数
def insert_br_at_half_width(text, char_widths_dict: Dict[str, int]) -> str:
    """
    与えられた文字列の Arial16px 形式における文字幅を計算し、
    合計幅の半分を超えた直後に "<br>" を挿入した文字列を返す。
    """
    # 文字列全体の幅を計算
    total_width = measure_text_width_Arial16(text, char_widths_dict)
    # 二等分地点
    half_width = total_width / 2

    current_width = 0
    insert_index = None

    for i, ch in enumerate(text):
        char_width = char_widths_dict.get(ch, 8)
        current_width += char_width
        # 半分の幅を超えた最初の位置を特定
        if current_width >= half_width:
            insert_index = i + 1 
            break

    if insert_index is not None:
        # 挿入位置までの文字列 + <br> + 残りの文字列
        result = text[:insert_index] + "<br>" + text[insert_index:]
    else:
        # すべての文字幅が半分以下の場合はそのまま返す
        result = text

    return result


# HTML形式におけるルビ文字列内での改行のために、適切な位置に"<br>"を"2つ"挿入する関数
def insert_br_at_third_width(text, char_widths_dict: Dict[str, int] ) -> str:
    """
    与えられた文字列の Arial16px 形式における文字幅を計算し、
    合計幅を3等分した際の 1つ目(1/3) と 2つ目(2/3) の境界を超えた直後に、
    "<br>" を挿入した文字列を返す。
    """
    total_width = measure_text_width_Arial16(text, char_widths_dict)
    third_width = total_width / 3
    thresholds = [third_width, third_width * 2]  # 2つの分割点

    current_width = 0
    insert_indices = []  # 挿入位置を記録 (例: [5, 10])
    found_first = False  # 1つ目の分割点発見フラグ

    for i, ch in enumerate(text):
        char_width = char_widths_dict.get(ch, 8)
        current_width += char_width

        # 1つ目の分割点チェック（未発見時のみ）
        if not found_first and current_width >= thresholds[0]:
            insert_indices.append(i + 1)
            found_first = True  # フラグを立てる
            
        # 2つ目の分割点チェック（1つ目発見後のみ）
        elif found_first and current_width >= thresholds[1]:
            insert_indices.append(i + 1)
            break  # 両方見つけたら終了

    # 後ろから挿入（インデックスのずれを防ぐため）
    result = text
    for idx in reversed(insert_indices):
        result = result[:idx] + "<br>" + result[idx:]

    return result

# ================================
# 4) 出力フォーマット (HTML/括弧形式等)
# ================================
# ユーザーが選択した出力形式を出力するための関数
def output_format(main_text, ruby_content, format_type, char_widths_dict):
    if format_type == 'HTML格式_Ruby文字_大小调整':
        width_ruby = measure_text_width_Arial16(ruby_content, char_widths_dict)
        width_main = measure_text_width_Arial16(main_text, char_widths_dict)
        ratio_1 = width_ruby / width_main
        # main_text(親要素)とruby_content(ルビ)の文字幅の比率に応じて、ルビサイズを8段階に分ける。
        # "や'などの特殊文字については、jsonモジュールが自動的にエスケープして、正しく処理してくれるので心配無用。
        if ratio_1 > 6 :# 親要素に対してルビが大きすぎる場合は、ルビ内で改行するため、関数'insert_br_at_third_width'によって適切な位置に'<br>'を2つ挿入。
            return '<ruby>{}<rt class="XXXS_S">{}</rt></ruby>'.format(main_text, insert_br_at_third_width(ruby_content, char_widths_dict))
        elif ratio_1>(9/3):# 親要素に対してルビが大きい場合は、ルビ内で改行するため、関数'insert_br_at_half_width'によって適切な位置に'<br>'を挿入。
            return '<ruby>{}<rt class="XXS_S">{}</rt></ruby>'.format(main_text, insert_br_at_half_width(ruby_content, char_widths_dict))
        elif ratio_1>(9/4):
            return '<ruby>{}<rt class="XS_S">{}</rt></ruby>'.format(main_text, ruby_content)
        elif  ratio_1>(9/5):
            return '<ruby>{}<rt class="S_S">{}</rt></ruby>'.format(main_text, ruby_content)
        elif  ratio_1>(9/6):
            return '<ruby>{}<rt class="M_M">{}</rt></ruby>'.format(main_text, ruby_content)
        elif  ratio_1>(9/7):
            return '<ruby>{}<rt class="L_L">{}</rt></ruby>'.format(main_text, ruby_content)
        elif  ratio_1>(9/8):
            return '<ruby>{}<rt class="XL_L">{}</rt></ruby>'.format(main_text, ruby_content)
        else:
            return '<ruby>{}<rt class="XXL_L">{}</rt></ruby>'.format(main_text, ruby_content)
    elif format_type == 'HTML格式_Ruby文字_大小调整_汉字替换':
        width_ruby = measure_text_width_Arial16(ruby_content, char_widths_dict)
        width_main = measure_text_width_Arial16(main_text, char_widths_dict)
        ratio_2 = width_main / width_ruby
        
        if ratio_2 > 6 :
            return '<ruby>{}<rt class="XXXS_S">{}</rt></ruby>'.format(ruby_content, insert_br_at_third_width(main_text, char_widths_dict))
        elif ratio_2>(9/3):
            return '<ruby>{}<rt class="XXS_S">{}</rt></ruby>'.format(ruby_content, insert_br_at_half_width(main_text, char_widths_dict))
        elif ratio_2>(9/4):
            return '<ruby>{}<rt class="XS_S">{}</rt></ruby>'.format(ruby_content, main_text)
        elif  ratio_2>(9/5):
            return '<ruby>{}<rt class="S_S">{}</rt></ruby>'.format(ruby_content, main_text)
        elif  ratio_2>(9/6):
            return '<ruby>{}<rt class="M_M">{}</rt></ruby>'.format(ruby_content, main_text)
        elif  ratio_2>(9/7):
            return '<ruby>{}<rt class="L_L">{}</rt></ruby>'.format(ruby_content, main_text)
        elif  ratio_2>(9/8):
            return '<ruby>{}<rt class="XL_L">{}</rt></ruby>'.format(ruby_content, main_text)
        else:
            return '<ruby>{}<rt class="XXL_L">{}</rt></ruby>'.format(ruby_content, main_text)
    elif format_type == 'HTML格式':
        return '<ruby>{}<rt>{}</rt></ruby>'.format(main_text, ruby_content)
    elif format_type == 'HTML格式_汉字替换':
        return '<ruby>{}<rt>{}</rt></ruby>'.format(ruby_content, main_text)
    elif format_type == '括弧(号)格式':
        return '{}({})'.format(main_text, ruby_content)
    elif format_type == '括弧(号)格式_汉字替换':
        return '{}({})'.format(ruby_content, main_text)
    elif format_type == '替换后文字列のみ(仅)保留(简单替换)':
        return '{}'.format(ruby_content)

# ユーザーに出力形式を選択してもらう
format_type = 'HTML格式_Ruby文字_大小调整'
# '括弧(号)格式'


# ================================
# 5) 文字列判定・placeholder インポート等の補助関数
# ================================

def contains_digit(s: str) -> bool:# 対象の文字列sに数字となりうる文字列(数字)が含まれるかどうかを確認する関数
    return any(char.isdigit() for char in s)

def import_placeholders(filename: str) -> List[str]:# placeholder(占位符)をインポートするためだけの関数
    with open(filename, 'r') as file:
        placeholders = [line.strip() for line in file if line.strip()]
    return placeholders

# 正規表現パターンを関数の外でコンパイル
RUBY_PATTERN = re.compile(
    r'^'                            # 行頭／文字列頭
    r'(.*?)'                        # グループ1: <ruby> より左側(外側)のテキスト
    r'(<ruby>)'                     # グループ2: "<ruby>"
    r'([^<]+)'                      # グループ3: "<ruby>"～"<rt" の間にある文字列　親要素(本文)
    r'(<rt[^>]*>)'                  # グループ4: "<rt class="xxx"等 >"
    r'([^<]*?(?:<br>[^<]*?){0,2})'  # グループ5: ルビ部分（<br>を含む場合あり、最大2回）
    r'(</rt>)'                      # グループ6: "</rt>"
    r'(</ruby>)?'                   # グループ7: "</ruby>"
    r'(.*)'                         # グループ8: 残り(この <ruby> ブロックの後ろのテキストすべて)
    r'$'                            # 行末／文字列末
)

def capitalize_ruby_and_rt(text: str) -> str:
    def replacer(match):
        g1 = match.group(1)  # グループ1: <ruby> より左側(外側)のテキスト
        g2 = match.group(2)  # グループ2: "<ruby>"
        g3 = match.group(3)  # グループ3: "<ruby>"～"<rt" の間にある文字列　親要素(本文)
        g4 = match.group(4)  # グループ4: "<rt class="xxx"等 >"
        g5 = match.group(5)  # グループ5: <rt>～</rt> の中身　子要素(ルビ部分)
        g6 = match.group(6)  # グループ6: "</rt>"
        g7 = match.group(7)  # グループ7: "</ruby>"
        g8 = match.group(8)  # グループ8: 残り(この <ruby> ブロックの後ろのテキストすべて)
        
        # 左側(外側)のテキストが空ではない場合 → 左側の先頭を大文字化
        if g1.strip():
            return g1.capitalize() + g2 + g3 + g4 + g5 + g6 + (g7 if g7 else '') + g8
        else:
            # 左側が空の場合 → <ruby> 内の親文字列/ルビ文字列を大文字化
            parent_text = g3.capitalize()
            rt_text = g5.capitalize()
            return g1 + g2 + parent_text + g4 + rt_text + g6 + (g7 if g7 else '') + g8

    replaced_text = RUBY_PATTERN.sub(replacer, text)

    # もし置換が1箇所も行われなかった(=パターン不一致)なら、先頭を大文字化
    if replaced_text == text:
        replaced_text = text.capitalize()

    return replaced_text

# ================================
# 6) multiprocessing 関連
# ================================

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

## 並列実行するための下請け関数
def process_chunk_for_pre_replacements(
    chunk: List[List[str]],
    replacements: List[Tuple[str, str, str]]
) -> Dict[str, List[str]]:
    """
    chunk (E_stem_with_Part_Of_Speech_list の一部) を処理し、
    { E_root : [safe_replaced_string, posカンマ区切り], ... } という部分辞書を作る。
    """
    local_dict = {}

    for item in chunk:
        # item = [E_root, pos] を想定
        if len(item) != 2:
            continue
        E_root, pos_info = item

        # 元質問の条件: 2文字未満はスキップ (あるいは 3文字以上がよければ修正)
        if len(E_root) < 2:
            continue

        # 既に local_dict に登録があれば、pos のマージのみ
        if E_root in local_dict:
            replaced_stem, existing_pos_str = local_dict[E_root]
            existing_pos_list = existing_pos_str.split(',')
            # pos_info が既存でなければ追加
            if pos_info not in existing_pos_list:
                existing_pos_list.append(pos_info)
                merged_pos_str = ",".join(existing_pos_list)
                local_dict[E_root] = [replaced_stem, merged_pos_str]
        else:
            # safe_replace で置換を実行 (今回のコア処理)
            replaced = safe_replace(E_root, replacements)
            local_dict[E_root] = [replaced, pos_info]

    return local_dict

########################################
# メイン関数: 並列実行で辞書をまとめて作る
########################################
## 並列実行で部分辞書を作り、マージして最終的な pre_replacements_dict_1 を作る関数
def parallel_build_pre_replacements_dict(
    E_stem_with_Part_Of_Speech_list: List[List[str]],
    replacements: List[Tuple[str, str, str]],
    num_processes: int = 4
) -> Dict[str, List[str]]:
    """
    :param E_stem_with_Part_Of_Speech_list: [[E_root, pos], [E_root, pos], ...]
    :param replacements: safe_replace(...) に使う置換リスト
    :param num_processes: プロセス数 (CPUコア数などに応じて)
    :return: { E_root: [ replaced_string, posカンマ区切り ] } の辞書
    """

    total_len = len(E_stem_with_Part_Of_Speech_list)
    if total_len == 0:
        return {}

    # === (a) まずデータを num_processes 個に分割する ===
    chunk_size = -(-total_len // num_processes)
    chunks = []
    start_index = 0
    for _ in range(num_processes):
        end_index = min(start_index + chunk_size, total_len)
        chunk = E_stem_with_Part_Of_Speech_list[start_index:end_index]
        chunks.append(chunk)
        start_index = end_index
        if start_index >= total_len:
            break

    # === (b) 各プロセスが process_chunk_for_pre_replacements(...) を実行 ===
    with multiprocessing.Pool(num_processes) as pool:
        partial_dicts = pool.starmap(
            process_chunk_for_pre_replacements,
            [(chunk, replacements) for chunk in chunks]
        )
        # partial_dicts は複数の { E_root: [ replaced_stem, posStr ], ... } のリスト

    # === (c) 部分辞書をマージ ===
    merged_dict = {}
    for partial_d in partial_dicts:
        for E_root, val in partial_d.items():
            replaced_stem, pos_str = val  # pos_str = "n" とか "n,v" とか

            if E_root not in merged_dict:
                # 全く新規のキー
                merged_dict[E_root] = [replaced_stem, pos_str]
            else:
                # 既にキーがある場合、pos をマージ (重複チェック含む)
                existing_replaced_stem, existing_pos_str = merged_dict[E_root]

                # replaced_stem が異なるケースが起きるかどうかは要検討
                # ここでは「最初に得られた replaced_stem を優先する」想定。
                existing_pos_list = existing_pos_str.split(',')
                new_pos_list = pos_str.split(',')
                # set union して重複を排除
                pos_merged = list(set(existing_pos_list) | set(new_pos_list))
                # pos_merged をソートして文字列化 (お好みで)
                pos_merged_str = ",".join(sorted(pos_merged))
                # replaced_stem は変えない (必要なら衝突処理)
                merged_dict[E_root] = [existing_replaced_stem, pos_merged_str]

    return merged_dict


# 追加(202502)
IDENTICAL_RUBY_PATTERN = re.compile(r'<ruby>([^<]+)<rt class="XXL_L">([^<]+)</rt></ruby>')
def remove_redundant_ruby_if_identical(text: str) -> str:
    """
    入力文字列中の <ruby>{1}<rt class="XXL_L">{2}</rt></ruby> を探し、
    {1} と {2} が完全一致している場合に、それらを {1} のみ
    (つまり <ruby>～</ruby> を取り除いて {1} に) 置換して返す関数。
    
    一致しない場合には置換を行わず、そのままのタグ構造を保持。
    """

    def replacer(match: re.Match) -> str:
        group1 = match.group(1)  # <ruby> 直後〜<rt class="XXL_L"> の手前にある文字列 ( {1} )
        group2 = match.group(2)  # <rt class="XXL_L">〜</rt> の間にある文字列 ( {2} )

        # {1} と {2} が完全に同じか？
        if group1 == group2:
            # 一致している場合は、<ruby>〜</ruby> を単に group1 ( {1} ) のみで置き換える
            return group1
        else:
            # 一致していない場合は、置換せずそのまま返す
            return match.group(0)

    # re.sub() を使うことで、テキスト中に何箇所あっても一括で置換される
    replaced_text = IDENTICAL_RUBY_PATTERN.sub(replacer, text)
    return replaced_text


