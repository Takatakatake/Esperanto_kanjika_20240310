#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import os
import re
import json
import multiprocessing


# In[2]:


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
# テスト用のエスペラント文
# text = "Ĝis revido! Mia nomo estas Ĵoĥano. Ĉu vi ŝatas ĥorojn? -Ne, mi s^tas felic^on. C^ S^ H^ c^ s^ h^  Ĉ Ĝ  Gxis revido! Mia nomo estas Jxohxano. Cxu vi sxatas hxorojn? -Ne, mi sxtas felicxon. Cx Sx Hx cx sx hx  Cx Gx"
# エスペラント文の文字形式の変換
# replaced_text = replace_esperanto_chars(text,x_to_circumflex)
# replaced_text =replace_esperanto_chars(text,hat_to_circumflex)
# replaced_text =replace_esperanto_chars(text,circumflex_to_hat)

# print("元のテキスト:", text)
# print("変換後のテキスト:", replaced_text)


# In[3]:


import json
# HTML形式における文字幅は、半角1,全角2,と明確に決まっているわけではなく、文字の種類に応じて大きく異なる。　例えば、同じ半角アルファベットでも最大幅の'm'が18pxであるとき、最小幅の'j'はわずか5pxしかなかったりする。
# この文字幅の違いは、ルビサイズを決めるときに大きな問題になる。
# そこで、最も一般的に用いられる'Arial形式,16px'の際の文字幅をJSON形式で保存しておき、おおよその文字幅の基準として用いることとした。 ("Unicode_BMP全范围文字幅(宽)_Arial16.json"は、"Unicode_BMP全范围文字幅(宽)检测处理_Arial16_JSON保存.ipynb"を用いて取得した。)

# 事前に作成した Unicode_BMP全范围文字幅(宽)_Arial16.json ファイルを読み込み
with open("Unicode_BMP全范围文字幅(宽)_Arial16.json", "r", encoding="utf-8") as fp:
    char_widths_dict = json.load(fp)

def measure_text_width_Arial16(text, char_widths_dict):
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
# text = "练"
# width_px = measure_text_width_Arial16(text, char_widths_dict)
# print(f"文字列: {text}",f",幅: {width_px}px")
# for i in list("abcdefghijklmnopqrstuvwxyz"):
#     print(i,': ',measure_text_width_Arial16(i, char_widths_dict))


# In[4]:


import re
def contains_digit(s):# 対象の文字列sに数字となりうる文字列(数字)が含まれるかどうかを確認する関数
    return any(char.isdigit() for char in s)

def import_placeholders(filename):# placeholder(占位符)をインポートするためだけの関数
    with open(filename, 'r') as file:
        placeholders = [line.strip() for line in file if line.strip()]
    return placeholders

def unify_halfwidth_spaces(text):
    """全角スペース(U+3000)は変更せず、半角スペースと視覚的に区別がつきにくい空白文字を
        ASCII半角スペース(U+0020)に統一する。連続した空白は1文字ずつ置換する。"""
    pattern = r"[\u00A0\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A]"# 対象とする空白文字をまとめたパターン
    return re.sub(pattern, " ", text)# マッチした部分を半角スペースに置換


# ⇓以下3つのセルについては逐一実行する必要はない。(202412)

# In[5]:


# まず、"世界语全部单词列表_约44700个(原pejvo.txt)_utf8转换_第二部分以后重点修正_追加2024年版PEJVO更新项目_最终版202501.txt"をhat形式から字上符形式に変換する。 (変換コード上では字上符形式で統一している。)
with open("世界语全部单词列表_约44700个(原pejvo.txt)_utf8转换_第二部分以后重点修正_追加2024年版PEJVO更新项目_最终版202501.txt", 'r', encoding='utf-8') as file:# "世界语全部单词列表_约44700个(原pejvo.txt)_utf8转换_第二部分以后重点修正_追加2024年版PEJVO更新项目_最终版202501.txt"本体については、基本的に今後変更は加えないようにする。
    text = file.read()
    converted_text=replace_esperanto_chars(text,hat_to_circumflex)# Hat形式を字上符形式に変換。
    converted_text=converted_text.lower()# 小文字に変換。
# 結果を"一时的_PEJVO(世界语全部单词列表)を小文字・字上符形式に转换.txt"に書き出す。
with open('一时的_PEJVO(世界语全部单词列表)を小文字・字上符形式に转换.txt', 'w', encoding='utf-8') as file:
    file.write(converted_text)


# In[6]:


import re
stem_with_part_of_speech_list=[]
# "一时的_PEJVO(世界语全部单词列表)を小文字・字上符形式に转换.txt"("世界语全部单词列表_约44700个(原pejvo.txt)_utf8转换_第二部分以后重点修正_追加2024年版PEJVO更新项目_最终版202501.txt"をhat形式から小文字、字上符形式に変換したもの)を開く。
with open("一时的_PEJVO(世界语全部单词列表)を小文字・字上符形式に转换.txt", 'r', encoding='utf-8') as file:
    # "一时的_PEJVO(世界语全部单词列表)を小文字・字上符形式に转换.txt"の各行をループ。
    for line in file:
        # ':'が出てくるまでの部分を取り出す。
        line=line.replace('-','/')# 20240618追加
        word = line.split(":")[0]
        word = word.lstrip('/')# 日本版,第一部分だけ
        # さらに取り出した部分を'-'、' '、','で分ける。","もごくまれに存在する(例:'tial')
        parts = re.split('-| |,', word)
        # 各部分をループし、単語の語尾の形式によって品詞分類しながら、その語尾をカットする。
        for jj in range(len(parts)):
            if jj>=0:# 第一部分と第二部分以後も('全部')
                part=parts[jj]
                if not (contains_digit(part) or len(part)<2):# 2文字以上 かつ　数字を含まない単語
                    if "/" in part:
                        AA=["/".join(part.split("/")[:-1])]
                        if part.endswith(('/o','/on','oj','/o!','ojn','on!')):
                            AA.append('名词')
                        elif part.endswith(('/a','/aj','/an','/an!')):
                            AA.append('形容词')
                        elif part.endswith(('/e','/e!')):
                            AA.append('副词')
                        elif part.endswith(('/e/n','/e/n!')):# '/e/n'は後で気をつける  圧倒的に少ない(72個)ので無詞にしたほうが(20240707確認)
                            AA=[part,"無詞"]
                        elif part.endswith(('/i','/u','/u!')):
                            AA.append('动词')
                        elif part.endswith(('/n')):
                            AA.append('n词')            
                    else:
                        AA=[part,"无词"]
                    stem_with_part_of_speech_list.append(AA)


# In[7]:


import json# 以後、辞書型、リスト型配列の一時保存にはJSON形式を用いる。JSON形式で保存しておくと、データの読み書きが容易であるし、"や'などの特殊文字も正しく処理してくれる。
# すべての単語の語尾が正しくカットされているかどうかチェックするため、JSON形式で一時保存。 ここまで情報の損失は殆どないはず。                                                                                       
with open("PEJVO(世界语全部单词列表)'全部'について、词尾(a,i,u,e,o,n等)をcutし、comma(,)で隔てて词性と併せて记录した列表(stem_with_part_of_speech_list).json", "w", encoding="utf-8") as g:
    json.dump(stem_with_part_of_speech_list, g, ensure_ascii=False, indent=2)  # ensure_ascii=FalseでUnicodeをそのまま出力


# ⇑ 上3つのセルについては逐一実行する必要はない。(202412)

# In[8]:


import json
# JSONデータを読み込む
with open("PEJVO(世界语全部单词列表)'全部'について、词尾(a,i,u,e,o,n等)をcutし、comma(,)で隔てて词性と併せて记录した列表(stem_with_part_of_speech_list).json", "r", encoding="utf-8") as g:
    stem_with_part_of_speech_list = json.load(g)
len(stem_with_part_of_speech_list)


# In[9]:


# ユーザーが選択した出力形式を出力するための関数
def output_format(main_text, ruby_content, format_type):
    width_ruby = measure_text_width_Arial16(ruby_content, char_widths_dict)
    width_main = measure_text_width_Arial16(main_text, char_widths_dict)
    
    if format_type == 'HTML格式_Ruby文字_大小调整':
        ratio_1 = width_ruby / width_main
        if ratio_1>(10/4):# main_text(親要素)とruby_content(ルビ)の文字幅の比率に応じて、ルビサイズを6段階に分ける。
            return '<ruby>{}<rt class="ruby-XS_S_S">{}</rt></ruby>'.format(main_text, ruby_content)# "や'などの特殊文字については、jsonモジュールが自動的にエスケープして、正しく処理してくれるので心配無用。
        elif  ratio_1>(10/5):
            return '<ruby>{}<rt class="ruby-S_S_S">{}</rt></ruby>'.format(main_text, ruby_content)
        elif  ratio_1>(10/6):
            return '<ruby>{}<rt class="ruby-M_M_M">{}</rt></ruby>'.format(main_text, ruby_content)
        elif  ratio_1>(10/7):
            return '<ruby>{}<rt class="ruby-L_L_L">{}</rt></ruby>'.format(main_text, ruby_content)
        elif  ratio_1>(10/8):
            return '<ruby>{}<rt class="ruby-XL_L_L">{}</rt></ruby>'.format(main_text, ruby_content)
        else:
            return '<ruby>{}<rt class="ruby-XXL_L_L">{}</rt></ruby>'.format(main_text, ruby_content)
    elif format_type == 'HTML格式_Ruby文字_大小调整_汉字替换':
        ratio2 = width_main / width_ruby
        if ratio2>(10/4):# ruby_content(親要素)とmain_text(ルビ)の文字幅の比率に応じて、ルビサイズを6段階に分ける。
            return '<ruby>{}<rt class="ruby-XS_S_S">{}</rt></ruby>'.format(ruby_content, main_text)# "や'などの特殊文字については、jsonモジュールが自動的にエスケープして、正しく処理してくれるので心配無用。
        elif  ratio2>(10/5):
            return '<ruby>{}<rt class="ruby-S_S_S">{}</rt></ruby>'.format(ruby_content, main_text)
        elif  ratio2>(10/6):
            return '<ruby>{}<rt class="ruby-M_M_M">{}</rt></ruby>'.format(ruby_content, main_text)
        elif  ratio2>(10/7):
            return '<ruby>{}<rt class="ruby-L_L_L">{}</rt></ruby>'.format(ruby_content, main_text)
        elif  ratio2>(10/8):
            return '<ruby>{}<rt class="ruby-XL_L_L">{}</rt></ruby>'.format(ruby_content, main_text)
        else:
            return '<ruby>{}<rt class="ruby-XXL_L_L">{}</rt></ruby>'.format(ruby_content, main_text)
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


# In[10]:


# 上の作業で抽出した、'PEJVO(世界语全部单词列表)'全部'について、词尾(a,i,u,e,o,n等)をcutし、comma(,)で隔てて词性と併せて记录した列表'(stem_with_part_of_speech_list)を文字列(漢字)置換するための、置換リストを作成していく。
# "'PEJVO(世界语全部单词列表)'全部'について、词尾(a,i,u,e,o,n等)をcutし、comma(,)で隔てて词性と併せて记录した列表'(stem_with_part_of_speech_list)を文字列(漢字)置換し終えたリスト"こそが最終的な置換リスト(replacements_final_list)の大元になる。
# '既に'/'(スラッシュ)によって完全に語根分解された状態の単語'が対象であれば、文字数の多い語根順に文字列(漢字)置換するだけで、理論上完璧な精度の置換ができるはず。
# ただし、その完璧な精度の置換のためにはあらかじめ"世界语全部单词列表_约44700个(原pejvo.txt)_utf8转换_第二部分以后重点修正_追加2024年版PEJVO更新项目_最终版202501.txt"から"世界语全部单词列表_约44700个(原pejvo.txt)_utf8转换_第二部分以后重点修正_追加2024年版PEJVO更新项目_最终版202501.txt＿から＿世界语全部词根_约11148个_202501.txt＿を抽出.ipynb"を用いてエスペラントの全語根を抽出しておく必要がある。

# 一旦辞書型を使う。(後で内容(value)を更新するため)
temporary_replacements_dict={}
with open("世界语全部词根_约11148个_202501.txt", 'r', encoding='utf-8') as file:
    # "世界语全部词根_约11148个_202501.txt"は"世界语全部单词列表_约44700个(原pejvo.txt)_utf8转换_第二部分以后重点修正_追加2024年版PEJVO更新项目_最终版202501.txt"から"世界语全部单词列表_约44700个(原pejvo.txt)_utf8转换_第二部分以后重点修正_追加2024年版PEJVO更新项目_最终版202501.txt＿から＿世界语全部词根_约11148个_202501.txt＿を抽出.ipynb"を用いて抽出したエスペラントの全語根である。
    roots = file.readlines()
    for root in roots:
        root = root.strip()
        if not root.isdigit():# 混入していた数字の'10'と'7'を削除
            temporary_replacements_dict[root]=[root,len(root)]# 各エスペラント語根に対する'置換後の文字列'(この作業では元の置換対象の語根のまま)と、その置換優先順序として、'置換対象の語根の文字数'を設定。　置換優先順序の数字が大きい('置換対象の語根の文字数'が多い)ほど、先に置換されるようにする。
len(temporary_replacements_dict)


# In[11]:


# 上のセルでの作業に引き続き、"'PEJVO(世界语全部单词列表)'全部'について、词尾(a,i,u,e,o,n等)をcutし、comma(,)で隔てて词性と併せて记录した列表'(stem_with_part_of_speech_list)を文字列(漢字)置換するための、置換リスト"を作成していく。　
# ここでは置換リスト(辞書型配列)に自分で作成したエスペラント語根の日本語訳ルビリストを反映させる。
import pandas as pd

# ⇓以下のcsvファイルの内容を色々カスタマイズすることで、様々な内容の文字列(漢字)置換が可能になる。
input_csv_file="日本語訳ルビリスト_20250112_字上符形式.csv"

# with open(input_csv_file, 'r', encoding='utf-8') as file:
#     for line in file:
#         line = line.strip()
#         j = line.split(',')
#         if len(j)>=2:
#             E_root,hanzi_or_meaning=j[0],j[1]
#             if (hanzi_or_meaning!='') and (E_root!='') and ('#' not in E_root):# この条件によって関係のない行を除外。
#                 temporary_replacements_dict[E_root]=[output_format(E_root, hanzi_or_meaning, format_type),len(E_root)]# 辞書型配列では要素(key)に対する値(value)を後から更新できることを利用している。


# CSVファイルの処理に最適化されている'pandas'を使うことにした。
CSV_data_imported = pd.read_csv(input_csv_file, encoding="utf-8")
for _, (E_root, hanzi_or_meaning) in CSV_data_imported.iterrows():
    if pd.notna(E_root) and pd.notna(hanzi_or_meaning) and '#' not in E_root and (E_root != '') and (hanzi_or_meaning != ''):  # 条件を満たす行のみ処理
        temporary_replacements_dict[E_root] = [output_format(E_root, hanzi_or_meaning, format_type),len(E_root)]

with open("一时的な替换用の辞書(字典)型配列(temporary_replacements_dict).json", "w", encoding="utf-8") as g:
    json.dump(temporary_replacements_dict, g, ensure_ascii=False, indent=2)  # ensure_ascii=FalseでUnicodeをそのまま出力
# with open("一时的な替换用の辞書(字典)型配列(temporary_replacements_dict).json", "r", encoding="utf-8") as g:
#     temporary_replacements_dict_experiment = json.load(g)


# In[12]:


# 辞書型をリスト型に戻した上で、文字数順に並び替え。
# "'PEJVO(世界语全部单词列表)'全部'について、词尾(a,i,u,e,o,n等)をcutし、comma(,)で隔てて词性と併せて记录した列表'(stem_with_part_of_speech_list)を文字列(漢字)置換するための、置換リスト"を置換優先順位の数字の大きさ順(ここでは文字数順)にソート。

temporary_replacements_list_1=[]
for old,new in temporary_replacements_dict.items():
    temporary_replacements_list_1.append((old,new[0],new[1]))
temporary_replacements_list_2 = sorted(temporary_replacements_list_1, key=lambda x: x[2], reverse=True)

# '置換リスト'の各置換に対してplaceholder(占位符)を追加し、リスト'temporary_replacements_list_final'として完成させる。
# placeholder法とは、既に置換を終えた文字列が後続の置換によって重複して置換されてしまうことを避けるために、その置換を終えた部分に一時的に無関係な文字列(placeholder)を置いておいて、
# 全ての置換が終わった後に、改めてその'無関係な文字列(placeholder)'から'目的の置換後文字列'に変換していく手法である。

imported_placeholders = import_placeholders('占位符(placeholders)_$20987$-$499999$_全域替换用.txt')

temporary_replacements_list_final=[]
for kk in range(len(temporary_replacements_list_2)):
    temporary_replacements_list_final.append([temporary_replacements_list_2[kk][0],temporary_replacements_list_2[kk][1],imported_placeholders[kk]])


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


# リスト'temporary_replacements_list_final'("'PEJVO(世界语全部单词列表)'全部'について、词尾(a,i,u,e,o,n等)をcutし、comma(,)で隔てて词性と併せて记录した列表'(stem_with_part_of_speech_list)を文字列(漢字)置換するための、一時的な置換リスト"の完成版)の内容確認
with open("一时的な替换用のリスト(列表)型配列(temporary_replacements_list_final).json", "w", encoding="utf-8") as g:
    json.dump(temporary_replacements_list_final, g, ensure_ascii=False, indent=2)  # ensure_ascii=FalseでUnicodeをそのまま出力
# with open("一时的な替换用のリスト(列表)型配列(temporary_replacements_list_final).json", "r", encoding="utf-8") as g:
#     temporary_replacements_list_final= json.load(g)


# 以下の2つのセルは逐一実行する必要はない。実行にも20秒程度かかる。

# In[13]:


# このセルの処理が全体を通して一番時間がかかる(数十秒)
# 'PEJVO(世界语全部单词列表)'全部'について、词尾(a,i,u,e,o,n等)をcutし、comma(,)で隔てて词性と併せて记录した列表'(stem_with_part_of_speech_list)を実際にリスト'temporary_replacements_list_final'(一時的な置換リストの完成版)によって文字列(漢字)置換。　
# ここで作成される、"文字列(漢字)置換し終えたリスト(辞書型配列)"(pre_replacements_dict_1)こそが最終的な置換リスト(replacements_final_list)の大元になる。
# リスト'stem_with_part_of_speech_list'までは情報の損失は殆どないはず。

pre_replacements_dict_1={}
for j in stem_with_part_of_speech_list:# 20秒ほどかかる。　先にリストの要素を全て結合して、一つの文字列にしてから置換する方法を試しても(上述)、さほど高速化しなかった。
    if len(j)==2:# (j[0]がエスペラント語根、j[1]が品詞。)
        if len(j[0])>=2:# 2文字以上のエスペラント語根のみが対象  3で良いのでは(202412)
            if j[0] in pre_replacements_dict_1:
                if j[1] not in pre_replacements_dict_1[j[0]][1]:
                    pre_replacements_dict_1[j[0]] = [pre_replacements_dict_1[j[0]][0],pre_replacements_dict_1[j[0]][1] + ',' + j[1]]# 複数品詞の追加
            else:
                pre_replacements_dict_1[j[0]]=[safe_replace(j[0], temporary_replacements_list_final),j[1]]# 辞書型配列の追加法


# In[14]:


# 上の作業で作成した辞書型配列(pre_replacements_dict_1)の最初から20個分を表示
for key, value in dict(list(pre_replacements_dict_1.items())[9:20]).items():
    print(f"{key}: {value}")
with open("替换用の辞書(字典)型配列(pre_replacements_dict_1).json", "w", encoding="utf-8") as g:
    json.dump(pre_replacements_dict_1, g, ensure_ascii=False, indent=2)  # ensure_ascii=FalseでUnicodeをそのまま出力
# with open("替换用の辞書(字典)型配列(pre_replacements_dict_1).json", "r", encoding="utf-8") as g:
#     pre_replacements_dict_1_experiment = json.load(g)


# ⇑ 上2つのセルは逐一実行する必要はない。実行にも20秒程度かかる。

# In[15]:


import json
# JSONファイルから辞書を再構築する
with open("替换用の辞書(字典)型配列(pre_replacements_dict_1).json", "r", encoding="utf-8") as g:
    pre_replacements_dict_1 = json.load(g)
# 再構築された辞書の内容を表示
for key, value in dict(list(pre_replacements_dict_1.items())[:5]).items():
    print(f"{key}: {value}")


# In[16]:


# 辞書型配列'pre_replacements_dict_1'の中で複数通りに語根分解されてしまっているケースが存在しないかを確認
# スラッシュを取り除いたキーでデータを整理するための辞書
normalized_keys = {}

# 各キーからスラッシュを取り除き、既存のキーとして整理
for old, value in pre_replacements_dict_1.items():
    # スラッシュを取り除く
    normalized_key = old.replace('/', '')

    # 辞書に追加
    if normalized_key not in normalized_keys:
        normalized_keys[normalized_key] = []
    normalized_keys[normalized_key].append((old, value))

# 抜き出すためのファイル出力
with open("辞書(字典)型配列(pre_replacements_dict_1)の重复词根分解示例.txt", 'w', encoding='utf-8') as file:
    for key, entries in normalized_keys.items():
        # 同じ語根を持つ要素が複数ある場合のみファイルに書き込む
        if len(entries) > 1:
            for old, value in entries:
                file.write(f'  {old},{value[0]},{value[1]}  ||')
            file.write('\n')

# # 各語根ごとに最長のキー(一番細かく語根分解されているもの)を保持する辞書
# max_length_keys = {}
# # スラッシュを取り除いた語根をキーとして、最長のキーと値を保存
# for old, value in pre_replacements_dict_1.items():
#     # スラッシュを取り除く
#     normalized_key = old.replace('/', '')
#     # 辞書にこの語根が存在するか、存在する場合は現在のキーと比較
#     if normalized_key not in max_length_keys or len(max_length_keys[normalized_key][0]) < len(old):
#         max_length_keys[normalized_key] = (old, value)

# # 最終的な辞書を作成   pre_replacements_dict_1_ と　pre_replacements_dict_1 は 単語3個分("pre_replacements_dict_1_重复.txt"の分)しか変わらない、ほとんど同じ辞書型配列である。
# pre_replacements_dict_1_ = {k: v for _, (k, v) in max_length_keys.items()}

# len(pre_replacements_dict_1),len(pre_replacements_dict_1_)

# with open("替换用の辞書(字典)型配列(pre_replacements_dict_1_).json", "w", encoding="utf-8") as g:
#     json.dump(pre_replacements_dict_1_, g, ensure_ascii=False, indent=2)  # ensure_ascii=FalseでUnicodeをそのまま出力
# with open("替换用の辞書(字典)型配列(pre_replacements_dict_1_).json", "r", encoding="utf-8") as g:
#     pre_replacements_dict_1_experiment = json.load(g)

# # 品詞によって語根分解の仕方を変えることは可能か？20241207


# In[17]:


keys_to_remove = ['domen', 'teren','posten']# 後でdomen/o,domen/a,domen/e等を追加する。　→確認済み(24/12)
for key in keys_to_remove:
    pre_replacements_dict_1.pop(key, None)  # 'None' はキーが存在しない場合に返すデフォルト


# ここから、"'PEJVO(世界语全部单词列表)'全部'について、词尾(a,i,u,e,o,n等)をcutし、comma(,)で隔てて词性と併せて记录した列表'(stem_with_part_of_speech_list)をリスト'temporary_replacements_list_final'(一時的な置換リストの完成版)によって文字列(漢字)置換し終えたリスト(辞書型配列)"(pre_replacements_dict_1)を最終的な置換リスト(replacements_final_list)に成形していく。

# In[55]:


# 品詞の追加(特に動詞)　あまり使わない。
# pre_replacements_dict_1["sen/son"][1]=pre_replacements_dict_1["sen/son"][1]+",动词"


# In[44]:


# 上のセルで行われた、辞書型配列'pre_replacements_dict_1'の重複語根分解のチェックと、ここでの辞書型配列'pre_replacements_dict_2'の上書き更新によって、複数通りに語根分解されるケースは排除できていると考えられる。　品詞別に語根分解の方法を残すべきではないのか→日本語版の全単語語根分解リストについては解決。??202412

#  pre_replacements_dict_1→pre_replacements_dict_2  ("'PEJVO(世界语全部单词列表)'全部'について、词尾(a,i,u,e,o,n等)をcutし、comma(,)で隔てて词性と併せて记录した列表'(stem_with_part_of_speech_list)をリスト'temporary_replacements_list_final'(一時的な置換リストの完成版)によって文字列(漢字)置換し終えたリスト(辞書型配列)"(pre_replacements_dict_1)を最終的な置換リスト(replacements_final_list)に成形していく。)
# pre_replacements_dict_1の'置換対象の単語'、'置換後の文字列'から"/"を抜く(HTML形式にしたい場合、"</rt></ruby>"は"/"を含むので要注意！)。
# 新たに置換優先順位を表す数字を追加し(置換する単語は'文字数×10000'、置換しない単語は'文字数×10000-3000')、辞書型配列pre_replacements_dict_2として保存。
pre_replacements_dict_2={}
for i,j in pre_replacements_dict_1.items():# (iが置換対象の単語、j[0]が置換後の文字列、j[1]が品詞。)
    if i==j[0]:# 置換しない単語  # ⇓の右辺では、HTMLのルビ形式に含まれる'/'を避けながら'置換後の文字列'から"/"を抜く処理を行っている。HTML形式でなくてもしても大丈夫な処理なので、出力形式が'括弧(号)格式'や'替换后文字列のみ(仅)保留(简单替换)'であっても心配無用。
        pre_replacements_dict_2[i.replace('/', '')]=[j[0].replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),j[1],len(i.replace('/', ''))*10000-3000]# 置換しない単語は優先順位を下げる
    else:
        pre_replacements_dict_2[i.replace('/', '')]=[j[0].replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),j[1],len(i.replace('/', ''))*10000]

with open("替换用の辞書(字典)型配列(pre_replacements_dict_2).json", "w", encoding="utf-8") as g:
    json.dump(pre_replacements_dict_2, g, ensure_ascii=False, indent=2)  # ensure_ascii=FalseでUnicodeをそのまま出力
# with open("替换用の辞書(字典)型配列(pre_replacements_dict_2).json", "r", encoding="utf-8") as g:
#     pre_replacements_dict_2 = json.load(g)


# In[45]:


# 基本的には动词に対してのみ活用語尾・接尾辞を追加し、置換対象の単語の文字数を増やす(置換の優先順位を上げる。)

verb_suffix_2l={'as':'as', 'is':'is', 'os':'os', 'us':'us','at':'at','it':'it','ot':'ot', 'ad':'ad','iĝ':'iĝ','ig':'ig','ant':'ant','int':'int','ont':'ont'}

verb_suffix_2l_2={}
for original_verb_suffix,replaced_verb_suffix in verb_suffix_2l.items():
    verb_suffix_2l_2[original_verb_suffix]=safe_replace(replaced_verb_suffix, temporary_replacements_list_final)
print(verb_suffix_2l_2)


# In[46]:


# 一番の工夫ポイント(如何にして置換の優先順位を定め、置換精度を向上させるか。)
# 基本は単語の文字数が多い順に置換していくことになるが、
# 例えば、"置換対象の単語に接頭辞、接尾辞を追加し、単語の文字数を増やし、置換の優先順位を上げたものを、置換対象の単語として新たに追加する。"などが、置換精度を上げる方策として考えられる。
# しかし、いろいろ試した結果、动词に対してのみ活用語尾・接尾辞を追加し、置換対象の単語の文字数を増やす(置換の優先順位を上げる。)のが、ベストに近いことがわかった。

#  pre_replacements_dict_1→pre_replacements_dict_2→pre_replacements_dict_3  ("'PEJVO(世界语全部单词列表)'全部'について、词尾(a,i,u,e,o,n等)をcutし、comma(,)で隔てて词性と併せて记录した列表'(stem_with_part_of_speech_list)をリスト'temporary_replacements_list_final'(一時的な置換リストの完成版)によって文字列(漢字)置換し終えたリスト(辞書型配列)"(pre_replacements_dict_1)を最終的な置換リスト(replacements_final_list)に成形していく。)

overlap_1,overlap_2,overlap_3,overlap_4,overlap_5,overlap_6,overlap_7,overlap_8=[],[],[],[],[],[],[],[]
overlap_9,overlap_10,overlap_11,overlap_12,overlap_13,overlap_14,overlap_15,overlap_16=[],[],[],[],[],[],[],[]
overlap_2_2,overlap_2_3=[],[]
unchangeable_after_creation_list=[]
count_0,count_1,count_2,count_3,count_4,count_5=0,0,0,0,0,0
adj_1,adj_2,adj_3,adj_4=0,0,0,0
AN_replacement = safe_replace('an', temporary_replacements_list_final)
AN_treatment=[]

# pre_replacements_dict_3内での重複の検査をし、それを元に、以下のセルにおける修正がなされている。
pre_replacements_dict_3={}
# 辞書をコピーする
pre_replacements_dict_2_copy = pre_replacements_dict_2.copy()# これがあるので、2回繰り返しするときは2個前のセルに戻ってpre_replacements_dict_2を作り直してからでないといけない。
for i,j in pre_replacements_dict_2_copy.items():# j[0]:置換後の文字列　j[1]:品詞 j[2]:置換優先順位
    if i.endswith('an') and (AN_replacement in j[0]) and ("名词" in j[1]) and (i[:-2] in pre_replacements_dict_2_copy):# and ("形容词" in pre_replacements_dict_2_copy[i[:-2]][1]) 190個→121個
        AN_treatment.append([i,j[0]])
        pre_replacements_dict_2.pop(i, None)# これで形容詞語尾のanが接尾辞an(員)として、誤って置換されてしまうことは大体防げたハズ。　逆に、接尾辞an(員)が形容詞語尾のanとして、置換されない場合は、後述の局所置換によってその都度対処する。 (202501)
        for k in ["o","a","e"]:
            if not i+k in pre_replacements_dict_2_copy:
                pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-2000]
    elif (j[1] == "名词") and (len(i)<=6) and not(j[2]==60000 or j[2]==50000 or j[2]==40000 or j[2]==30000 or j[2]==20000):# 名词だけで、6文字以下で、置換しないやつ  # 置換ミスを防ぐための条件(20240614) altajo,aviso,malm,abes 固有名词対策  意味ふりがなのときは再検討
        for k in ["o"]:
            if not i+k in pre_replacements_dict_2_copy:
                pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-2000]# 実質8000 # 既存でないものは優先順位を大きく下げる→普通の品詞接尾辞が既存でないという言い方はおかしい気もするが。(202412)
                count_0+=1
            # elif j[0]+k != pre_replacements_dict_2_copy[i+k][0]:# ←本当はこちらの条件のほうが、既に存在してなおかつ語根分解も異なる単語を抽出して来れるため、より良い。
            else:# 既に存在するのであれば、元々の語根分解を優先し、何もしない。
                overlap_1.append([i+k,pre_replacements_dict_2_copy[i+k][0],j[0]+k])# 語根分解の不一致が起きていないかを確認(pre_replacements_dict_2_copy[i+k][0],j[0]+k で)
                # ['buro', 'haloo', 'tauxro', 'unesko']の4個
        pre_replacements_dict_2.pop(i, None)
        count_1+=1


for i,j in pre_replacements_dict_2.items():# j[0]:置換後の文字列　j[1]:品詞 j[2]:置換優先順位
    if j[2]==20000:# 2文字で置換するやつ# len(i)<=2:# 1文字は存在しないはずではある。
        # 基本的に非动词の2文字の語根単体を以て置換することはない。　ただし、世界语全部单词_大约44700个(原pejvo.txt).txtに最初から含まれている2文字の語根は既に置換されており、実際の置換にも反映されることになる。
        # 2文字の語根でも、动词については活用語尾を追加することで、自動的に+2文字以上できるので追加した。
        if "名词" in j[1]:
            for k in ["o","on",'oj']:# "ojn"は不要か
                if not i+k in pre_replacements_dict_2:
                    pre_replacements_dict_3[' '+i+k]=[' '+j[0]+k,j[2]+(len(k)+1)*10000-5000]
                # elif j[0]+k != pre_replacements_dict_2[i+k][0]:# ←本当はこちらの条件のほうが、既に存在してなおかつ語根分解も異なる単語を抽出してこれるため、より良い。
                else:# 既に存在するのであれば、元々の語根分解を優先し、何もしない。
                    overlap_2.append([i+k,pre_replacements_dict_2[i+k][0],j[0]+k])
                # [['alo', '<ruby>alo<rt class="ruby-M_M_M">アロエ</rt></ruby>', '<ruby>al<rt class="ruby-S_S_S">~の方へ</rt></ruby>o'], ['duon', '<ruby>du<rt class="ruby-X_X_X">二</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>du<rt class="ruby-X_X_X">二</rt></ruby>on'], ['okon', '<ruby>ok<rt class="ruby-X_X_X">八</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>ok<rt class="ruby-X_X_X">八</rt></ruby>on']]
        if "形容词" in j[1]:
            for k in ["a","aj",'an']:# "ajn"は不要か  # sia pian ,'an 'も不要
                if not i+k in pre_replacements_dict_2:# if not なしのほうが良い
                    pre_replacements_dict_3[' '+i+k]=[' '+j[0]+k,j[2]+(len(k)+1)*10000-5000]
                else:# if not なしのほうが良いというのは既に存在しようとしまいと新しく作った方の語根分解を優先するということ。if not を付けたとしても、elseの方でも同じ処理をするようにすれば何の問題もない。
                    pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-5000]# ここは空白なしにすることに(2412)
                    overlap_2_2.append([i+k,pre_replacements_dict_2[i+k][0],j[0]+k])# "eman"は元のほうが良いだろうが、出てきたとしても固有名詞であろうからOK。
                    unchangeable_after_creation_list.append(i+k)# 新しく定めた語根分解が後で更新されてしまわないように、unchangeable_after_creation_list に追加。
                    # [['sia', 'sia', '<ruby>si<rt class="ruby-M_M_M">自分</rt></ruby>a'], ['eman', 'eman', '<ruby>em<rt class="ruby-M_M_M">傾向</rt></ruby>an'], ['lian', '<ruby>lian<rt class="ruby-S_S_S">[植]つる植物</rt></ruby>', '<ruby>li<rt class="ruby-X_X_X">彼</rt></ruby>an'], ['pian', '<ruby>pian<rt class="ruby-M_M_M">[楽]ピアノ</rt></ruby>', '<ruby>pi<rt class="ruby-S_S_S">信心深い</rt></ruby>an']]
            adj_1+=1
        if "副词" in j[1]:
            for k in ["e"]:
                if not i+k in pre_replacements_dict_2:# if not なしのほうが良い
                    pre_replacements_dict_3[' '+i+k]=[' '+j[0]+k,j[2]+(len(k)+1)*10000-5000]
                else:
                    pre_replacements_dict_3[' '+i+k]=[' '+j[0]+k,j[2]+(len(k)+1)*10000-5000]
                    overlap_2_3.append([i+k,pre_replacements_dict_2[i+k][0],j[0]+k])# ege   エーゲ海を意味するegeoを元の辞書に追加 今思えば、偽語根分解する必要は全く無かった。(24/12)
        if "动词" in j[1]:
            for k1,k2 in verb_suffix_2l_2.items():
                if not i+k1 in pre_replacements_dict_2:# j[0]:置換後の文字列　j[1]:品詞 j[2]:置換優先順位
                    pre_replacements_dict_3[i+k1]=[j[0]+k2,j[2]+len(k1)*10000-3000]
                elif j[0]+k2 != pre_replacements_dict_2[i+k1][0]:
                    pre_replacements_dict_3[i+k1]=[j[0]+k2,j[2]+len(k1)*10000-3000]# 新しく作った方の語根分解を優先する
                    print(i+k1,pre_replacements_dict_3[i+k1],[j[0]+k2,j[2]+len(k1)*10000-3000])
                    overlap_3.append([i+k1,pre_replacements_dict_2[i+k1][0],j[0]+k2])
                    unchangeable_after_creation_list.append(i+k1)# 新しく定めた語根分解が後で更新されてしまわないように、unchangeable_after_creation_list に追加。
                # [['agat', '<ruby>agat<rt class="ruby-M_M_M">[鉱]メノウ</rt></ruby>', '<ruby>ag<rt class="ruby-S_S_S">行動する</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['agit', '<ruby>agit<rt class="ruby-S_S_S">(を)扇動する</rt></ruby>', '<ruby>ag<rt class="ruby-S_S_S">行動する</rt></ruby><ruby>it<rt class="ruby-S_S_S">受動完了</rt></ruby>'], ['amas', '<ruby>amas<rt class="ruby-M_M_M">集積;大衆</rt></ruby>', '<ruby>am<rt class="ruby-S_S_S">愛する</rt></ruby><ruby>as<rt class="ruby-S_S_S">現在形</rt></ruby>'], ['iris', '<ruby>iris<rt class="ruby-M_M_M">[解]虹彩</rt></ruby>', '<ruby>ir<rt class="ruby-M_M_M">行く</rt></ruby><ruby>is<rt class="ruby-S_S_S">過去形</rt></ruby>'], ['irit', 'irit', '<ruby>ir<rt class="ruby-M_M_M">行く</rt></ruby><ruby>it<rt class="ruby-S_S_S">受動完了</rt></ruby>']]
            for k in ["u ","i ","u","i"]:# 动词の"u","i"単体の接尾辞は後ろが空白と決まっているので、2文字分増やすことができる。
                if not i+k in pre_replacements_dict_2:
                    pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]
                elif j[0]+k != pre_replacements_dict_2[i+k][0]:
                    overlap_4.append([i+k,pre_replacements_dict_2[i+k][0],j[0]+k])# 該当なし
        count_2+=1
        continue

    else:
        if not i in unchangeable_after_creation_list:# unchangeable_after_creation_list に含まれる場合は除外。(上記で新しく定めた語根分解が更新されてしまわないようにするため。)
            pre_replacements_dict_3[i]=[j[0],j[2]]# 品詞情報はここで用いるためにあった。以後は不要なので省いていく。
        if j[2]==60000 or j[2]==50000 or j[2]==40000 or j[2]==30000:# 文字数が比較的少なく(<=5)、実際に置換するエスペラント語根(文字数×10000)のみを対象とする 
            if "名词" in j[1]:# 名词については形容词、副词と違い、置換しないものにもoをつける。
                for k in ["o","on",'oj']:
                    if not i+k in pre_replacements_dict_2:
                        pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]# 既存でないものは優先順位を大きく下げる→普通の品詞接尾辞が既存でないという言い方はおかしい気がしてきた。(20240612)
                    elif j[0]+k != pre_replacements_dict_2[i+k][0]:
                        pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]# 新しく作った方の語根分解を優先する
                        overlap_5.append([i+k,pre_replacements_dict_2[i+k][0],j[0]+k])
                        unchangeable_after_creation_list.append(i+k)
                    # on系[['nombron', '<ruby>nombr<rt class="ruby-X_X_X">数</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>nombr<rt class="ruby-X_X_X">数</rt></ruby>on'], ['patron', '<ruby>patron<rt class="ruby-X_X_X">後援者</rt></ruby>', '<ruby>patr<rt class="ruby-X_X_X">父</rt></ruby>on'], ['karbon', '<ruby>karbon<rt class="ruby-L_L_L">[化]炭素</rt></ruby>', '<ruby>karb<rt class="ruby-X_X_X">炭</rt></ruby>on'], ['ciklon', '<ruby>ciklon<rt class="ruby-X_X_X">低気圧</rt></ruby>', '<ruby>cikl<rt class="ruby-X_X_X">周期</rt></ruby>on'], ['aldon', '<ruby>al<rt class="ruby-S_S_S">~の方へ</rt></ruby><ruby>don<rt class="ruby-M_M_M">与える</rt></ruby>', '<ruby>ald<rt class="ruby-M_M_M">アルト</rt></ruby>on'], ['balon', '<ruby>balon<rt class="ruby-X_X_X">気球</rt></ruby>', '<ruby>bal<rt class="ruby-M_M_M">舞踏会</rt></ruby>on'], ['baron', '<ruby>baron<rt class="ruby-X_X_X">男爵</rt></ruby>', '<ruby>bar<rt class="ruby-L_L_L">障害</rt></ruby>on'], ['baston', '<ruby>baston<rt class="ruby-X_X_X">棒</rt></ruby>', '<ruby>bast<rt class="ruby-M_M_M">[植]じん皮</rt></ruby>on'], ['magneton', '<ruby>magnet<rt class="ruby-L_L_L">[理]磁石</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>magnet<rt class="ruby-L_L_L">[理]磁石</rt></ruby>on'], ['beton', 'beton', '<ruby>bet<rt class="ruby-M_M_M">ビート</rt></ruby>on'], ['bombon', '<ruby>bombon<rt class="ruby-L_L_L">キャンデー</rt></ruby>', '<ruby>bomb<rt class="ruby-X_X_X">爆弾</rt></ruby>on'], ['breton', 'breton', '<ruby>bret<rt class="ruby-X_X_X">棚</rt></ruby>on'], ['burgxon', '<ruby>burgxon<rt class="ruby-X_X_X">芽</rt></ruby>', '<ruby>burgx<rt class="ruby-M_M_M">ブルジョワ</rt></ruby>on'], ['centon', '<ruby>cent<rt class="ruby-X_X_X">百</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>cent<rt class="ruby-X_X_X">百</rt></ruby>on'], ['milon', '<ruby>mil<rt class="ruby-X_X_X">千</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>mil<rt class="ruby-X_X_X">千</rt></ruby>on'], ['kanton', '<ruby>kanton<rt class="ruby-M_M_M">(フランスの)郡</rt></ruby>', '<ruby>kant<rt class="ruby-M_M_M">(を)歌う</rt></ruby>on'], ['citron', '<ruby>citron<rt class="ruby-M_M_M">[果]シトロン</rt></ruby>', '<ruby>citr<rt class="ruby-M_M_M">[楽]チター</rt></ruby>on'], ['platon', 'platon', '<ruby>plat<rt class="ruby-L_L_L">平たい</rt></ruby>on'], ['dekon', '<ruby>dek<rt class="ruby-X_X_X">十</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>dek<rt class="ruby-X_X_X">十</rt></ruby>on'], ['kvaron', '<ruby>kvar<rt class="ruby-X_X_X">四</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>kvar<rt class="ruby-X_X_X">四</rt></ruby>on'], ['kvinon', '<ruby>kvin<rt class="ruby-X_X_X">五</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>kvin<rt class="ruby-X_X_X">五</rt></ruby>on'], ['seson', '<ruby>ses<rt class="ruby-X_X_X">六</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>ses<rt class="ruby-X_X_X">六</rt></ruby>on'], ['trion', '<ruby>tri<rt class="ruby-X_X_X">三</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>tri<rt class="ruby-X_X_X">三</rt></ruby>on'], ['karton', '<ruby>karton<rt class="ruby-X_X_X">厚紙</rt></ruby>', '<ruby>kart<rt class="ruby-L_L_L">カード</rt></ruby>on'], ['foton', '<ruby>fot<rt class="ruby-S_S_S">写真を撮る</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>fot<rt class="ruby-S_S_S">写真を撮る</rt></ruby>on'], ['peron', '<ruby>peron<rt class="ruby-X_X_X">階段</rt></ruby>', '<ruby>per<rt class="ruby-M_M_M">よって</rt></ruby>on'], ['elektron', '<ruby>elektr<rt class="ruby-X_X_X">電気</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>elektr<rt class="ruby-X_X_X">電気</rt></ruby>on'], ['drakon', 'drakon', '<ruby>drak<rt class="ruby-X_X_X">竜</rt></ruby>on'], ['mondon', '<ruby>mon<rt class="ruby-L_L_L">金銭</rt></ruby><ruby>don<rt class="ruby-M_M_M">与える</rt></ruby>', '<ruby>mond<rt class="ruby-X_X_X">世界</rt></ruby>on'], ['pension', '<ruby>pension<rt class="ruby-X_X_X">下宿屋</rt></ruby>', '<ruby>pensi<rt class="ruby-X_X_X">年金</rt></ruby>on'], ['ordon', '<ruby>ordon<rt class="ruby-M_M_M">(を)命令する</rt></ruby>', '<ruby>ord<rt class="ruby-L_L_L">順序</rt></ruby>on'], ['eskadron', 'eskadron', '<ruby>eskadr<rt class="ruby-L_L_L">[軍]艦隊</rt></ruby>on'], ['senton', '<ruby>sen<rt class="ruby-S_S_S">(~)なしで</rt></ruby><ruby>ton<rt class="ruby-M_M_M">[楽]楽音</rt></ruby>', '<ruby>sent<rt class="ruby-M_M_M">(を)感じる</rt></ruby>on'], ['eston', 'eston', '<ruby>est<rt class="ruby-S_S_S">(~)である</rt></ruby>on'], ['fanfaron', '<ruby>fanfaron<rt class="ruby-L_L_L">大言壮語する</rt></ruby>', '<ruby>fanfar<rt class="ruby-S_S_S">[楽]ファンファーレ</rt></ruby>on'], ['fero', 'fero', '<ruby>fer<rt class="ruby-X_X_X">鉄</rt></ruby>o'], ['feston', '<ruby>feston<rt class="ruby-X_X_X">花綱</rt></ruby>', '<ruby>fest<rt class="ruby-M_M_M">(を)祝う</rt></ruby>on'], ['flegmon', 'flegmon', '<ruby>flegm<rt class="ruby-X_X_X">冷静</rt></ruby>on'], ['fronton', '<ruby>fronton<rt class="ruby-M_M_M">[建]ペディメント</rt></ruby>', '<ruby>front<rt class="ruby-X_X_X">正面</rt></ruby>on'], ['galon', '<ruby>galon<rt class="ruby-M_M_M">[服]モール</rt></ruby>', '<ruby>gal<rt class="ruby-M_M_M">[生]胆汁</rt></ruby>on'], ['mason', '<ruby>mason<rt class="ruby-X_X_X">築く</rt></ruby>', '<ruby>mas<rt class="ruby-M_M_M">かたまり</rt></ruby>on'], ['helikon', 'helikon', '<ruby>helik<rt class="ruby-S_S_S">[動]カタツムリ</rt></ruby>on'], ['kanon', '<ruby>kanon<rt class="ruby-L_L_L">[軍]大砲</rt></ruby>', '<ruby>kan<rt class="ruby-M_M_M">[植]アシ</rt></ruby>on'], ['kapon', '<ruby>kapon<rt class="ruby-M_M_M">去勢オンドリ</rt></ruby>', '<ruby>kap<rt class="ruby-X_X_X">頭</rt></ruby>on'], ['kokon', '<ruby>kokon<rt class="ruby-M_M_M">[虫]繭(まゆ)</rt></ruby>', '<ruby>kok<rt class="ruby-M_M_M">ニワトリ</rt></ruby>on'], ['kolon', '<ruby>kolon<rt class="ruby-L_L_L">[建]円柱</rt></ruby>', '<ruby>kol<rt class="ruby-M_M_M">[解]首</rt></ruby>on'], ['komision', '<ruby>komision<rt class="ruby-L_L_L">(調査)委員会</rt></ruby>', '<ruby>komisi<rt class="ruby-M_M_M">(を)委託する</rt></ruby>on'], ['salon', '<ruby>salon<rt class="ruby-L_L_L">サロン</rt></ruby>', '<ruby>sal<rt class="ruby-X_X_X">塩</rt></ruby>on'], ['ponton', '<ruby>ponton<rt class="ruby-L_L_L">[軍]平底舟</rt></ruby>', '<ruby>pont<rt class="ruby-X_X_X">橋</rt></ruby>on'], ['koton', '<ruby>koton<rt class="ruby-X_X_X">綿</rt></ruby>', '<ruby>kot<rt class="ruby-X_X_X">泥</rt></ruby>on'], ['kripton', 'kripton', '<ruby>kript<rt class="ruby-M_M_M">[宗]地下聖堂</rt></ruby>on'], ['kupon', '<ruby>kupon<rt class="ruby-M_M_M">クーポン券</rt></ruby>', '<ruby>kup<rt class="ruby-M_M_M">吸い玉</rt></ruby>on'], ['lakon', 'lakon', '<ruby>lak<rt class="ruby-M_M_M">ラッカー</rt></ruby>on'], ['ludon', '<ruby>lu<rt class="ruby-S_S_S">賃借する</rt></ruby><ruby>don<rt class="ruby-M_M_M">与える</rt></ruby>', '<ruby>lud<rt class="ruby-M_M_M">(を)遊ぶ</rt></ruby>on'], ['melon', '<ruby>melon<rt class="ruby-M_M_M">[果]メロン</rt></ruby>', '<ruby>mel<rt class="ruby-M_M_M">アナグマ</rt></ruby>on'], ['menton', '<ruby>menton<rt class="ruby-L_L_L">[解]下あご</rt></ruby>', '<ruby>ment<rt class="ruby-M_M_M">[植]ハッカ</rt></ruby>on'], ['milion', '<ruby>milion<rt class="ruby-X_X_X">百万</rt></ruby>', '<ruby>mili<rt class="ruby-M_M_M">[植]キビ</rt></ruby>on'], ['milionon', '<ruby>milion<rt class="ruby-X_X_X">百万</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>milion<rt class="ruby-X_X_X">百万</rt></ruby>on'], ['nauxon', '<ruby>naux<rt class="ruby-X_X_X">九</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>naux<rt class="ruby-X_X_X">九</rt></ruby>on'], ['violon', '<ruby>violon<rt class="ruby-M_M_M">[楽]バイオリン</rt></ruby>', '<ruby>viol<rt class="ruby-M_M_M">[植]スミレ</rt></ruby>on'], ['refoj', '<ruby>re<rt class="ruby-M_M_M">再び</rt></ruby><ruby>foj<rt class="ruby-X_X_X">回</rt></ruby>', '<ruby>ref<rt class="ruby-M_M_M">リーフ</rt></ruby>oj'], ['trombon', '<ruby>trombon<rt class="ruby-M_M_M">[楽]トロンボーン</rt></ruby>', '<ruby>tromb<rt class="ruby-M_M_M">[気]たつまき</rt></ruby>on'], ['samo', 'samo', '<ruby>sam<rt class="ruby-M_M_M">同一の</rt></ruby>o'], ['savoj', 'savoj', '<ruby>sav<rt class="ruby-M_M_M">救助する</rt></ruby>oj'], ['senson', '<ruby>sen<rt class="ruby-S_S_S">(~)なしで</rt></ruby><ruby>son<rt class="ruby-M_M_M">音がする</rt></ruby>', '<ruby>sens<rt class="ruby-M_M_M">[生]感覚</rt></ruby>on'], ['sepon', '<ruby>sep<rt class="ruby-X_X_X">七</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>sep<rt class="ruby-X_X_X">七</rt></ruby>on'], ['skadron', 'skadron', '<ruby>skadr<rt class="ruby-M_M_M">[軍]騎兵中隊</rt></ruby>on'], ['stadion', '<ruby>stadion<rt class="ruby-L_L_L">スタジアム</rt></ruby>', '<ruby>stadi<rt class="ruby-X_X_X">段階</rt></ruby>on'], ['tetraon', 'tetraon', '<ruby>tetra<rt class="ruby-S_S_S">エゾライチョウ</rt></ruby>on'], ['timon', '<ruby>timon<rt class="ruby-L_L_L">かじ棒</rt></ruby>', '<ruby>tim<rt class="ruby-M_M_M">恐れる</rt></ruby>on'], ['valon', 'valon', '<ruby>val<rt class="ruby-M_M_M">[地]谷</rt></ruby>on'], ['veto', 'veto', '<ruby>vet<rt class="ruby-M_M_M">賭ける</rt></ruby>o']]
                    # on系以外は、'fero','refoj','samo','savoj','veto'
            if "形容词" in j[1]:
                for k in ["a","aj",'an']:
                    if not i+k in pre_replacements_dict_2:
                        pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]
                    elif j[0]+k != pre_replacements_dict_2[i+k][0]:
                        pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]# 新しく作った方の語根分解を優先する つまり、"an"は形容詞語尾として語根分解する。
                        overlap_6.append([i+k,pre_replacements_dict_2[i+k][0],j[0]+k])
                        unchangeable_after_creation_list.append(i+k)
                    # an系 [['dietan', '<ruby>diet<rt class="ruby-M_M_M">[医]規定食</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>diet<rt class="ruby-M_M_M">[医]規定食</rt></ruby>an'], ['afrikan', '<ruby>afrik<rt class="ruby-S_S_S">[地名]アフリカ</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>afrik<rt class="ruby-S_S_S">[地名]アフリカ</rt></ruby>an'], ['movadan', '<ruby>mov<rt class="ruby-M_M_M">動かす</rt></ruby><ruby>ad<rt class="ruby-S_S_S">継続行為</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>mov<rt class="ruby-M_M_M">動かす</rt></ruby><ruby>ad<rt class="ruby-S_S_S">継続行為</rt></ruby>an'], ['akcian', '<ruby>akci<rt class="ruby-M_M_M">[商]株式</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>akci<rt class="ruby-M_M_M">[商]株式</rt></ruby>an'], ['montaran', '<ruby>mont<rt class="ruby-X_X_X">山</rt></ruby><ruby>ar<rt class="ruby-M_M_M">集団</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>mont<rt class="ruby-X_X_X">山</rt></ruby><ruby>ar<rt class="ruby-M_M_M">集団</rt></ruby>an'], ['amerikan', '<ruby>amerik<rt class="ruby-M_M_M">[地名]アメリカ</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>amerik<rt class="ruby-M_M_M">[地名]アメリカ</rt></ruby>an'], ['regnan', '<ruby>regn<rt class="ruby-M_M_M">[法]国家</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>regn<rt class="ruby-M_M_M">[法]国家</rt></ruby>an'], ['dezertan', '<ruby>dezert<rt class="ruby-X_X_X">砂漠</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>dezert<rt class="ruby-X_X_X">砂漠</rt></ruby>an'], ['asocian', '<ruby>asoci<rt class="ruby-X_X_X">協会</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>asoci<rt class="ruby-X_X_X">協会</rt></ruby>an'], ['insulan', '<ruby>insul<rt class="ruby-X_X_X">島</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>insul<rt class="ruby-X_X_X">島</rt></ruby>an'], ['azian', '<ruby>azi<rt class="ruby-M_M_M">アジア</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>azi<rt class="ruby-M_M_M">アジア</rt></ruby>an'], ['sxtatan', '<ruby>sxtat<rt class="ruby-X_X_X">国家</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>sxtat<rt class="ruby-X_X_X">国家</rt></ruby>an'], ['doman', '<ruby>dom<rt class="ruby-X_X_X">家</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>dom<rt class="ruby-X_X_X">家</rt></ruby>an'], ['montan', '<ruby>mont<rt class="ruby-X_X_X">山</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>mont<rt class="ruby-X_X_X">山</rt></ruby>an'], ['familian', '<ruby>famili<rt class="ruby-X_X_X">家族</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>famili<rt class="ruby-X_X_X">家族</rt></ruby>an'], ['urban', '<ruby>urb<rt class="ruby-X_X_X">市</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>urb<rt class="ruby-X_X_X">市</rt></ruby>an'], ['inka', 'inka', '<ruby>ink<rt class="ruby-M_M_M">インク</rt></ruby>a'], ['popolan', '<ruby>popol<rt class="ruby-X_X_X">人民</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>popol<rt class="ruby-X_X_X">人民</rt></ruby>an'], ['dekan', '<ruby>dekan<rt class="ruby-L_L_L">学部長</rt></ruby>', '<ruby>dek<rt class="ruby-X_X_X">十</rt></ruby>an'], ['partian', '<ruby>parti<rt class="ruby-L_L_L">[政]党派</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>parti<rt class="ruby-L_L_L">[政]党派</rt></ruby>an'], ['lokan', '<ruby>lok<rt class="ruby-L_L_L">場所</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>lok<rt class="ruby-L_L_L">場所</rt></ruby>an'], ['sxipan', '<ruby>sxip<rt class="ruby-X_X_X">船</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>sxip<rt class="ruby-X_X_X">船</rt></ruby>an'], ['eklezian', '<ruby>eklezi<rt class="ruby-L_L_L">[宗]教会</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>eklezi<rt class="ruby-L_L_L">[宗]教会</rt></ruby>an'], ['landan', '<ruby>land<rt class="ruby-X_X_X">国</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>land<rt class="ruby-X_X_X">国</rt></ruby>an'], ['orientan', '<ruby>orient<rt class="ruby-M_M_M">方位定める;東</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>orient<rt class="ruby-M_M_M">方位定める;東</rt></ruby>an'], ['lernejan', '<ruby>lern<rt class="ruby-S_S_S">(を)学習する</rt></ruby><ruby>ej<rt class="ruby-M_M_M">場所</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>lern<rt class="ruby-S_S_S">(を)学習する</rt></ruby><ruby>ej<rt class="ruby-M_M_M">場所</rt></ruby>an'], ['enlandan', '<ruby>en<rt class="ruby-M_M_M">中で</rt></ruby><ruby>land<rt class="ruby-X_X_X">国</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>en<rt class="ruby-M_M_M">中で</rt></ruby><ruby>land<rt class="ruby-X_X_X">国</rt></ruby>an'], ['kalkan', '<ruby>kalkan<rt class="ruby-X_X_X">[解]踵</rt></ruby>', '<ruby>kalk<rt class="ruby-M_M_M">[化]石灰</rt></ruby>an'], ['estraran', '<ruby>estr<rt class="ruby-M_M_M">[接尾辞]長</rt></ruby><ruby>ar<rt class="ruby-M_M_M">集団</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>estr<rt class="ruby-M_M_M">[接尾辞]長</rt></ruby><ruby>ar<rt class="ruby-M_M_M">集団</rt></ruby>an'], ['etnan', '<ruby>etn<rt class="ruby-L_L_L">民族</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>etn<rt class="ruby-L_L_L">民族</rt></ruby>an'], ['euxropan', '<ruby>euxrop<rt class="ruby-L_L_L">ヨーロッパ</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>euxrop<rt class="ruby-L_L_L">ヨーロッパ</rt></ruby>an'], ['fazan', '<ruby>fazan<rt class="ruby-L_L_L">[鳥]キジ</rt></ruby>', '<ruby>faz<rt class="ruby-M_M_M">[理]位相</rt></ruby>an'], ['polican', '<ruby>polic<rt class="ruby-X_X_X">警察</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>polic<rt class="ruby-X_X_X">警察</rt></ruby>an'], ['socian', '<ruby>soci<rt class="ruby-X_X_X">社会</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>soci<rt class="ruby-X_X_X">社会</rt></ruby>an'], ['societan', '<ruby>societ<rt class="ruby-X_X_X">会</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>societ<rt class="ruby-X_X_X">会</rt></ruby>an'], ['grupan', '<ruby>grup<rt class="ruby-M_M_M">グループ</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>grup<rt class="ruby-M_M_M">グループ</rt></ruby>an'], ['havaj', 'havaj', '<ruby>hav<rt class="ruby-S_S_S">持っている</rt></ruby>aj'], ['ligan', '<ruby>lig<rt class="ruby-S_S_S">結ぶ;連盟</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>lig<rt class="ruby-S_S_S">結ぶ;連盟</rt></ruby>an'], ['nacian', '<ruby>naci<rt class="ruby-X_X_X">国民</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>naci<rt class="ruby-X_X_X">国民</rt></ruby>an'], ['koran', '<ruby>koran<rt class="ruby-M_M_M">[宗]コーラン</rt></ruby>', '<ruby>kor<rt class="ruby-X_X_X">心</rt></ruby>an'], ['religian', '<ruby>religi<rt class="ruby-X_X_X">宗教</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>religi<rt class="ruby-X_X_X">宗教</rt></ruby>an'], ['kuban', '<ruby>kub<rt class="ruby-M_M_M">立方体</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>kub<rt class="ruby-M_M_M">立方体</rt></ruby>an'], ['lama', '<ruby>lama<rt class="ruby-M_M_M">[宗]ラマ僧</rt></ruby>', '<ruby>lam<rt class="ruby-M_M_M">びっこの</rt></ruby>a'], ['majoran', '<ruby>major<rt class="ruby-M_M_M">[軍]陸軍少佐</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>major<rt class="ruby-M_M_M">[軍]陸軍少佐</rt></ruby>an'], ['malaj', 'malaj', '<ruby>mal<rt class="ruby-M_M_M">正反対</rt></ruby>aj'], ['marian', 'marian', '<ruby>mari<rt class="ruby-L_L_L">マリア</rt></ruby>an'], ['nordan', '<ruby>nord<rt class="ruby-X_X_X">北</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>nord<rt class="ruby-X_X_X">北</rt></ruby>an'], ['paran', 'paran', '<ruby>par<rt class="ruby-L_L_L">一対</rt></ruby>an'], ['parizan', '<ruby>pariz<rt class="ruby-M_M_M">[地名]パリ</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>pariz<rt class="ruby-M_M_M">[地名]パリ</rt></ruby>an'], ['parokan', '<ruby>parok<rt class="ruby-L_L_L">[宗]教区</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>parok<rt class="ruby-L_L_L">[宗]教区</rt></ruby>an'], ['podian', '<ruby>podi<rt class="ruby-L_L_L">ひな壇</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>podi<rt class="ruby-L_L_L">ひな壇</rt></ruby>an'], ['rusian', '<ruby>rus<rt class="ruby-M_M_M">ロシア人</rt></ruby>i<ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>rus<rt class="ruby-M_M_M">ロシア人</rt></ruby>ian'], ['satan', '<ruby>satan<rt class="ruby-M_M_M">[宗]サタン</rt></ruby>', '<ruby>sat<rt class="ruby-M_M_M">満腹した</rt></ruby>an'], ['sektan', '<ruby>sekt<rt class="ruby-M_M_M">[宗]宗派</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>sekt<rt class="ruby-M_M_M">[宗]宗派</rt></ruby>an'], ['senatan', '<ruby>senat<rt class="ruby-M_M_M">[政]参議院</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>senat<rt class="ruby-M_M_M">[政]参議院</rt></ruby>an'], ['skisman', '<ruby>skism<rt class="ruby-M_M_M">(団体の)分裂</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>skism<rt class="ruby-M_M_M">(団体の)分裂</rt></ruby>an'], ['sudan', 'sudan', '<ruby>sud<rt class="ruby-X_X_X">南</rt></ruby>an'], ['utopian', '<ruby>utopi<rt class="ruby-M_M_M">ユートピア</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>utopi<rt class="ruby-M_M_M">ユートピア</rt></ruby>an'], ['vilagxan', '<ruby>vilagx<rt class="ruby-X_X_X">村</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>vilagx<rt class="ruby-X_X_X">村</rt></ruby>an']]
                    # an系以外は'inka','malaj','havaj','lama'　　'marian'については、'マリアan'で行く。
            if "副词" in j[1]:
                for k in ["e"]:
                    if not i+k in pre_replacements_dict_2:
                        pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]
                    elif j[0]+k != pre_replacements_dict_2[i+k][0]:
                        pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]# 新しく作った方の語根分解を優先する
                        overlap_7.append([i+k,pre_replacements_dict_2[i+k][0],j[0]+k])
                        unchangeable_after_creation_list.append(i+k)
                    # [['alte', '<ruby>alte<rt class="ruby-M_M_M">タチアオイ</rt></ruby>', '<ruby>alt<rt class="ruby-L_L_L">高い</rt></ruby>e'], ['apoge', '<ruby>apoge<rt class="ruby-M_M_M">[天]遠地点</rt></ruby>', '<ruby>apog<rt class="ruby-M_M_M">(を)支える</rt></ruby>e'], ['kaze', '<ruby>kaze<rt class="ruby-M_M_M">[化]凝乳</rt></ruby>', '<ruby>kaz<rt class="ruby-M_M_M">[文]格</rt></ruby>e'], ['pere', '<ruby>pere<rt class="ruby-M_M_M">破滅する</rt></ruby>', '<ruby>per<rt class="ruby-M_M_M">よって</rt></ruby>e'], ['kore', 'kore', '<ruby>kor<rt class="ruby-X_X_X">心</rt></ruby>e'], ['male', 'male', '<ruby>mal<rt class="ruby-M_M_M">正反対</rt></ruby>e'], ['sole', '<ruby>sole<rt class="ruby-M_M_M">シタビラメ</rt></ruby>', '<ruby>sol<rt class="ruby-M_M_M">唯一の</rt></ruby>e']]
            if "动词" in j[1]:
                for k1,k2 in verb_suffix_2l_2.items():
                    if not i+k1 in pre_replacements_dict_2:
                        pre_replacements_dict_3[i+k1]=[j[0]+k2,j[2]+len(k1)*10000-3000]
                    elif j[0]+k2 != pre_replacements_dict_2[i+k1][0]:
                        pre_replacements_dict_3[i+k1]=[j[0]+k2,j[2]+len(k1)*10000-3000]# 新しく作った方の語根分解を優先する
                        overlap_8.append([i+k1,pre_replacements_dict_2[i+k1][0],j[0]+k2])
                        unchangeable_after_creation_list.append(i+k1)
                    # [['regulus', 'regulus', '<ruby>regul<rt class="ruby-X_X_X">規則</rt></ruby><ruby>us<rt class="ruby-S_S_S">条件法</rt></ruby>'], ['akirant', 'akirant', '<ruby>akir<rt class="ruby-S_S_S">(を)獲得する</rt></ruby><ruby>ant<rt class="ruby-S_S_S">能動;継続</rt></ruby>'], ['radius', 'radius', '<ruby>radi<rt class="ruby-L_L_L">[理]線</rt></ruby><ruby>us<rt class="ruby-S_S_S">条件法</rt></ruby>'], ['premis', '<ruby>premis<rt class="ruby-X_X_X">前提</rt></ruby>', '<ruby>prem<rt class="ruby-M_M_M">(を)押える</rt></ruby><ruby>is<rt class="ruby-S_S_S">過去形</rt></ruby>'], ['sonat', '<ruby>sonat<rt class="ruby-M_M_M">[楽]ソナタ</rt></ruby>', '<ruby>son<rt class="ruby-M_M_M">音がする</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['format', '<ruby>format<rt class="ruby-X_X_X">[印]判</rt></ruby>', '<ruby>form<rt class="ruby-X_X_X">形</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['markot', '<ruby>markot<rt class="ruby-L_L_L">[園]取木</rt></ruby>', '<ruby>mark<rt class="ruby-L_L_L">しるし</rt></ruby><ruby>ot<rt class="ruby-S_S_S">受動将然</rt></ruby>'], ['nomad', '<ruby>nomad<rt class="ruby-L_L_L">遊牧民</rt></ruby>', '<ruby>nom<rt class="ruby-L_L_L">名前</rt></ruby><ruby>ad<rt class="ruby-S_S_S">継続行為</rt></ruby>'], ['kantat', '<ruby>kantat<rt class="ruby-M_M_M">[楽]カンタータ</rt></ruby>', '<ruby>kant<rt class="ruby-M_M_M">(を)歌う</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['kolorad', 'kolorad', '<ruby>kolor<rt class="ruby-X_X_X">色</rt></ruby><ruby>ad<rt class="ruby-S_S_S">継続行為</rt></ruby>'], ['diplomat', '<ruby>diplomat<rt class="ruby-X_X_X">外交官</rt></ruby>', '<ruby>diplom<rt class="ruby-X_X_X">免状</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['diskont', '<ruby>diskont<rt class="ruby-M_M_M">[商]手形割引する</rt></ruby>', '<ruby>disk<rt class="ruby-X_X_X">円盤</rt></ruby><ruby>ont<rt class="ruby-S_S_S">能動;将然</rt></ruby>'], ['endos', 'endos', '<ruby>end<rt class="ruby-L_L_L">必要</rt></ruby><ruby>os<rt class="ruby-S_S_S">未来形</rt></ruby>'], ['esperant', '<ruby>esperant<rt class="ruby-L_L_L">エスペラント</rt></ruby>', '<ruby>esper<rt class="ruby-M_M_M">(を)希望する</rt></ruby><ruby>ant<rt class="ruby-S_S_S">能動;継続</rt></ruby>'], ['forkant', '<ruby>for<rt class="ruby-M_M_M">離れて</rt></ruby><ruby>kant<rt class="ruby-M_M_M">(を)歌う</rt></ruby>', '<ruby>fork<rt class="ruby-S_S_S">[料]フォーク</rt></ruby><ruby>ant<rt class="ruby-S_S_S">能動;継続</rt></ruby>'], ['gravit', 'gravit', '<ruby>grav<rt class="ruby-L_L_L">重要な</rt></ruby><ruby>it<rt class="ruby-S_S_S">受動完了</rt></ruby>'], ['konus', '<ruby>konus<rt class="ruby-L_L_L">[数]円錐</rt></ruby>', '<ruby>kon<rt class="ruby-S_S_S">知っている</rt></ruby><ruby>us<rt class="ruby-S_S_S">条件法</rt></ruby>'], ['salat', '<ruby>salat<rt class="ruby-M_M_M">[料]サラダ</rt></ruby>', '<ruby>sal<rt class="ruby-X_X_X">塩</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['legat', '<ruby>legat<rt class="ruby-M_M_M">[宗]教皇特使</rt></ruby>', '<ruby>leg<rt class="ruby-M_M_M">(を)読む</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['lekant', '<ruby>lekant<rt class="ruby-M_M_M">[植]マーガレット</rt></ruby>', '<ruby>lek<rt class="ruby-M_M_M">なめる</rt></ruby><ruby>ant<rt class="ruby-S_S_S">能動;継続</rt></ruby>'], ['lotus', '<ruby>lotus<rt class="ruby-L_L_L">[植]ハス</rt></ruby>', '<ruby>lot<rt class="ruby-L_L_L">くじ</rt></ruby><ruby>us<rt class="ruby-S_S_S">条件法</rt></ruby>'], ['malvolont', '<ruby>mal<rt class="ruby-M_M_M">正反対</rt></ruby><ruby>volont<rt class="ruby-L_L_L">自ら進んで</rt></ruby>', '<ruby>mal<rt class="ruby-M_M_M">正反対</rt></ruby><ruby>vol<rt class="ruby-S_S_S">意志がある</rt></ruby><ruby>ont<rt class="ruby-S_S_S">能動;将然</rt></ruby>'], ['mankis', '<ruby>man<rt class="ruby-X_X_X">手</rt></ruby><ruby>kis<rt class="ruby-M_M_M">キスする</rt></ruby>', '<ruby>mank<rt class="ruby-M_M_M">欠けている</rt></ruby><ruby>is<rt class="ruby-S_S_S">過去形</rt></ruby>'], ['minus', '<ruby>minus<rt class="ruby-L_L_L">マイナス</rt></ruby>', '<ruby>min<rt class="ruby-L_L_L">鉱山</rt></ruby><ruby>us<rt class="ruby-S_S_S">条件法</rt></ruby>'], ['patos', '<ruby>patos<rt class="ruby-M_M_M">[芸]パトス</rt></ruby>', '<ruby>pat<rt class="ruby-S_S_S">フライパン</rt></ruby><ruby>os<rt class="ruby-S_S_S">未来形</rt></ruby>'], ['predikat', '<ruby>predikat<rt class="ruby-X_X_X">[文]述部</rt></ruby>', '<ruby>predik<rt class="ruby-M_M_M">(を)説教する</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['rabat', '<ruby>rabat<rt class="ruby-L_L_L">[商]割引</rt></ruby>', '<ruby>rab<rt class="ruby-M_M_M">強奪する</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['rabot', '<ruby>rabot<rt class="ruby-S_S_S">かんなをかける</rt></ruby>', '<ruby>rab<rt class="ruby-M_M_M">強奪する</rt></ruby><ruby>ot<rt class="ruby-S_S_S">受動将然</rt></ruby>'], ['remont', 'remont', '<ruby>rem<rt class="ruby-L_L_L">漕ぐ</rt></ruby><ruby>ont<rt class="ruby-S_S_S">能動;将然</rt></ruby>'], ['satirus', 'satirus', '<ruby>satir<rt class="ruby-M_M_M">諷刺(詩;文)</rt></ruby><ruby>us<rt class="ruby-S_S_S">条件法</rt></ruby>'], ['sendat', '<ruby>sen<rt class="ruby-S_S_S">(~)なしで</rt></ruby><ruby>dat<rt class="ruby-L_L_L">日付</rt></ruby>', '<ruby>send<rt class="ruby-M_M_M">(を)送る</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['sendot', '<ruby>sen<rt class="ruby-S_S_S">(~)なしで</rt></ruby><ruby>dot<rt class="ruby-M_M_M">持参金</rt></ruby>', '<ruby>send<rt class="ruby-M_M_M">(を)送る</rt></ruby><ruby>ot<rt class="ruby-S_S_S">受動将然</rt></ruby>'], ['spirit', '<ruby>spirit<rt class="ruby-X_X_X">精神</rt></ruby>', '<ruby>spir<rt class="ruby-M_M_M">呼吸する</rt></ruby><ruby>it<rt class="ruby-S_S_S">受動完了</rt></ruby>'], ['spirant', 'spirant', '<ruby>spir<rt class="ruby-M_M_M">呼吸する</rt></ruby><ruby>ant<rt class="ruby-S_S_S">能動;継続</rt></ruby>'], ['taksus', '<ruby>taksus<rt class="ruby-L_L_L">[植]イチイ</rt></ruby>', '<ruby>taks<rt class="ruby-S_S_S">(を)評価する</rt></ruby><ruby>us<rt class="ruby-S_S_S">条件法</rt></ruby>'], ['tenis', 'tenis', '<ruby>ten<rt class="ruby-M_M_M">支え持つ</rt></ruby><ruby>is<rt class="ruby-S_S_S">過去形</rt></ruby>'], ['traktat', '<ruby>traktat<rt class="ruby-X_X_X">[政]条約</rt></ruby>', '<ruby>trakt<rt class="ruby-M_M_M">(を)取り扱う</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['trikot', '<ruby>trikot<rt class="ruby-M_M_M">[織]トリコット</rt></ruby>', '<ruby>trik<rt class="ruby-S_S_S">編み物をする</rt></ruby><ruby>ot<rt class="ruby-S_S_S">受動将然</rt></ruby>'], ['trilit', '<ruby>tri<rt class="ruby-X_X_X">三</rt></ruby><ruby>lit<rt class="ruby-M_M_M">ベッド</rt></ruby>', '<ruby>tril<rt class="ruby-M_M_M">[楽]トリル</rt></ruby><ruby>it<rt class="ruby-S_S_S">受動完了</rt></ruby>'], ['vizit', '<ruby>vizit<rt class="ruby-M_M_M">(を)訪問する</rt></ruby>', '<ruby>viz<rt class="ruby-L_L_L">ビザ</rt></ruby><ruby>it<rt class="ruby-S_S_S">受動完了</rt></ruby>'], ['volont', '<ruby>volont<rt class="ruby-L_L_L">自ら進んで</rt></ruby>', '<ruby>vol<rt class="ruby-S_S_S">意志がある</rt></ruby><ruby>ont<rt class="ruby-S_S_S">能動;将然</rt></ruby>']]
                for k in ["u ","i ","u","i"]:# 动词の"u","i"単体の接尾辞は後ろが空白と決まっているので、2文字分増やすことができる。
                    if not i+k in pre_replacements_dict_2:
                        pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]
                    elif j[0]+k != pre_replacements_dict_2[i+k][0]:
                        pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]# 新しく作った方の語根分解を優先する
                        overlap_9.append([i+k,pre_replacements_dict_2[i+k][0],j[0]+k])
                        unchangeable_after_creation_list.append(i+k)
                    # [['agxi', '<ruby>agxi<rt class="ruby-L_L_L">打ち歩</rt></ruby>', '<ruby>agx<rt class="ruby-L_L_L">年齢</rt></ruby>i'], ['premi', '<ruby>premi<rt class="ruby-X_X_X">賞品</rt></ruby>', '<ruby>prem<rt class="ruby-M_M_M">(を)押える</rt></ruby>i'], ['bari', 'bari', '<ruby>bar<rt class="ruby-L_L_L">障害</rt></ruby>i'], ['tempi', '<ruby>tempi<rt class="ruby-L_L_L">こめかみ</rt></ruby>', '<ruby>temp<rt class="ruby-X_X_X">時間</rt></ruby>i'], ['noktu', '<ruby>noktu<rt class="ruby-S_S_S">[鳥]コフクロウ</rt></ruby>', '<ruby>nokt<rt class="ruby-X_X_X">夜</rt></ruby>u'], ['vakcini', 'vakcini', '<ruby>vakcin<rt class="ruby-M_M_M">[薬]ワクチン</rt></ruby>i'], ['procesi', '<ruby>procesi<rt class="ruby-X_X_X">[宗]行列</rt></ruby>', '<ruby>proces<rt class="ruby-L_L_L">[法]訴訟</rt></ruby>i'], ['statu', '<ruby>statu<rt class="ruby-X_X_X">立像</rt></ruby>', '<ruby>stat<rt class="ruby-X_X_X">状態</rt></ruby>u'], ['devi', 'devi', '<ruby>dev<rt class="ruby-L_L_L">must</rt></ruby>i'], ['feri', '<ruby>feri<rt class="ruby-X_X_X">休日</rt></ruby>', '<ruby>fer<rt class="ruby-X_X_X">鉄</rt></ruby>i'], ['fleksi', '<ruby>fleksi<rt class="ruby-M_M_M">[文]語尾変化</rt></ruby>', '<ruby>fleks<rt class="ruby-M_M_M">(を)曲げる</rt></ruby>i'], ['pensi', '<ruby>pensi<rt class="ruby-X_X_X">年金</rt></ruby>', '<ruby>pens<rt class="ruby-X_X_X">思う</rt></ruby>i'], ['jesu', '<ruby>jesu<rt class="ruby-M_M_M">[宗]イエス</rt></ruby>', '<ruby>jes<rt class="ruby-L_L_L">はい</rt></ruby>u'], ['jxaluzi', 'jxaluzi', '<ruby>jxaluz<rt class="ruby-L_L_L">嫉妬深い</rt></ruby>i'], ['konfesi', 'konfesi', '<ruby>konfes<rt class="ruby-M_M_M">(を)告白する</rt></ruby>i'], ['konsili', 'konsili', '<ruby>konsil<rt class="ruby-M_M_M">(を)助言する</rt></ruby>i'], ['legi', '<ruby>legi<rt class="ruby-M_M_M">[史]軍団</rt></ruby>', '<ruby>leg<rt class="ruby-M_M_M">(を)読む</rt></ruby>i'], ['licenci', 'licenci', '<ruby>licenc<rt class="ruby-L_L_L">[商]認可</rt></ruby>i'], ['logxi', '<ruby>logxi<rt class="ruby-L_L_L">[劇]桟敷</rt></ruby>', '<ruby>logx<rt class="ruby-M_M_M">(に)住む</rt></ruby>i'], ['meti', '<ruby>meti<rt class="ruby-L_L_L">手仕事</rt></ruby>', '<ruby>met<rt class="ruby-M_M_M">(を)置く</rt></ruby>i'], ['pasi', '<ruby>pasi<rt class="ruby-X_X_X">情熱</rt></ruby>', '<ruby>pas<rt class="ruby-M_M_M">通過する</rt></ruby>i'], ['revu', '<ruby>revu<rt class="ruby-M_M_M">専門雑誌</rt></ruby>', '<ruby>rev<rt class="ruby-M_M_M">空想する</rt></ruby>u'], ['rabi', '<ruby>rabi<rt class="ruby-M_M_M">[病]狂犬病</rt></ruby>', '<ruby>rab<rt class="ruby-M_M_M">強奪する</rt></ruby>i'], ['religi', '<ruby>religi<rt class="ruby-X_X_X">宗教</rt></ruby>', '<ruby>re<rt class="ruby-M_M_M">再び</rt></ruby><ruby>lig<rt class="ruby-S_S_S">結ぶ;連盟</rt></ruby>i'], ['sagu', '<ruby>sagu<rt class="ruby-M_M_M">[料]サゴ粉</rt></ruby>', '<ruby>sag<rt class="ruby-X_X_X">矢</rt></ruby>u'], ['sekci', '<ruby>sekci<rt class="ruby-X_X_X">部</rt></ruby>', '<ruby>sekc<rt class="ruby-S_S_S">[医]切断する</rt></ruby>i'], ['sendi', '<ruby>sen<rt class="ruby-S_S_S">(~)なしで</rt></ruby><ruby>di<rt class="ruby-X_X_X">神</rt></ruby>', '<ruby>send<rt class="ruby-M_M_M">(を)送る</rt></ruby>i'], ['teni', '<ruby>teni<rt class="ruby-M_M_M">サナダムシ</rt></ruby>', '<ruby>ten<rt class="ruby-M_M_M">支え持つ</rt></ruby>i'], ['vaku', 'vaku', '<ruby>vak<rt class="ruby-S_S_S">あいている</rt></ruby>u'], ['vizi', '<ruby>vizi<rt class="ruby-X_X_X">幻影</rt></ruby>', '<ruby>viz<rt class="ruby-L_L_L">ビザ</rt></ruby>i']]
            count_3+=1
        elif len(i)>=3 and len(i)<=6:# 3文字から6文字の語根で置換しないもの　　結局2文字の語根で置換しないものについては、完全に除外している。
            if "名词" in j[1]:# 名词については形容词、副词と違い、置換しないものにもoをつける。
                for k in ["o"]:
                    if not i+k in pre_replacements_dict_2:
                        pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-5000]# 実質3000# 存でないものは優先順位を大きく下げる→普通の品詞接尾辞が既存でないという言い方はおかしい気がしてきた。(20240612)
                    elif j[0]+k != pre_replacements_dict_2[i+k][0]:
                        overlap_10.append([i+k,pre_replacements_dict_2[i+k][0],j[0]+k])# 該当なし
            if "形容词" in j[1]:
                for k in ["a"]:
                    if not i+k in pre_replacements_dict_2:
                        pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-5000]
                    elif j[0]+k != pre_replacements_dict_2[i+k][0]:
                        overlap_11.append([i+k,pre_replacements_dict_2[i+k][0],j[0]+k])# 該当なし
            if "副词" in j[1]:
                for k in ["e"]:
                    if not i+k in pre_replacements_dict_2:
                        pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-5000]
                    elif j[0]+k != pre_replacements_dict_2[i+k][0]:
                        overlap_12.append([i+k,pre_replacements_dict_2[i+k][0],j[0]+k])# 該当なし
            count_4+=1


# In[52]:


# circumflex= {'ĉ','ĝ','ĥ','ĵ','ŝ','ŭ','Ĉ','Ĝ','Ĥ','Ĵ','Ŝ','Ŭ'}
check_list=[' feo',' fea',
    'buroo', 'haloo', 'taŭro', 'unesko','alo','duon','okon','sia','eman','lian','pian','agat','agit','amas','iris','irit','alte','apoge','kaze','regulus','akirant','radius','aĝi','premi','bari','marian','gravit','predikat','baria','tempiost','arĝentan','ĵaluzi']
for i in check_list:
    print(pre_replacements_dict_3[i])


# In[53]:


# X形式での処理から字上符形式での処理へ変更した際(202501)に生じた差異を割り出す。
from pprint import pprint

# --- 例として、2つの Python 出力を仮に用意します ---
# # ===== 1つ目の Python 出力から得られた値 =====
# overlap_1_a = [['buro', 'buro', 'buro'], ['haloo', 'haloo', 'haloo'], ['taŭro', 'taŭro', 'taŭro'], ['unesko', 'unesko', 'unesko']]
# overlap_2_a = [['alo', '<ruby>alo<rt class="ruby-S_S_S">アロエ</rt></ruby>', '<ruby>al<rt class="ruby-XS_S_S">~の方へ</rt></ruby>o'], ['duon', '<ruby>du<rt class="ruby-XXL_L_L">二</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>du<rt class="ruby-XXL_L_L">二</rt></ruby>on'], ['okon', '<ruby>ok<rt class="ruby-XXL_L_L">八</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>ok<rt class="ruby-XXL_L_L">八</rt></ruby>on']]
# overlap_2_2_a = [['sia', 'sia', '<ruby>si<rt class="ruby-S_S_S">自分</rt></ruby>a'], ['eman', 'eman', '<ruby>em<rt class="ruby-XL_L_L">傾向</rt></ruby>an'], ['lian', '<ruby>lian<rt class="ruby-XS_S_S">[植]つる植物</rt></ruby>', '<ruby>li<rt class="ruby-M_M_M">彼</rt></ruby>an'], ['pian', '<ruby>pian<rt class="ruby-S_S_S">[楽]ピアノ</rt></ruby>', '<ruby>pi<rt class="ruby-XS_S_S">信心深い</rt></ruby>an']]
# overlap_3_a = [['agat', '<ruby>agat<rt class="ruby-S_S_S">[鉱]メノウ</rt></ruby>', '<ruby>ag<rt class="ruby-XS_S_S">行動する</rt></ruby><ruby>at<rt class="ruby-XS_S_S">受動継続</rt></ruby>'], ['agit', '<ruby>agit<rt class="ruby-XS_S_S">(を)扇動する</rt></ruby>', '<ruby>ag<rt class="ruby-XS_S_S">行動する</rt></ruby><ruby>it<rt class="ruby-XS_S_S">受動完了</rt></ruby>'], ['amas', '<ruby>amas<rt class="ruby-L_L_L">集積;大衆</rt></ruby>', '<ruby>am<rt class="ruby-M_M_M">愛する</rt></ruby><ruby>as<rt class="ruby-XS_S_S">現在形</rt></ruby>'], ['iris', '<ruby>iris<rt class="ruby-XS_S_S">[解]虹彩</rt></ruby>', '<ruby>ir<rt class="ruby-XS_S_S">行く</rt></ruby><ruby>is<rt class="ruby-XS_S_S">過去形</rt></ruby>'], ['irit', 'irit', '<ruby>ir<rt class="ruby-XS_S_S">行く</rt></ruby><ruby>it<rt class="ruby-XS_S_S">受動完了</rt></ruby>']]
# overlap_4_a = [['aĝi', '<ruby>aĝi<rt class="ruby-S_S_S">打ち歩</rt></ruby>', '<ruby>aĝ<rt class="ruby-M_M_M">年齢</rt></ruby>i']]
# overlap_5_a = [['nombron', '<ruby>nombr<rt class="ruby-XXL_L_L">数</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>nombr<rt class="ruby-XXL_L_L">数</rt></ruby>on'], ['patron', '<ruby>patron<rt class="ruby-XXL_L_L">後援者</rt></ruby>', '<ruby>patr<rt class="ruby-XXL_L_L">父</rt></ruby>on'], ['karbon', '<ruby>karbon<rt class="ruby-XXL_L_L">[化]炭素</rt></ruby>', '<ruby>karb<rt class="ruby-XXL_L_L">炭</rt></ruby>on'], ['ciklon', '<ruby>ciklon<rt class="ruby-XXL_L_L">低気圧</rt></ruby>', '<ruby>cikl<rt class="ruby-XXL_L_L">周期</rt></ruby>on'], ['aldon', '<ruby>al<rt class="ruby-XS_S_S">~の方へ</rt></ruby><ruby>don<rt class="ruby-M_M_M">与える</rt></ruby>', '<ruby>ald<rt class="ruby-S_S_S">アルト</rt></ruby>on'], ['balon', '<ruby>balon<rt class="ruby-XXL_L_L">気球</rt></ruby>', '<ruby>bal<rt class="ruby-S_S_S">舞踏会</rt></ruby>on'], ['baron', '<ruby>baron<rt class="ruby-XXL_L_L">男爵</rt></ruby>', '<ruby>bar<rt class="ruby-XL_L_L">障害</rt></ruby>on'], ['baston', '<ruby>baston<rt class="ruby-XXL_L_L">棒</rt></ruby>', '<ruby>bast<rt class="ruby-S_S_S">[植]じん皮</rt></ruby>on'], ['magneton', '<ruby>magnet<rt class="ruby-XXL_L_L">[理]磁石</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>magnet<rt class="ruby-XXL_L_L">[理]磁石</rt></ruby>on'], ['beton', 'beton', '<ruby>bet<rt class="ruby-S_S_S">ビート</rt></ruby>on'], ['bombon', '<ruby>bombon<rt class="ruby-XL_L_L">キャンデー</rt></ruby>', '<ruby>bomb<rt class="ruby-XXL_L_L">爆弾</rt></ruby>on'], ['breton', 'breton', '<ruby>bret<rt class="ruby-XXL_L_L">棚</rt></ruby>on'], ['burĝon', '<ruby>burĝon<rt class="ruby-XXL_L_L">芽</rt></ruby>', '<ruby>burĝ<rt class="ruby-S_S_S">ブルジョワ</rt></ruby>on'], ['centon', '<ruby>cent<rt class="ruby-XXL_L_L">百</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>cent<rt class="ruby-XXL_L_L">百</rt></ruby>on'], ['milon', '<ruby>mil<rt class="ruby-XXL_L_L">千</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>mil<rt class="ruby-XXL_L_L">千</rt></ruby>on'], ['kanton', '<ruby>kanton<rt class="ruby-S_S_S">(フランスの)郡</rt></ruby>', '<ruby>kant<rt class="ruby-M_M_M">(を)歌う</rt></ruby>on'], ['citron', '<ruby>citron<rt class="ruby-S_S_S">[果]シトロン</rt></ruby>', '<ruby>citr<rt class="ruby-XS_S_S">[楽]チター</rt></ruby>on'], ['platon', 'platon', '<ruby>plat<rt class="ruby-M_M_M">平たい</rt></ruby>on'], ['dekon', '<ruby>dek<rt class="ruby-XXL_L_L">十</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>dek<rt class="ruby-XXL_L_L">十</rt></ruby>on'], ['kvaron', '<ruby>kvar<rt class="ruby-XXL_L_L">四</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>kvar<rt class="ruby-XXL_L_L">四</rt></ruby>on'], ['kvinon', '<ruby>kvin<rt class="ruby-XXL_L_L">五</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>kvin<rt class="ruby-XXL_L_L">五</rt></ruby>on'], ['seson', '<ruby>ses<rt class="ruby-XXL_L_L">六</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>ses<rt class="ruby-XXL_L_L">六</rt></ruby>on'], ['trion', '<ruby>tri<rt class="ruby-XXL_L_L">三</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>tri<rt class="ruby-XXL_L_L">三</rt></ruby>on'], ['karton', '<ruby>karton<rt class="ruby-XXL_L_L">厚紙</rt></ruby>', '<ruby>kart<rt class="ruby-M_M_M">カード</rt></ruby>on'], ['foton', '<ruby>fot<rt class="ruby-XS_S_S">写真を撮る</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>fot<rt class="ruby-XS_S_S">写真を撮る</rt></ruby>on'], ['peron', '<ruby>peron<rt class="ruby-XXL_L_L">階段</rt></ruby>', '<ruby>per<rt class="ruby-M_M_M">よって</rt></ruby>on'], ['elektron', '<ruby>elektr<rt class="ruby-XXL_L_L">電気</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>elektr<rt class="ruby-XXL_L_L">電気</rt></ruby>on'], ['drakon', 'drakon', '<ruby>drak<rt class="ruby-XXL_L_L">竜</rt></ruby>on'], ['mondon', '<ruby>mon<rt class="ruby-XXL_L_L">金銭</rt></ruby><ruby>don<rt class="ruby-M_M_M">与える</rt></ruby>', '<ruby>mond<rt class="ruby-XXL_L_L">世界</rt></ruby>on'], ['pension', '<ruby>pension<rt class="ruby-XXL_L_L">下宿屋</rt></ruby>', '<ruby>pensi<rt class="ruby-XXL_L_L">年金</rt></ruby>on'], ['ordon', '<ruby>ordon<rt class="ruby-S_S_S">(を)命令する</rt></ruby>', '<ruby>ord<rt class="ruby-XL_L_L">順序</rt></ruby>on'], ['eskadron', 'eskadron', '<ruby>eskadr<rt class="ruby-XXL_L_L">[軍]艦隊</rt></ruby>on'], ['senton', '<ruby>sen<rt class="ruby-S_S_S">(~)なしで</rt></ruby><ruby>ton<rt class="ruby-XS_S_S">[楽]楽音</rt></ruby>', '<ruby>sent<rt class="ruby-S_S_S">(を)感じる</rt></ruby>on'], ['eston', 'eston', '<ruby>est<rt class="ruby-XS_S_S">(~)である</rt></ruby>on'], ['fanfaron', '<ruby>fanfaron<rt class="ruby-L_L_L">大言壮語する</rt></ruby>', '<ruby>fanfar<rt class="ruby-XS_S_S">[楽]ファンファーレ</rt></ruby>on'], ['fero', 'fero', '<ruby>fer<rt class="ruby-XXL_L_L">鉄</rt></ruby>o'], ['feston', '<ruby>feston<rt class="ruby-XXL_L_L">花綱</rt></ruby>', '<ruby>fest<rt class="ruby-S_S_S">(を)祝う</rt></ruby>on'], ['flegmon', 'flegmon', '<ruby>flegm<rt class="ruby-XXL_L_L">冷静</rt></ruby>on'], ['fronton', '<ruby>fronton<rt class="ruby-S_S_S">[建]ペディメント</rt></ruby>', '<ruby>front<rt class="ruby-XXL_L_L">正面</rt></ruby>on'], ['galon', '<ruby>galon<rt class="ruby-M_M_M">[服]モール</rt></ruby>', '<ruby>gal<rt class="ruby-XS_S_S">[生]胆汁</rt></ruby>on'], ['mason', '<ruby>mason<rt class="ruby-XXL_L_L">築く</rt></ruby>', '<ruby>mas<rt class="ruby-M_M_M">かたまり</rt></ruby>on'], ['helikon', 'helikon', '<ruby>helik<rt class="ruby-XS_S_S">[動]カタツムリ</rt></ruby>on'], ['kanon', '<ruby>kanon<rt class="ruby-XXL_L_L">[軍]大砲</rt></ruby>', '<ruby>kan<rt class="ruby-S_S_S">[植]アシ</rt></ruby>on'], ['kapon', '<ruby>kapon<rt class="ruby-S_S_S">去勢オンドリ</rt></ruby>', '<ruby>kap<rt class="ruby-XXL_L_L">頭</rt></ruby>on'], ['kokon', '<ruby>kokon<rt class="ruby-M_M_M">[虫]繭(まゆ)</rt></ruby>', '<ruby>kok<rt class="ruby-S_S_S">ニワトリ</rt></ruby>on'], ['kolon', '<ruby>kolon<rt class="ruby-XL_L_L">[建]円柱</rt></ruby>', '<ruby>kol<rt class="ruby-M_M_M">[解]首</rt></ruby>on'], ['komision', '<ruby>komision<rt class="ruby-XL_L_L">(調査)委員会</rt></ruby>', '<ruby>komisi<rt class="ruby-M_M_M">(を)委託する</rt></ruby>on'], ['salon', '<ruby>salon<rt class="ruby-XXL_L_L">サロン</rt></ruby>', '<ruby>sal<rt class="ruby-XXL_L_L">塩</rt></ruby>on'], ['ponton', '<ruby>ponton<rt class="ruby-XL_L_L">[軍]平底舟</rt></ruby>', '<ruby>pont<rt class="ruby-XXL_L_L">橋</rt></ruby>on'], ['koton', '<ruby>koton<rt class="ruby-XXL_L_L">綿</rt></ruby>', '<ruby>kot<rt class="ruby-XXL_L_L">泥</rt></ruby>on'], ['kripton', 'kripton', '<ruby>kript<rt class="ruby-XS_S_S">[宗]地下聖堂</rt></ruby>on'], ['kupon', '<ruby>kupon<rt class="ruby-M_M_M">クーポン券</rt></ruby>', '<ruby>kup<rt class="ruby-M_M_M">吸い玉</rt></ruby>on'], ['lakon', 'lakon', '<ruby>lak<rt class="ruby-XS_S_S">ラッカー</rt></ruby>on'], ['ludon', '<ruby>lu<rt class="ruby-XS_S_S">賃借する</rt></ruby><ruby>don<rt class="ruby-M_M_M">与える</rt></ruby>', '<ruby>lud<rt class="ruby-XS_S_S">(を)遊ぶ</rt></ruby>on'], ['melon', '<ruby>melon<rt class="ruby-L_L_L">[果]メロン</rt></ruby>', '<ruby>mel<rt class="ruby-S_S_S">アナグマ</rt></ruby>on'], ['menton', '<ruby>menton<rt class="ruby-XL_L_L">[解]下あご</rt></ruby>', '<ruby>ment<rt class="ruby-M_M_M">[植]ハッカ</rt></ruby>on'], ['milion', '<ruby>milion<rt class="ruby-XXL_L_L">百万</rt></ruby>', '<ruby>mili<rt class="ruby-S_S_S">[植]キビ</rt></ruby>on'], ['milionon', '<ruby>milion<rt class="ruby-XXL_L_L">百万</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>milion<rt class="ruby-XXL_L_L">百万</rt></ruby>on'], ['naŭon', '<ruby>naŭ<rt class="ruby-XXL_L_L">九</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>naŭ<rt class="ruby-XXL_L_L">九</rt></ruby>on'], ['violon', '<ruby>violon<rt class="ruby-S_S_S">[楽]バイオリン</rt></ruby>', '<ruby>viol<rt class="ruby-XS_S_S">[植]スミレ</rt></ruby>on'], ['refoj', '<ruby>re<rt class="ruby-S_S_S">再び</rt></ruby><ruby>foj<rt class="ruby-XXL_L_L">回</rt></ruby>', '<ruby>ref<rt class="ruby-S_S_S">リーフ</rt></ruby>oj'], ['trombon', '<ruby>trombon<rt class="ruby-M_M_M">[楽]トロンボーン</rt></ruby>', '<ruby>tromb<rt class="ruby-S_S_S">[気]たつまき</rt></ruby>on'], ['samo', 'samo', '<ruby>sam<rt class="ruby-L_L_L">同一の</rt></ruby>o'], ['savoj', 'savoj', '<ruby>sav<rt class="ruby-S_S_S">救助する</rt></ruby>oj'], ['senson', '<ruby>sen<rt class="ruby-S_S_S">(~)なしで</rt></ruby><ruby>son<rt class="ruby-S_S_S">音がする</rt></ruby>', '<ruby>sens<rt class="ruby-L_L_L">[生]感覚</rt></ruby>on'], ['sepon', '<ruby>sep<rt class="ruby-XXL_L_L">七</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>sep<rt class="ruby-XXL_L_L">七</rt></ruby>on'], ['skadron', 'skadron', '<ruby>skadr<rt class="ruby-S_S_S">[軍]騎兵中隊</rt></ruby>on'], ['stadion', '<ruby>stadion<rt class="ruby-XL_L_L">スタジアム</rt></ruby>', '<ruby>stadi<rt class="ruby-XXL_L_L">段階</rt></ruby>on'], ['tetraon', 'tetraon', '<ruby>tetra<rt class="ruby-XS_S_S">エゾライチョウ</rt></ruby>on'], ['timon', '<ruby>timon<rt class="ruby-XXL_L_L">かじ棒</rt></ruby>', '<ruby>tim<rt class="ruby-S_S_S">恐れる</rt></ruby>on'], ['valon', 'valon', '<ruby>val<rt class="ruby-M_M_M">[地]谷</rt></ruby>on'], ['veto', 'veto', '<ruby>vet<rt class="ruby-S_S_S">賭ける</rt></ruby>o']]
# overlap_6_a = [['dietan', '<ruby>diet<rt class="ruby-XS_S_S">[医]規定食</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>diet<rt class="ruby-XS_S_S">[医]規定食</rt></ruby>an'], ['afrikan', '<ruby>afrik<rt class="ruby-XS_S_S">[地名]アフリカ</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>afrik<rt class="ruby-XS_S_S">[地名]アフリカ</rt></ruby>an'], ['movadan', '<ruby>mov<rt class="ruby-L_L_L">動かす</rt></ruby><ruby>ad<rt class="ruby-XS_S_S">継続行為</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>mov<rt class="ruby-L_L_L">動かす</rt></ruby><ruby>ad<rt class="ruby-XS_S_S">継続行為</rt></ruby>an'], ['akcian', '<ruby>akci<rt class="ruby-M_M_M">[商]株式</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>akci<rt class="ruby-M_M_M">[商]株式</rt></ruby>an'], ['montaran', '<ruby>mont<rt class="ruby-XXL_L_L">山</rt></ruby><ruby>ar<rt class="ruby-S_S_S">集団</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>mont<rt class="ruby-XXL_L_L">山</rt></ruby><ruby>ar<rt class="ruby-S_S_S">集団</rt></ruby>an'], ['amerikan', '<ruby>amerik<rt class="ruby-S_S_S">[地名]アメリカ</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>amerik<rt class="ruby-S_S_S">[地名]アメリカ</rt></ruby>an'], ['regnan', '<ruby>regn<rt class="ruby-M_M_M">[法]国家</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>regn<rt class="ruby-M_M_M">[法]国家</rt></ruby>an'], ['dezertan', '<ruby>dezert<rt class="ruby-XXL_L_L">砂漠</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>dezert<rt class="ruby-XXL_L_L">砂漠</rt></ruby>an'], ['arĝentan', 'arĝentan', '<ruby>arĝent<rt class="ruby-XXL_L_L">銀</rt></ruby>an'], ['asocian', '<ruby>asoci<rt class="ruby-XXL_L_L">協会</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>asoci<rt class="ruby-XXL_L_L">協会</rt></ruby>an'], ['insulan', '<ruby>insul<rt class="ruby-XXL_L_L">島</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>insul<rt class="ruby-XXL_L_L">島</rt></ruby>an'], ['azian', '<ruby>azi<rt class="ruby-S_S_S">アジア</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>azi<rt class="ruby-S_S_S">アジア</rt></ruby>an'], ['ŝtatan', '<ruby>ŝtat<rt class="ruby-XXL_L_L">国家</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>ŝtat<rt class="ruby-XXL_L_L">国家</rt></ruby>an'], ['doman', '<ruby>dom<rt class="ruby-XXL_L_L">家</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>dom<rt class="ruby-XXL_L_L">家</rt></ruby>an'], ['montan', '<ruby>mont<rt class="ruby-XXL_L_L">山</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>mont<rt class="ruby-XXL_L_L">山</rt></ruby>an'], ['familian', '<ruby>famili<rt class="ruby-XXL_L_L">家族</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>famili<rt class="ruby-XXL_L_L">家族</rt></ruby>an'], ['urban', '<ruby>urb<rt class="ruby-XXL_L_L">市</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>urb<rt class="ruby-XXL_L_L">市</rt></ruby>an'], ['inka', 'inka', '<ruby>ink<rt class="ruby-S_S_S">インク</rt></ruby>a'], ['popolan', '<ruby>popol<rt class="ruby-XXL_L_L">人民</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>popol<rt class="ruby-XXL_L_L">人民</rt></ruby>an'], ['dekan', '<ruby>dekan<rt class="ruby-XXL_L_L">学部長</rt></ruby>', '<ruby>dek<rt class="ruby-XXL_L_L">十</rt></ruby>an'], ['partian', '<ruby>parti<rt class="ruby-M_M_M">[政]党派</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>parti<rt class="ruby-M_M_M">[政]党派</rt></ruby>an'], ['lokan', '<ruby>lok<rt class="ruby-XL_L_L">場所</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>lok<rt class="ruby-XL_L_L">場所</rt></ruby>an'], ['ŝipan', '<ruby>ŝip<rt class="ruby-XXL_L_L">船</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>ŝip<rt class="ruby-XXL_L_L">船</rt></ruby>an'], ['eklezian', '<ruby>eklezi<rt class="ruby-XL_L_L">[宗]教会</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>eklezi<rt class="ruby-XL_L_L">[宗]教会</rt></ruby>an'], ['landan', '<ruby>land<rt class="ruby-XXL_L_L">国</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>land<rt class="ruby-XXL_L_L">国</rt></ruby>an'], ['orientan', '<ruby>orient<rt class="ruby-S_S_S">方位定める;東</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>orient<rt class="ruby-S_S_S">方位定める;東</rt></ruby>an'], ['lernejan', '<ruby>lern<rt class="ruby-XS_S_S">(を)学習する</rt></ruby><ruby>ej<rt class="ruby-S_S_S">場所</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>lern<rt class="ruby-XS_S_S">(を)学習する</rt></ruby><ruby>ej<rt class="ruby-S_S_S">場所</rt></ruby>an'], ['enlandan', '<ruby>en<rt class="ruby-L_L_L">中で</rt></ruby><ruby>land<rt class="ruby-XXL_L_L">国</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>en<rt class="ruby-L_L_L">中で</rt></ruby><ruby>land<rt class="ruby-XXL_L_L">国</rt></ruby>an'], ['kalkan', '<ruby>kalkan<rt class="ruby-XXL_L_L">[解]踵</rt></ruby>', '<ruby>kalk<rt class="ruby-M_M_M">[化]石灰</rt></ruby>an'], ['estraran', '<ruby>estr<rt class="ruby-XS_S_S">[接尾辞]長</rt></ruby><ruby>ar<rt class="ruby-S_S_S">集団</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>estr<rt class="ruby-XS_S_S">[接尾辞]長</rt></ruby><ruby>ar<rt class="ruby-S_S_S">集団</rt></ruby>an'], ['etnan', '<ruby>etn<rt class="ruby-XL_L_L">民族</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>etn<rt class="ruby-XL_L_L">民族</rt></ruby>an'], ['eŭropan', '<ruby>eŭrop<rt class="ruby-M_M_M">ヨーロッパ</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>eŭrop<rt class="ruby-M_M_M">ヨーロッパ</rt></ruby>an'], ['fazan', '<ruby>fazan<rt class="ruby-XL_L_L">[鳥]キジ</rt></ruby>', '<ruby>faz<rt class="ruby-S_S_S">[理]位相</rt></ruby>an'], ['polican', '<ruby>polic<rt class="ruby-XXL_L_L">警察</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>polic<rt class="ruby-XXL_L_L">警察</rt></ruby>an'], ['socian', '<ruby>soci<rt class="ruby-XXL_L_L">社会</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>soci<rt class="ruby-XXL_L_L">社会</rt></ruby>an'], ['societan', '<ruby>societ<rt class="ruby-XXL_L_L">会</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>societ<rt class="ruby-XXL_L_L">会</rt></ruby>an'], ['grupan', '<ruby>grup<rt class="ruby-M_M_M">グループ</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>grup<rt class="ruby-M_M_M">グループ</rt></ruby>an'], ['havaj', 'havaj', '<ruby>hav<rt class="ruby-XS_S_S">持っている</rt></ruby>aj'], ['ligan', '<ruby>lig<rt class="ruby-XS_S_S">結ぶ;連盟</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>lig<rt class="ruby-XS_S_S">結ぶ;連盟</rt></ruby>an'], ['nacian', '<ruby>naci<rt class="ruby-XXL_L_L">国民</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>naci<rt class="ruby-XXL_L_L">国民</rt></ruby>an'], ['koran', '<ruby>koran<rt class="ruby-S_S_S">[宗]コーラン</rt></ruby>', '<ruby>kor<rt class="ruby-XXL_L_L">心</rt></ruby>an'], ['religian', '<ruby>religi<rt class="ruby-XXL_L_L">宗教</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>religi<rt class="ruby-XXL_L_L">宗教</rt></ruby>an'], ['kuban', '<ruby>kub<rt class="ruby-M_M_M">立方体</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>kub<rt class="ruby-M_M_M">立方体</rt></ruby>an'], ['lama', '<ruby>lama<rt class="ruby-M_M_M">[宗]ラマ僧</rt></ruby>', '<ruby>lam<rt class="ruby-S_S_S">びっこの</rt></ruby>a'], ['majoran', '<ruby>major<rt class="ruby-S_S_S">[軍]陸軍少佐</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>major<rt class="ruby-S_S_S">[軍]陸軍少佐</rt></ruby>an'], ['malaj', 'malaj', '<ruby>mal<rt class="ruby-M_M_M">正反対</rt></ruby>aj'], ['marian', 'marian', '<ruby>mari<rt class="ruby-XL_L_L">マリア</rt></ruby>an'], ['nordan', '<ruby>nord<rt class="ruby-XXL_L_L">北</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>nord<rt class="ruby-XXL_L_L">北</rt></ruby>an'], ['paran', 'paran', '<ruby>par<rt class="ruby-XL_L_L">一対</rt></ruby>an'], ['parizan', '<ruby>pariz<rt class="ruby-M_M_M">[地名]パリ</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>pariz<rt class="ruby-M_M_M">[地名]パリ</rt></ruby>an'], ['parokan', '<ruby>parok<rt class="ruby-XL_L_L">[宗]教区</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>parok<rt class="ruby-XL_L_L">[宗]教区</rt></ruby>an'], ['podian', '<ruby>podi<rt class="ruby-L_L_L">ひな壇</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>podi<rt class="ruby-L_L_L">ひな壇</rt></ruby>an'], ['rusian', '<ruby>rus<rt class="ruby-XS_S_S">ロシア人</rt></ruby>i<ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>rus<rt class="ruby-XS_S_S">ロシア人</rt></ruby>ian'], ['satan', '<ruby>satan<rt class="ruby-M_M_M">[宗]サタン</rt></ruby>', '<ruby>sat<rt class="ruby-XS_S_S">満腹した</rt></ruby>an'], ['sektan', '<ruby>sekt<rt class="ruby-M_M_M">[宗]宗派</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>sekt<rt class="ruby-M_M_M">[宗]宗派</rt></ruby>an'], ['senatan', '<ruby>senat<rt class="ruby-M_M_M">[政]参議院</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>senat<rt class="ruby-M_M_M">[政]参議院</rt></ruby>an'], ['skisman', '<ruby>skism<rt class="ruby-S_S_S">(団体の)分裂</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>skism<rt class="ruby-S_S_S">(団体の)分裂</rt></ruby>an'], ['sudan', 'sudan', '<ruby>sud<rt class="ruby-XXL_L_L">南</rt></ruby>an'], ['utopian', '<ruby>utopi<rt class="ruby-S_S_S">ユートピア</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>utopi<rt class="ruby-S_S_S">ユートピア</rt></ruby>an'], ['vilaĝan', '<ruby>vilaĝ<rt class="ruby-XXL_L_L">村</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>vilaĝ<rt class="ruby-XXL_L_L">村</rt></ruby>an']]
# overlap_7_a = [['alte', '<ruby>alte<rt class="ruby-XS_S_S">タチアオイ</rt></ruby>', '<ruby>alt<rt class="ruby-M_M_M">高い</rt></ruby>e'], ['apoge', '<ruby>apoge<rt class="ruby-L_L_L">[天]遠地点</rt></ruby>', '<ruby>apog<rt class="ruby-M_M_M">(を)支える</rt></ruby>e'], ['kaze', '<ruby>kaze<rt class="ruby-L_L_L">[化]凝乳</rt></ruby>', '<ruby>kaz<rt class="ruby-L_L_L">[文]格</rt></ruby>e'], ['pere', '<ruby>pere<rt class="ruby-M_M_M">破滅する</rt></ruby>', '<ruby>per<rt class="ruby-M_M_M">よって</rt></ruby>e'], ['kore', 'kore', '<ruby>kor<rt class="ruby-XXL_L_L">心</rt></ruby>e'], ['male', 'male', '<ruby>mal<rt class="ruby-M_M_M">正反対</rt></ruby>e'], ['sole', '<ruby>sole<rt class="ruby-S_S_S">シタビラメ</rt></ruby>', '<ruby>sol<rt class="ruby-S_S_S">唯一の</rt></ruby>e']]
# overlap_8_a = [['regulus', 'regulus', '<ruby>regul<rt class="ruby-XXL_L_L">規則</rt></ruby><ruby>us<rt class="ruby-XS_S_S">条件法</rt></ruby>'], ['akirant', 'akirant', '<ruby>akir<rt class="ruby-XS_S_S">(を)獲得する</rt></ruby><ruby>ant<rt class="ruby-XS_S_S">能動;継続</rt></ruby>'], ['radius', 'radius', '<ruby>radi<rt class="ruby-L_L_L">[理]線</rt></ruby><ruby>us<rt class="ruby-XS_S_S">条件法</rt></ruby>'], ['premis', '<ruby>premis<rt class="ruby-XXL_L_L">前提</rt></ruby>', '<ruby>prem<rt class="ruby-M_M_M">(を)押える</rt></ruby><ruby>is<rt class="ruby-XS_S_S">過去形</rt></ruby>'], ['sonat', '<ruby>sonat<rt class="ruby-M_M_M">[楽]ソナタ</rt></ruby>', '<ruby>son<rt class="ruby-S_S_S">音がする</rt></ruby><ruby>at<rt class="ruby-XS_S_S">受動継続</rt></ruby>'], ['format', '<ruby>format<rt class="ruby-XXL_L_L">[印]判</rt></ruby>', '<ruby>form<rt class="ruby-XXL_L_L">形</rt></ruby><ruby>at<rt class="ruby-XS_S_S">受動継続</rt></ruby>'], ['markot', '<ruby>markot<rt class="ruby-XXL_L_L">[園]取木</rt></ruby>', '<ruby>mark<rt class="ruby-XXL_L_L">しるし</rt></ruby><ruby>ot<rt class="ruby-XS_S_S">受動将然</rt></ruby>'], ['nomad', '<ruby>nomad<rt class="ruby-XXL_L_L">遊牧民</rt></ruby>', '<ruby>nom<rt class="ruby-XXL_L_L">名前</rt></ruby><ruby>ad<rt class="ruby-XS_S_S">継続行為</rt></ruby>'], ['kantat', '<ruby>kantat<rt class="ruby-S_S_S">[楽]カンタータ</rt></ruby>', '<ruby>kant<rt class="ruby-M_M_M">(を)歌う</rt></ruby><ruby>at<rt class="ruby-XS_S_S">受動継続</rt></ruby>'], ['kolorad', 'kolorad', '<ruby>kolor<rt class="ruby-XXL_L_L">色</rt></ruby><ruby>ad<rt class="ruby-XS_S_S">継続行為</rt></ruby>'], ['diplomat', '<ruby>diplomat<rt class="ruby-XXL_L_L">外交官</rt></ruby>', '<ruby>diplom<rt class="ruby-XXL_L_L">免状</rt></ruby><ruby>at<rt class="ruby-XS_S_S">受動継続</rt></ruby>'], ['diskont', '<ruby>diskont<rt class="ruby-S_S_S">[商]手形割引する</rt></ruby>', '<ruby>disk<rt class="ruby-XXL_L_L">円盤</rt></ruby><ruby>ont<rt class="ruby-XS_S_S">能動;将然</rt></ruby>'], ['endos', 'endos', '<ruby>end<rt class="ruby-XXL_L_L">必要</rt></ruby><ruby>os<rt class="ruby-XS_S_S">未来形</rt></ruby>'], ['esperant', '<ruby>esperant<rt class="ruby-XL_L_L">エスペラント</rt></ruby>', '<ruby>esper<rt class="ruby-S_S_S">(を)希望する</rt></ruby><ruby>ant<rt class="ruby-XS_S_S">能動;継続</rt></ruby>'], ['forkant', '<ruby>for<rt class="ruby-S_S_S">離れて</rt></ruby><ruby>kant<rt class="ruby-M_M_M">(を)歌う</rt></ruby>', '<ruby>fork<rt class="ruby-XS_S_S">[料]フォーク</rt></ruby><ruby>ant<rt class="ruby-XS_S_S">能動;継続</rt></ruby>'], ['gravit', 'gravit', '<ruby>grav<rt class="ruby-XL_L_L">重要な</rt></ruby><ruby>it<rt class="ruby-XS_S_S">受動完了</rt></ruby>'], ['konus', '<ruby>konus<rt class="ruby-XL_L_L">[数]円錐</rt></ruby>', '<ruby>kon<rt class="ruby-XS_S_S">知っている</rt></ruby><ruby>us<rt class="ruby-XS_S_S">条件法</rt></ruby>'], ['salat', '<ruby>salat<rt class="ruby-M_M_M">[料]サラダ</rt></ruby>', '<ruby>sal<rt class="ruby-XXL_L_L">塩</rt></ruby><ruby>at<rt class="ruby-XS_S_S">受動継続</rt></ruby>'], ['legat', '<ruby>legat<rt class="ruby-S_S_S">[宗]教皇特使</rt></ruby>', '<ruby>leg<rt class="ruby-XS_S_S">(を)読む</rt></ruby><ruby>at<rt class="ruby-XS_S_S">受動継続</rt></ruby>'], ['lekant', '<ruby>lekant<rt class="ruby-XS_S_S">[植]マーガレット</rt></ruby>', '<ruby>lek<rt class="ruby-S_S_S">なめる</rt></ruby><ruby>ant<rt class="ruby-XS_S_S">能動;継続</rt></ruby>'], ['lotus', '<ruby>lotus<rt class="ruby-L_L_L">[植]ハス</rt></ruby>', '<ruby>lot<rt class="ruby-M_M_M">くじ</rt></ruby><ruby>us<rt class="ruby-XS_S_S">条件法</rt></ruby>'], ['malvolont', '<ruby>mal<rt class="ruby-M_M_M">正反対</rt></ruby><ruby>volont<rt class="ruby-M_M_M">自ら進んで</rt></ruby>', '<ruby>mal<rt class="ruby-M_M_M">正反対</rt></ruby><ruby>vol<rt class="ruby-XS_S_S">意志がある</rt></ruby><ruby>ont<rt class="ruby-XS_S_S">能動;将然</rt></ruby>'], ['mankis', '<ruby>man<rt class="ruby-XXL_L_L">手</rt></ruby><ruby>kis<rt class="ruby-XS_S_S">キスする</rt></ruby>', '<ruby>mank<rt class="ruby-M_M_M">欠けている</rt></ruby><ruby>is<rt class="ruby-XS_S_S">過去形</rt></ruby>'], ['minus', '<ruby>minus<rt class="ruby-XL_L_L">マイナス</rt></ruby>', '<ruby>min<rt class="ruby-XXL_L_L">鉱山</rt></ruby><ruby>us<rt class="ruby-XS_S_S">条件法</rt></ruby>'], ['patos', '<ruby>patos<rt class="ruby-M_M_M">[芸]パトス</rt></ruby>', '<ruby>pat<rt class="ruby-XS_S_S">フライパン</rt></ruby><ruby>os<rt class="ruby-XS_S_S">未来形</rt></ruby>'], ['predikat', '<ruby>predikat<rt class="ruby-XXL_L_L">[文]述部</rt></ruby>', '<ruby>predik<rt class="ruby-M_M_M">(を)説教する</rt></ruby><ruby>at<rt class="ruby-XS_S_S">受動継続</rt></ruby>'], ['rabat', '<ruby>rabat<rt class="ruby-L_L_L">[商]割引</rt></ruby>', '<ruby>rab<rt class="ruby-XS_S_S">強奪する</rt></ruby><ruby>at<rt class="ruby-XS_S_S">受動継続</rt></ruby>'], ['rabot', '<ruby>rabot<rt class="ruby-XS_S_S">かんなをかける</rt></ruby>', '<ruby>rab<rt class="ruby-XS_S_S">強奪する</rt></ruby><ruby>ot<rt class="ruby-XS_S_S">受動将然</rt></ruby>'], ['remont', 'remont', '<ruby>rem<rt class="ruby-XXL_L_L">漕ぐ</rt></ruby><ruby>ont<rt class="ruby-XS_S_S">能動;将然</rt></ruby>'], ['satirus', 'satirus', '<ruby>satir<rt class="ruby-S_S_S">諷刺(詩;文)</rt></ruby><ruby>us<rt class="ruby-XS_S_S">条件法</rt></ruby>'], ['sendat', '<ruby>sen<rt class="ruby-S_S_S">(~)なしで</rt></ruby><ruby>dat<rt class="ruby-XL_L_L">日付</rt></ruby>', '<ruby>send<rt class="ruby-L_L_L">(を)送る</rt></ruby><ruby>at<rt class="ruby-XS_S_S">受動継続</rt></ruby>'], ['sendot', '<ruby>sen<rt class="ruby-S_S_S">(~)なしで</rt></ruby><ruby>dot<rt class="ruby-S_S_S">持参金</rt></ruby>', '<ruby>send<rt class="ruby-L_L_L">(を)送る</rt></ruby><ruby>ot<rt class="ruby-XS_S_S">受動将然</rt></ruby>'], ['spirit', '<ruby>spirit<rt class="ruby-XXL_L_L">精神</rt></ruby>', '<ruby>spir<rt class="ruby-S_S_S">呼吸する</rt></ruby><ruby>it<rt class="ruby-XS_S_S">受動完了</rt></ruby>'], ['spirant', 'spirant', '<ruby>spir<rt class="ruby-S_S_S">呼吸する</rt></ruby><ruby>ant<rt class="ruby-XS_S_S">能動;継続</rt></ruby>'], ['taksus', '<ruby>taksus<rt class="ruby-L_L_L">[植]イチイ</rt></ruby>', '<ruby>taks<rt class="ruby-XS_S_S">(を)評価する</rt></ruby><ruby>us<rt class="ruby-XS_S_S">条件法</rt></ruby>'], ['tenis', 'tenis', '<ruby>ten<rt class="ruby-XS_S_S">支え持つ</rt></ruby><ruby>is<rt class="ruby-XS_S_S">過去形</rt></ruby>'], ['traktat', '<ruby>traktat<rt class="ruby-XXL_L_L">[政]条約</rt></ruby>', '<ruby>trakt<rt class="ruby-XS_S_S">(を)取り扱う</rt></ruby><ruby>at<rt class="ruby-XS_S_S">受動継続</rt></ruby>'], ['trikot', '<ruby>trikot<rt class="ruby-XS_S_S">[織]トリコット</rt></ruby>', '<ruby>trik<rt class="ruby-XS_S_S">編み物をする</rt></ruby><ruby>ot<rt class="ruby-XS_S_S">受動将然</rt></ruby>'], ['trilit', '<ruby>tri<rt class="ruby-XXL_L_L">三</rt></ruby><ruby>lit<rt class="ruby-XS_S_S">ベッド</rt></ruby>', '<ruby>tril<rt class="ruby-XS_S_S">[楽]トリル</rt></ruby><ruby>it<rt class="ruby-XS_S_S">受動完了</rt></ruby>'], ['vizit', '<ruby>vizit<rt class="ruby-XS_S_S">(を)訪問する</rt></ruby>', '<ruby>viz<rt class="ruby-L_L_L">ビザ</rt></ruby><ruby>it<rt class="ruby-XS_S_S">受動完了</rt></ruby>'], ['volont', '<ruby>volont<rt class="ruby-M_M_M">自ら進んで</rt></ruby>', '<ruby>vol<rt class="ruby-XS_S_S">意志がある</rt></ruby><ruby>ont<rt class="ruby-XS_S_S">能動;将然</rt></ruby>']]
# overlap_9_a = [['premi', '<ruby>premi<rt class="ruby-XXL_L_L">賞品</rt></ruby>', '<ruby>prem<rt class="ruby-M_M_M">(を)押える</rt></ruby>i'], ['bari', 'bari', '<ruby>bar<rt class="ruby-XL_L_L">障害</rt></ruby>i'], ['tempi', '<ruby>tempi<rt class="ruby-L_L_L">こめかみ</rt></ruby>', '<ruby>temp<rt class="ruby-XXL_L_L">時間</rt></ruby>i'], ['noktu', '<ruby>noktu<rt class="ruby-S_S_S">[鳥]コフクロウ</rt></ruby>', '<ruby>nokt<rt class="ruby-XXL_L_L">夜</rt></ruby>u'], ['vakcini', 'vakcini', '<ruby>vakcin<rt class="ruby-M_M_M">[薬]ワクチン</rt></ruby>i'], ['procesi', '<ruby>procesi<rt class="ruby-XXL_L_L">[宗]行列</rt></ruby>', '<ruby>proces<rt class="ruby-XXL_L_L">[法]訴訟</rt></ruby>i'], ['statu', '<ruby>statu<rt class="ruby-XXL_L_L">立像</rt></ruby>', '<ruby>stat<rt class="ruby-XXL_L_L">状態</rt></ruby>u'], ['devi', 'devi', '<ruby>dev<rt class="ruby-XL_L_L">must</rt></ruby>i'], ['feri', '<ruby>feri<rt class="ruby-XL_L_L">休日</rt></ruby>', '<ruby>fer<rt class="ruby-XXL_L_L">鉄</rt></ruby>i'], ['fleksi', '<ruby>fleksi<rt class="ruby-S_S_S">[文]語尾変化</rt></ruby>', '<ruby>fleks<rt class="ruby-S_S_S">(を)曲げる</rt></ruby>i'], ['pensi', '<ruby>pensi<rt class="ruby-XXL_L_L">年金</rt></ruby>', '<ruby>pens<rt class="ruby-XXL_L_L">思う</rt></ruby>i'], ['jesu', '<ruby>jesu<rt class="ruby-S_S_S">[宗]イエス</rt></ruby>', '<ruby>jes<rt class="ruby-XL_L_L">はい</rt></ruby>u'], ['konfesi', 'konfesi', '<ruby>konfes<rt class="ruby-M_M_M">(を)告白する</rt></ruby>i'], ['konsili', 'konsili', '<ruby>konsil<rt class="ruby-S_S_S">(を)助言する</rt></ruby>i'], ['legi', '<ruby>legi<rt class="ruby-S_S_S">[史]軍団</rt></ruby>', '<ruby>leg<rt class="ruby-XS_S_S">(を)読む</rt></ruby>i'], ['licenci', 'licenci', '<ruby>licenc<rt class="ruby-XL_L_L">[商]認可</rt></ruby>i'], ['loĝi', '<ruby>loĝi<rt class="ruby-S_S_S">[劇]桟敷</rt></ruby>', '<ruby>loĝ<rt class="ruby-XS_S_S">(に)住む</rt></ruby>i'], ['meti', '<ruby>meti<rt class="ruby-L_L_L">手仕事</rt></ruby>', '<ruby>met<rt class="ruby-S_S_S">(を)置く</rt></ruby>i'], ['pasi', '<ruby>pasi<rt class="ruby-XXL_L_L">情熱</rt></ruby>', '<ruby>pas<rt class="ruby-S_S_S">通過する</rt></ruby>i'], ['revu', '<ruby>revu<rt class="ruby-M_M_M">専門雑誌</rt></ruby>', '<ruby>rev<rt class="ruby-XS_S_S">空想する</rt></ruby>u'], ['rabi', '<ruby>rabi<rt class="ruby-XS_S_S">[病]狂犬病</rt></ruby>', '<ruby>rab<rt class="ruby-XS_S_S">強奪する</rt></ruby>i'], ['religi', '<ruby>religi<rt class="ruby-XXL_L_L">宗教</rt></ruby>', '<ruby>re<rt class="ruby-S_S_S">再び</rt></ruby><ruby>lig<rt class="ruby-XS_S_S">結ぶ;連盟</rt></ruby>i'], ['sagu', '<ruby>sagu<rt class="ruby-M_M_M">[料]サゴ粉</rt></ruby>', '<ruby>sag<rt class="ruby-XXL_L_L">矢</rt></ruby>u'], ['sekci', '<ruby>sekci<rt class="ruby-XXL_L_L">部</rt></ruby>', '<ruby>sekc<rt class="ruby-XS_S_S">[医]切断する</rt></ruby>i'], ['sendi', '<ruby>sen<rt class="ruby-S_S_S">(~)なしで</rt></ruby><ruby>di<rt class="ruby-XXL_L_L">神</rt></ruby>', '<ruby>send<rt class="ruby-L_L_L">(を)送る</rt></ruby>i'], ['teni', '<ruby>teni<rt class="ruby-XS_S_S">サナダムシ</rt></ruby>', '<ruby>ten<rt class="ruby-XS_S_S">支え持つ</rt></ruby>i'], ['vaku', 'vaku', '<ruby>vak<rt class="ruby-XS_S_S">あいている</rt></ruby>u'], ['vizi', '<ruby>vizi<rt class="ruby-XXL_L_L">幻影</rt></ruby>', '<ruby>viz<rt class="ruby-L_L_L">ビザ</rt></ruby>i']]

# # ===== 2つ目の Python 出力から得られた値 =====
# overlap_1_b =[['buro', 'buro', 'buro'], ['haloo', 'haloo', 'haloo'], ['tauxro', 'tauxro', 'tauxro'], ['unesko', 'unesko', 'unesko']]
# overlap_2_b = [['alo', '<ruby>alo<rt class="ruby-M_M_M">アロエ</rt></ruby>', '<ruby>al<rt class="ruby-S_S_S">~の方へ</rt></ruby>o'], ['duon', '<ruby>du<rt class="ruby-X_X_X">二</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>du<rt class="ruby-X_X_X">二</rt></ruby>on'], ['okon', '<ruby>ok<rt class="ruby-X_X_X">八</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>ok<rt class="ruby-X_X_X">八</rt></ruby>on']]
# overlap_2_2_b = [['sia', 'sia', '<ruby>si<rt class="ruby-M_M_M">自分</rt></ruby>a'], ['eman', 'eman', '<ruby>em<rt class="ruby-M_M_M">傾向</rt></ruby>an'], ['lian', '<ruby>lian<rt class="ruby-S_S_S">[植]つる植物</rt></ruby>', '<ruby>li<rt class="ruby-X_X_X">彼</rt></ruby>an'], ['pian', '<ruby>pian<rt class="ruby-M_M_M">[楽]ピアノ</rt></ruby>', '<ruby>pi<rt class="ruby-S_S_S">信心深い</rt></ruby>an']]
# overlap_3_b = [['agat', '<ruby>agat<rt class="ruby-M_M_M">[鉱]メノウ</rt></ruby>', '<ruby>ag<rt class="ruby-S_S_S">行動する</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['agit', '<ruby>agit<rt class="ruby-S_S_S">(を)扇動する</rt></ruby>', '<ruby>ag<rt class="ruby-S_S_S">行動する</rt></ruby><ruby>it<rt class="ruby-S_S_S">受動完了</rt></ruby>'], ['amas', '<ruby>amas<rt class="ruby-M_M_M">集積;大衆</rt></ruby>', '<ruby>am<rt class="ruby-S_S_S">愛する</rt></ruby><ruby>as<rt class="ruby-S_S_S">現在形</rt></ruby>'], ['iris', '<ruby>iris<rt class="ruby-M_M_M">[解]虹彩</rt></ruby>', '<ruby>ir<rt class="ruby-M_M_M">行く</rt></ruby><ruby>is<rt class="ruby-S_S_S">過去形</rt></ruby>'], ['irit', 'irit', '<ruby>ir<rt class="ruby-M_M_M">行く</rt></ruby><ruby>it<rt class="ruby-S_S_S">受動完了</rt></ruby>']]
# overlap_4_b = []
# overlap_5_b = [['nombron', '<ruby>nombr<rt class="ruby-X_X_X">数</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>nombr<rt class="ruby-X_X_X">数</rt></ruby>on'], ['patron', '<ruby>patron<rt class="ruby-X_X_X">後援者</rt></ruby>', '<ruby>patr<rt class="ruby-X_X_X">父</rt></ruby>on'], ['karbon', '<ruby>karbon<rt class="ruby-L_L_L">[化]炭素</rt></ruby>', '<ruby>karb<rt class="ruby-X_X_X">炭</rt></ruby>on'], ['ciklon', '<ruby>ciklon<rt class="ruby-X_X_X">低気圧</rt></ruby>', '<ruby>cikl<rt class="ruby-X_X_X">周期</rt></ruby>on'], ['aldon', '<ruby>al<rt class="ruby-S_S_S">~の方へ</rt></ruby><ruby>don<rt class="ruby-M_M_M">与える</rt></ruby>', '<ruby>ald<rt class="ruby-M_M_M">アルト</rt></ruby>on'], ['balon', '<ruby>balon<rt class="ruby-X_X_X">気球</rt></ruby>', '<ruby>bal<rt class="ruby-M_M_M">舞踏会</rt></ruby>on'], ['baron', '<ruby>baron<rt class="ruby-X_X_X">男爵</rt></ruby>', '<ruby>bar<rt class="ruby-L_L_L">障害</rt></ruby>on'], ['baston', '<ruby>baston<rt class="ruby-X_X_X">棒</rt></ruby>', '<ruby>bast<rt class="ruby-M_M_M">[植]じん皮</rt></ruby>on'], ['magneton', '<ruby>magnet<rt class="ruby-L_L_L">[理]磁石</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>magnet<rt class="ruby-L_L_L">[理]磁石</rt></ruby>on'], ['beton', 'beton', '<ruby>bet<rt class="ruby-M_M_M">ビート</rt></ruby>on'], ['bombon', '<ruby>bombon<rt class="ruby-L_L_L">キャンデー</rt></ruby>', '<ruby>bomb<rt class="ruby-X_X_X">爆弾</rt></ruby>on'], ['breton', 'breton', '<ruby>bret<rt class="ruby-X_X_X">棚</rt></ruby>on'], ['burgxon', '<ruby>burgxon<rt class="ruby-X_X_X">芽</rt></ruby>', '<ruby>burgx<rt class="ruby-M_M_M">ブルジョワ</rt></ruby>on'], ['centon', '<ruby>cent<rt class="ruby-X_X_X">百</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>cent<rt class="ruby-X_X_X">百</rt></ruby>on'], ['milon', '<ruby>mil<rt class="ruby-X_X_X">千</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>mil<rt class="ruby-X_X_X">千</rt></ruby>on'], ['kanton', '<ruby>kanton<rt class="ruby-M_M_M">(フランスの)郡</rt></ruby>', '<ruby>kant<rt class="ruby-M_M_M">(を)歌う</rt></ruby>on'], ['citron', '<ruby>citron<rt class="ruby-M_M_M">[果]シトロン</rt></ruby>', '<ruby>citr<rt class="ruby-M_M_M">[楽]チター</rt></ruby>on'], ['platon', 'platon', '<ruby>plat<rt class="ruby-L_L_L">平たい</rt></ruby>on'], ['dekon', '<ruby>dek<rt class="ruby-X_X_X">十</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>dek<rt class="ruby-X_X_X">十</rt></ruby>on'], ['kvaron', '<ruby>kvar<rt class="ruby-X_X_X">四</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>kvar<rt class="ruby-X_X_X">四</rt></ruby>on'], ['kvinon', '<ruby>kvin<rt class="ruby-X_X_X">五</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>kvin<rt class="ruby-X_X_X">五</rt></ruby>on'], ['seson', '<ruby>ses<rt class="ruby-X_X_X">六</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>ses<rt class="ruby-X_X_X">六</rt></ruby>on'], ['trion', '<ruby>tri<rt class="ruby-X_X_X">三</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>tri<rt class="ruby-X_X_X">三</rt></ruby>on'], ['karton', '<ruby>karton<rt class="ruby-X_X_X">厚紙</rt></ruby>', '<ruby>kart<rt class="ruby-L_L_L">カード</rt></ruby>on'], ['foton', '<ruby>fot<rt class="ruby-S_S_S">写真を撮る</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>fot<rt class="ruby-S_S_S">写真を撮る</rt></ruby>on'], ['peron', '<ruby>peron<rt class="ruby-X_X_X">階段</rt></ruby>', '<ruby>per<rt class="ruby-M_M_M">よって</rt></ruby>on'], ['elektron', '<ruby>elektr<rt class="ruby-X_X_X">電気</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>elektr<rt class="ruby-X_X_X">電気</rt></ruby>on'], ['drakon', 'drakon', '<ruby>drak<rt class="ruby-X_X_X">竜</rt></ruby>on'], ['mondon', '<ruby>mon<rt class="ruby-L_L_L">金銭</rt></ruby><ruby>don<rt class="ruby-M_M_M">与える</rt></ruby>', '<ruby>mond<rt class="ruby-X_X_X">世界</rt></ruby>on'], ['pension', '<ruby>pension<rt class="ruby-X_X_X">下宿屋</rt></ruby>', '<ruby>pensi<rt class="ruby-X_X_X">年金</rt></ruby>on'], ['ordon', '<ruby>ordon<rt class="ruby-M_M_M">(を)命令する</rt></ruby>', '<ruby>ord<rt class="ruby-L_L_L">順序</rt></ruby>on'], ['eskadron', 'eskadron', '<ruby>eskadr<rt class="ruby-L_L_L">[軍]艦隊</rt></ruby>on'], ['senton', '<ruby>sen<rt class="ruby-S_S_S">(~)なしで</rt></ruby><ruby>ton<rt class="ruby-M_M_M">[楽]楽音</rt></ruby>', '<ruby>sent<rt class="ruby-M_M_M">(を)感じる</rt></ruby>on'], ['eston', 'eston', '<ruby>est<rt class="ruby-S_S_S">(~)である</rt></ruby>on'], ['fanfaron', '<ruby>fanfaron<rt class="ruby-L_L_L">大言壮語する</rt></ruby>', '<ruby>fanfar<rt class="ruby-S_S_S">[楽]ファンファーレ</rt></ruby>on'], ['fero', 'fero', '<ruby>fer<rt class="ruby-X_X_X">鉄</rt></ruby>o'], ['feston', '<ruby>feston<rt class="ruby-X_X_X">花綱</rt></ruby>', '<ruby>fest<rt class="ruby-M_M_M">(を)祝う</rt></ruby>on'], ['flegmon', 'flegmon', '<ruby>flegm<rt class="ruby-X_X_X">冷静</rt></ruby>on'], ['fronton', '<ruby>fronton<rt class="ruby-M_M_M">[建]ペディメント</rt></ruby>', '<ruby>front<rt class="ruby-X_X_X">正面</rt></ruby>on'], ['galon', '<ruby>galon<rt class="ruby-M_M_M">[服]モール</rt></ruby>', '<ruby>gal<rt class="ruby-M_M_M">[生]胆汁</rt></ruby>on'], ['mason', '<ruby>mason<rt class="ruby-X_X_X">築く</rt></ruby>', '<ruby>mas<rt class="ruby-M_M_M">かたまり</rt></ruby>on'], ['helikon', 'helikon', '<ruby>helik<rt class="ruby-S_S_S">[動]カタツムリ</rt></ruby>on'], ['kanon', '<ruby>kanon<rt class="ruby-L_L_L">[軍]大砲</rt></ruby>', '<ruby>kan<rt class="ruby-M_M_M">[植]アシ</rt></ruby>on'], ['kapon', '<ruby>kapon<rt class="ruby-M_M_M">去勢オンドリ</rt></ruby>', '<ruby>kap<rt class="ruby-X_X_X">頭</rt></ruby>on'], ['kokon', '<ruby>kokon<rt class="ruby-M_M_M">[虫]繭(まゆ)</rt></ruby>', '<ruby>kok<rt class="ruby-M_M_M">ニワトリ</rt></ruby>on'], ['kolon', '<ruby>kolon<rt class="ruby-L_L_L">[建]円柱</rt></ruby>', '<ruby>kol<rt class="ruby-M_M_M">[解]首</rt></ruby>on'], ['komision', '<ruby>komision<rt class="ruby-L_L_L">(調査)委員会</rt></ruby>', '<ruby>komisi<rt class="ruby-M_M_M">(を)委託する</rt></ruby>on'], ['salon', '<ruby>salon<rt class="ruby-L_L_L">サロン</rt></ruby>', '<ruby>sal<rt class="ruby-X_X_X">塩</rt></ruby>on'], ['ponton', '<ruby>ponton<rt class="ruby-L_L_L">[軍]平底舟</rt></ruby>', '<ruby>pont<rt class="ruby-X_X_X">橋</rt></ruby>on'], ['koton', '<ruby>koton<rt class="ruby-X_X_X">綿</rt></ruby>', '<ruby>kot<rt class="ruby-X_X_X">泥</rt></ruby>on'], ['kripton', 'kripton', '<ruby>kript<rt class="ruby-M_M_M">[宗]地下聖堂</rt></ruby>on'], ['kupon', '<ruby>kupon<rt class="ruby-M_M_M">クーポン券</rt></ruby>', '<ruby>kup<rt class="ruby-M_M_M">吸い玉</rt></ruby>on'], ['lakon', 'lakon', '<ruby>lak<rt class="ruby-M_M_M">ラッカー</rt></ruby>on'], ['ludon', '<ruby>lu<rt class="ruby-S_S_S">賃借する</rt></ruby><ruby>don<rt class="ruby-M_M_M">与える</rt></ruby>', '<ruby>lud<rt class="ruby-M_M_M">(を)遊ぶ</rt></ruby>on'], ['melon', '<ruby>melon<rt class="ruby-M_M_M">[果]メロン</rt></ruby>', '<ruby>mel<rt class="ruby-M_M_M">アナグマ</rt></ruby>on'], ['menton', '<ruby>menton<rt class="ruby-L_L_L">[解]下あご</rt></ruby>', '<ruby>ment<rt class="ruby-M_M_M">[植]ハッカ</rt></ruby>on'], ['milion', '<ruby>milion<rt class="ruby-X_X_X">百万</rt></ruby>', '<ruby>mili<rt class="ruby-M_M_M">[植]キビ</rt></ruby>on'], ['milionon', '<ruby>milion<rt class="ruby-X_X_X">百万</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>milion<rt class="ruby-X_X_X">百万</rt></ruby>on'], ['nauxon', '<ruby>naux<rt class="ruby-X_X_X">九</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>naux<rt class="ruby-X_X_X">九</rt></ruby>on'], ['violon', '<ruby>violon<rt class="ruby-M_M_M">[楽]バイオリン</rt></ruby>', '<ruby>viol<rt class="ruby-M_M_M">[植]スミレ</rt></ruby>on'], ['refoj', '<ruby>re<rt class="ruby-M_M_M">再び</rt></ruby><ruby>foj<rt class="ruby-X_X_X">回</rt></ruby>', '<ruby>ref<rt class="ruby-M_M_M">リーフ</rt></ruby>oj'], ['trombon', '<ruby>trombon<rt class="ruby-M_M_M">[楽]トロンボーン</rt></ruby>', '<ruby>tromb<rt class="ruby-M_M_M">[気]たつまき</rt></ruby>on'], ['samo', 'samo', '<ruby>sam<rt class="ruby-M_M_M">同一の</rt></ruby>o'], ['savoj', 'savoj', '<ruby>sav<rt class="ruby-M_M_M">救助する</rt></ruby>oj'], ['senson', '<ruby>sen<rt class="ruby-S_S_S">(~)なしで</rt></ruby><ruby>son<rt class="ruby-M_M_M">音がする</rt></ruby>', '<ruby>sens<rt class="ruby-M_M_M">[生]感覚</rt></ruby>on'], ['sepon', '<ruby>sep<rt class="ruby-X_X_X">七</rt></ruby><ruby>on<rt class="ruby-M_M_M">分数</rt></ruby>', '<ruby>sep<rt class="ruby-X_X_X">七</rt></ruby>on'], ['skadron', 'skadron', '<ruby>skadr<rt class="ruby-M_M_M">[軍]騎兵中隊</rt></ruby>on'], ['stadion', '<ruby>stadion<rt class="ruby-L_L_L">スタジアム</rt></ruby>', '<ruby>stadi<rt class="ruby-X_X_X">段階</rt></ruby>on'], ['tetraon', 'tetraon', '<ruby>tetra<rt class="ruby-S_S_S">エゾライチョウ</rt></ruby>on'], ['timon', '<ruby>timon<rt class="ruby-L_L_L">かじ棒</rt></ruby>', '<ruby>tim<rt class="ruby-M_M_M">恐れる</rt></ruby>on'], ['valon', 'valon', '<ruby>val<rt class="ruby-M_M_M">[地]谷</rt></ruby>on'], ['veto', 'veto', '<ruby>vet<rt class="ruby-M_M_M">賭ける</rt></ruby>o']]
# overlap_6_b = [['dietan', '<ruby>diet<rt class="ruby-M_M_M">[医]規定食</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>diet<rt class="ruby-M_M_M">[医]規定食</rt></ruby>an'], ['afrikan', '<ruby>afrik<rt class="ruby-S_S_S">[地名]アフリカ</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>afrik<rt class="ruby-S_S_S">[地名]アフリカ</rt></ruby>an'], ['movadan', '<ruby>mov<rt class="ruby-M_M_M">動かす</rt></ruby><ruby>ad<rt class="ruby-S_S_S">継続行為</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>mov<rt class="ruby-M_M_M">動かす</rt></ruby><ruby>ad<rt class="ruby-S_S_S">継続行為</rt></ruby>an'], ['akcian', '<ruby>akci<rt class="ruby-M_M_M">[商]株式</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>akci<rt class="ruby-M_M_M">[商]株式</rt></ruby>an'], ['montaran', '<ruby>mont<rt class="ruby-X_X_X">山</rt></ruby><ruby>ar<rt class="ruby-M_M_M">集団</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>mont<rt class="ruby-X_X_X">山</rt></ruby><ruby>ar<rt class="ruby-M_M_M">集団</rt></ruby>an'], ['amerikan', '<ruby>amerik<rt class="ruby-M_M_M">[地名]アメリカ</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>amerik<rt class="ruby-M_M_M">[地名]アメリカ</rt></ruby>an'], ['regnan', '<ruby>regn<rt class="ruby-M_M_M">[法]国家</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>regn<rt class="ruby-M_M_M">[法]国家</rt></ruby>an'], ['dezertan', '<ruby>dezert<rt class="ruby-X_X_X">砂漠</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>dezert<rt class="ruby-X_X_X">砂漠</rt></ruby>an'], ['asocian', '<ruby>asoci<rt class="ruby-X_X_X">協会</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>asoci<rt class="ruby-X_X_X">協会</rt></ruby>an'], ['insulan', '<ruby>insul<rt class="ruby-X_X_X">島</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>insul<rt class="ruby-X_X_X">島</rt></ruby>an'], ['azian', '<ruby>azi<rt class="ruby-M_M_M">アジア</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>azi<rt class="ruby-M_M_M">アジア</rt></ruby>an'], ['sxtatan', '<ruby>sxtat<rt class="ruby-X_X_X">国家</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>sxtat<rt class="ruby-X_X_X">国家</rt></ruby>an'], ['doman', '<ruby>dom<rt class="ruby-X_X_X">家</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>dom<rt class="ruby-X_X_X">家</rt></ruby>an'], ['montan', '<ruby>mont<rt class="ruby-X_X_X">山</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>mont<rt class="ruby-X_X_X">山</rt></ruby>an'], ['familian', '<ruby>famili<rt class="ruby-X_X_X">家族</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>famili<rt class="ruby-X_X_X">家族</rt></ruby>an'], ['urban', '<ruby>urb<rt class="ruby-X_X_X">市</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>urb<rt class="ruby-X_X_X">市</rt></ruby>an'], ['inka', 'inka', '<ruby>ink<rt class="ruby-M_M_M">インク</rt></ruby>a'], ['popolan', '<ruby>popol<rt class="ruby-X_X_X">人民</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>popol<rt class="ruby-X_X_X">人民</rt></ruby>an'], ['dekan', '<ruby>dekan<rt class="ruby-L_L_L">学部長</rt></ruby>', '<ruby>dek<rt class="ruby-X_X_X">十</rt></ruby>an'], ['partian', '<ruby>parti<rt class="ruby-L_L_L">[政]党派</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>parti<rt class="ruby-L_L_L">[政]党派</rt></ruby>an'], ['lokan', '<ruby>lok<rt class="ruby-L_L_L">場所</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>lok<rt class="ruby-L_L_L">場所</rt></ruby>an'], ['sxipan', '<ruby>sxip<rt class="ruby-X_X_X">船</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>sxip<rt class="ruby-X_X_X">船</rt></ruby>an'], ['eklezian', '<ruby>eklezi<rt class="ruby-L_L_L">[宗]教会</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>eklezi<rt class="ruby-L_L_L">[宗]教会</rt></ruby>an'], ['landan', '<ruby>land<rt class="ruby-X_X_X">国</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>land<rt class="ruby-X_X_X">国</rt></ruby>an'], ['orientan', '<ruby>orient<rt class="ruby-M_M_M">方位定める;東</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>orient<rt class="ruby-M_M_M">方位定める;東</rt></ruby>an'], ['lernejan', '<ruby>lern<rt class="ruby-S_S_S">(を)学習する</rt></ruby><ruby>ej<rt class="ruby-M_M_M">場所</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>lern<rt class="ruby-S_S_S">(を)学習する</rt></ruby><ruby>ej<rt class="ruby-M_M_M">場所</rt></ruby>an'], ['enlandan', '<ruby>en<rt class="ruby-M_M_M">中で</rt></ruby><ruby>land<rt class="ruby-X_X_X">国</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>en<rt class="ruby-M_M_M">中で</rt></ruby><ruby>land<rt class="ruby-X_X_X">国</rt></ruby>an'], ['kalkan', '<ruby>kalkan<rt class="ruby-X_X_X">[解]踵</rt></ruby>', '<ruby>kalk<rt class="ruby-M_M_M">[化]石灰</rt></ruby>an'], ['estraran', '<ruby>estr<rt class="ruby-M_M_M">[接尾辞]長</rt></ruby><ruby>ar<rt class="ruby-M_M_M">集団</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>estr<rt class="ruby-M_M_M">[接尾辞]長</rt></ruby><ruby>ar<rt class="ruby-M_M_M">集団</rt></ruby>an'], ['etnan', '<ruby>etn<rt class="ruby-L_L_L">民族</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>etn<rt class="ruby-L_L_L">民族</rt></ruby>an'], ['euxropan', '<ruby>euxrop<rt class="ruby-L_L_L">ヨーロッパ</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>euxrop<rt class="ruby-L_L_L">ヨーロッパ</rt></ruby>an'], ['fazan', '<ruby>fazan<rt class="ruby-L_L_L">[鳥]キジ</rt></ruby>', '<ruby>faz<rt class="ruby-M_M_M">[理]位相</rt></ruby>an'], ['polican', '<ruby>polic<rt class="ruby-X_X_X">警察</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>polic<rt class="ruby-X_X_X">警察</rt></ruby>an'], ['socian', '<ruby>soci<rt class="ruby-X_X_X">社会</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>soci<rt class="ruby-X_X_X">社会</rt></ruby>an'], ['societan', '<ruby>societ<rt class="ruby-X_X_X">会</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>societ<rt class="ruby-X_X_X">会</rt></ruby>an'], ['grupan', '<ruby>grup<rt class="ruby-M_M_M">グループ</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>grup<rt class="ruby-M_M_M">グループ</rt></ruby>an'], ['havaj', 'havaj', '<ruby>hav<rt class="ruby-S_S_S">持っている</rt></ruby>aj'], ['ligan', '<ruby>lig<rt class="ruby-S_S_S">結ぶ;連盟</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>lig<rt class="ruby-S_S_S">結ぶ;連盟</rt></ruby>an'], ['nacian', '<ruby>naci<rt class="ruby-X_X_X">国民</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>naci<rt class="ruby-X_X_X">国民</rt></ruby>an'], ['koran', '<ruby>koran<rt class="ruby-M_M_M">[宗]コーラン</rt></ruby>', '<ruby>kor<rt class="ruby-X_X_X">心</rt></ruby>an'], ['religian', '<ruby>religi<rt class="ruby-X_X_X">宗教</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>religi<rt class="ruby-X_X_X">宗教</rt></ruby>an'], ['kuban', '<ruby>kub<rt class="ruby-M_M_M">立方体</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>kub<rt class="ruby-M_M_M">立方体</rt></ruby>an'], ['lama', '<ruby>lama<rt class="ruby-M_M_M">[宗]ラマ僧</rt></ruby>', '<ruby>lam<rt class="ruby-M_M_M">びっこの</rt></ruby>a'], ['majoran', '<ruby>major<rt class="ruby-M_M_M">[軍]陸軍少佐</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>major<rt class="ruby-M_M_M">[軍]陸軍少佐</rt></ruby>an'], ['malaj', 'malaj', '<ruby>mal<rt class="ruby-M_M_M">正反対</rt></ruby>aj'], ['marian', 'marian', '<ruby>mari<rt class="ruby-L_L_L">マリア</rt></ruby>an'], ['nordan', '<ruby>nord<rt class="ruby-X_X_X">北</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>nord<rt class="ruby-X_X_X">北</rt></ruby>an'], ['paran', 'paran', '<ruby>par<rt class="ruby-L_L_L">一対</rt></ruby>an'], ['parizan', '<ruby>pariz<rt class="ruby-M_M_M">[地名]パリ</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>pariz<rt class="ruby-M_M_M">[地名]パリ</rt></ruby>an'], ['parokan', '<ruby>parok<rt class="ruby-L_L_L">[宗]教区</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>parok<rt class="ruby-L_L_L">[宗]教区</rt></ruby>an'], ['podian', '<ruby>podi<rt class="ruby-L_L_L">ひな壇</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>podi<rt class="ruby-L_L_L">ひな壇</rt></ruby>an'], ['rusian', '<ruby>rus<rt class="ruby-M_M_M">ロシア人</rt></ruby>i<ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>rus<rt class="ruby-M_M_M">ロシア人</rt></ruby>ian'], ['satan', '<ruby>satan<rt class="ruby-M_M_M">[宗]サタン</rt></ruby>', '<ruby>sat<rt class="ruby-M_M_M">満腹した</rt></ruby>an'], ['sektan', '<ruby>sekt<rt class="ruby-M_M_M">[宗]宗派</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>sekt<rt class="ruby-M_M_M">[宗]宗派</rt></ruby>an'], ['senatan', '<ruby>senat<rt class="ruby-M_M_M">[政]参議院</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>senat<rt class="ruby-M_M_M">[政]参議院</rt></ruby>an'], ['skisman', '<ruby>skism<rt class="ruby-M_M_M">(団体の)分裂</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>skism<rt class="ruby-M_M_M">(団体の)分裂</rt></ruby>an'], ['sudan', 'sudan', '<ruby>sud<rt class="ruby-X_X_X">南</rt></ruby>an'], ['utopian', '<ruby>utopi<rt class="ruby-M_M_M">ユートピア</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>utopi<rt class="ruby-M_M_M">ユートピア</rt></ruby>an'], ['vilagxan', '<ruby>vilagx<rt class="ruby-X_X_X">村</rt></ruby><ruby>an<rt class="ruby-M_M_M">会員</rt></ruby>', '<ruby>vilagx<rt class="ruby-X_X_X">村</rt></ruby>an']]
# overlap_7_b = [['alte', '<ruby>alte<rt class="ruby-M_M_M">タチアオイ</rt></ruby>', '<ruby>alt<rt class="ruby-L_L_L">高い</rt></ruby>e'], ['apoge', '<ruby>apoge<rt class="ruby-M_M_M">[天]遠地点</rt></ruby>', '<ruby>apog<rt class="ruby-M_M_M">(を)支える</rt></ruby>e'], ['kaze', '<ruby>kaze<rt class="ruby-M_M_M">[化]凝乳</rt></ruby>', '<ruby>kaz<rt class="ruby-M_M_M">[文]格</rt></ruby>e'], ['pere', '<ruby>pere<rt class="ruby-M_M_M">破滅する</rt></ruby>', '<ruby>per<rt class="ruby-M_M_M">よって</rt></ruby>e'], ['kore', 'kore', '<ruby>kor<rt class="ruby-X_X_X">心</rt></ruby>e'], ['male', 'male', '<ruby>mal<rt class="ruby-M_M_M">正反対</rt></ruby>e'], ['sole', '<ruby>sole<rt class="ruby-M_M_M">シタビラメ</rt></ruby>', '<ruby>sol<rt class="ruby-M_M_M">唯一の</rt></ruby>e']]
# overlap_8_b = [['regulus', 'regulus', '<ruby>regul<rt class="ruby-X_X_X">規則</rt></ruby><ruby>us<rt class="ruby-S_S_S">条件法</rt></ruby>'], ['akirant', 'akirant', '<ruby>akir<rt class="ruby-S_S_S">(を)獲得する</rt></ruby><ruby>ant<rt class="ruby-S_S_S">能動;継続</rt></ruby>'], ['radius', 'radius', '<ruby>radi<rt class="ruby-L_L_L">[理]線</rt></ruby><ruby>us<rt class="ruby-S_S_S">条件法</rt></ruby>'], ['premis', '<ruby>premis<rt class="ruby-X_X_X">前提</rt></ruby>', '<ruby>prem<rt class="ruby-M_M_M">(を)押える</rt></ruby><ruby>is<rt class="ruby-S_S_S">過去形</rt></ruby>'], ['sonat', '<ruby>sonat<rt class="ruby-M_M_M">[楽]ソナタ</rt></ruby>', '<ruby>son<rt class="ruby-M_M_M">音がする</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['format', '<ruby>format<rt class="ruby-X_X_X">[印]判</rt></ruby>', '<ruby>form<rt class="ruby-X_X_X">形</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['markot', '<ruby>markot<rt class="ruby-L_L_L">[園]取木</rt></ruby>', '<ruby>mark<rt class="ruby-L_L_L">しるし</rt></ruby><ruby>ot<rt class="ruby-S_S_S">受動将然</rt></ruby>'], ['nomad', '<ruby>nomad<rt class="ruby-L_L_L">遊牧民</rt></ruby>', '<ruby>nom<rt class="ruby-L_L_L">名前</rt></ruby><ruby>ad<rt class="ruby-S_S_S">継続行為</rt></ruby>'], ['kantat', '<ruby>kantat<rt class="ruby-M_M_M">[楽]カンタータ</rt></ruby>', '<ruby>kant<rt class="ruby-M_M_M">(を)歌う</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['kolorad', 'kolorad', '<ruby>kolor<rt class="ruby-X_X_X">色</rt></ruby><ruby>ad<rt class="ruby-S_S_S">継続行為</rt></ruby>'], ['diplomat', '<ruby>diplomat<rt class="ruby-X_X_X">外交官</rt></ruby>', '<ruby>diplom<rt class="ruby-X_X_X">免状</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['diskont', '<ruby>diskont<rt class="ruby-M_M_M">[商]手形割引する</rt></ruby>', '<ruby>disk<rt class="ruby-X_X_X">円盤</rt></ruby><ruby>ont<rt class="ruby-S_S_S">能動;将然</rt></ruby>'], ['endos', 'endos', '<ruby>end<rt class="ruby-L_L_L">必要</rt></ruby><ruby>os<rt class="ruby-S_S_S">未来形</rt></ruby>'], ['esperant', '<ruby>esperant<rt class="ruby-L_L_L">エスペラント</rt></ruby>', '<ruby>esper<rt class="ruby-M_M_M">(を)希望する</rt></ruby><ruby>ant<rt class="ruby-S_S_S">能動;継続</rt></ruby>'], ['forkant', '<ruby>for<rt class="ruby-M_M_M">離れて</rt></ruby><ruby>kant<rt class="ruby-M_M_M">(を)歌う</rt></ruby>', '<ruby>fork<rt class="ruby-S_S_S">[料]フォーク</rt></ruby><ruby>ant<rt class="ruby-S_S_S">能動;継続</rt></ruby>'], ['gravit', 'gravit', '<ruby>grav<rt class="ruby-L_L_L">重要な</rt></ruby><ruby>it<rt class="ruby-S_S_S">受動完了</rt></ruby>'], ['konus', '<ruby>konus<rt class="ruby-L_L_L">[数]円錐</rt></ruby>', '<ruby>kon<rt class="ruby-S_S_S">知っている</rt></ruby><ruby>us<rt class="ruby-S_S_S">条件法</rt></ruby>'], ['salat', '<ruby>salat<rt class="ruby-M_M_M">[料]サラダ</rt></ruby>', '<ruby>sal<rt class="ruby-X_X_X">塩</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['legat', '<ruby>legat<rt class="ruby-M_M_M">[宗]教皇特使</rt></ruby>', '<ruby>leg<rt class="ruby-M_M_M">(を)読む</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['lekant', '<ruby>lekant<rt class="ruby-M_M_M">[植]マーガレット</rt></ruby>', '<ruby>lek<rt class="ruby-M_M_M">なめる</rt></ruby><ruby>ant<rt class="ruby-S_S_S">能動;継続</rt></ruby>'], ['lotus', '<ruby>lotus<rt class="ruby-L_L_L">[植]ハス</rt></ruby>', '<ruby>lot<rt class="ruby-L_L_L">くじ</rt></ruby><ruby>us<rt class="ruby-S_S_S">条件法</rt></ruby>'], ['malvolont', '<ruby>mal<rt class="ruby-M_M_M">正反対</rt></ruby><ruby>volont<rt class="ruby-L_L_L">自ら進んで</rt></ruby>', '<ruby>mal<rt class="ruby-M_M_M">正反対</rt></ruby><ruby>vol<rt class="ruby-S_S_S">意志がある</rt></ruby><ruby>ont<rt class="ruby-S_S_S">能動;将然</rt></ruby>'], ['mankis', '<ruby>man<rt class="ruby-X_X_X">手</rt></ruby><ruby>kis<rt class="ruby-M_M_M">キスする</rt></ruby>', '<ruby>mank<rt class="ruby-M_M_M">欠けている</rt></ruby><ruby>is<rt class="ruby-S_S_S">過去形</rt></ruby>'], ['minus', '<ruby>minus<rt class="ruby-L_L_L">マイナス</rt></ruby>', '<ruby>min<rt class="ruby-L_L_L">鉱山</rt></ruby><ruby>us<rt class="ruby-S_S_S">条件法</rt></ruby>'], ['patos', '<ruby>patos<rt class="ruby-M_M_M">[芸]パトス</rt></ruby>', '<ruby>pat<rt class="ruby-S_S_S">フライパン</rt></ruby><ruby>os<rt class="ruby-S_S_S">未来形</rt></ruby>'], ['predikat', '<ruby>predikat<rt class="ruby-X_X_X">[文]述部</rt></ruby>', '<ruby>predik<rt class="ruby-M_M_M">(を)説教する</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['rabat', '<ruby>rabat<rt class="ruby-L_L_L">[商]割引</rt></ruby>', '<ruby>rab<rt class="ruby-M_M_M">強奪する</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['rabot', '<ruby>rabot<rt class="ruby-S_S_S">かんなをかける</rt></ruby>', '<ruby>rab<rt class="ruby-M_M_M">強奪する</rt></ruby><ruby>ot<rt class="ruby-S_S_S">受動将然</rt></ruby>'], ['remont', 'remont', '<ruby>rem<rt class="ruby-L_L_L">漕ぐ</rt></ruby><ruby>ont<rt class="ruby-S_S_S">能動;将然</rt></ruby>'], ['satirus', 'satirus', '<ruby>satir<rt class="ruby-M_M_M">諷刺(詩;文)</rt></ruby><ruby>us<rt class="ruby-S_S_S">条件法</rt></ruby>'], ['sendat', '<ruby>sen<rt class="ruby-S_S_S">(~)なしで</rt></ruby><ruby>dat<rt class="ruby-L_L_L">日付</rt></ruby>', '<ruby>send<rt class="ruby-M_M_M">(を)送る</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['sendot', '<ruby>sen<rt class="ruby-S_S_S">(~)なしで</rt></ruby><ruby>dot<rt class="ruby-M_M_M">持参金</rt></ruby>', '<ruby>send<rt class="ruby-M_M_M">(を)送る</rt></ruby><ruby>ot<rt class="ruby-S_S_S">受動将然</rt></ruby>'], ['spirit', '<ruby>spirit<rt class="ruby-X_X_X">精神</rt></ruby>', '<ruby>spir<rt class="ruby-M_M_M">呼吸する</rt></ruby><ruby>it<rt class="ruby-S_S_S">受動完了</rt></ruby>'], ['spirant', 'spirant', '<ruby>spir<rt class="ruby-M_M_M">呼吸する</rt></ruby><ruby>ant<rt class="ruby-S_S_S">能動;継続</rt></ruby>'], ['taksus', '<ruby>taksus<rt class="ruby-L_L_L">[植]イチイ</rt></ruby>', '<ruby>taks<rt class="ruby-S_S_S">(を)評価する</rt></ruby><ruby>us<rt class="ruby-S_S_S">条件法</rt></ruby>'], ['tenis', 'tenis', '<ruby>ten<rt class="ruby-M_M_M">支え持つ</rt></ruby><ruby>is<rt class="ruby-S_S_S">過去形</rt></ruby>'], ['traktat', '<ruby>traktat<rt class="ruby-X_X_X">[政]条約</rt></ruby>', '<ruby>trakt<rt class="ruby-M_M_M">(を)取り扱う</rt></ruby><ruby>at<rt class="ruby-S_S_S">受動継続</rt></ruby>'], ['trikot', '<ruby>trikot<rt class="ruby-M_M_M">[織]トリコット</rt></ruby>', '<ruby>trik<rt class="ruby-S_S_S">編み物をする</rt></ruby><ruby>ot<rt class="ruby-S_S_S">受動将然</rt></ruby>'], ['trilit', '<ruby>tri<rt class="ruby-X_X_X">三</rt></ruby><ruby>lit<rt class="ruby-M_M_M">ベッド</rt></ruby>', '<ruby>tril<rt class="ruby-M_M_M">[楽]トリル</rt></ruby><ruby>it<rt class="ruby-S_S_S">受動完了</rt></ruby>'], ['vizit', '<ruby>vizit<rt class="ruby-M_M_M">(を)訪問する</rt></ruby>', '<ruby>viz<rt class="ruby-L_L_L">ビザ</rt></ruby><ruby>it<rt class="ruby-S_S_S">受動完了</rt></ruby>'], ['volont', '<ruby>volont<rt class="ruby-L_L_L">自ら進んで</rt></ruby>', '<ruby>vol<rt class="ruby-S_S_S">意志がある</rt></ruby><ruby>ont<rt class="ruby-S_S_S">能動;将然</rt></ruby>']]
# overlap_9_b = [['agxi', '<ruby>agxi<rt class="ruby-L_L_L">打ち歩</rt></ruby>', '<ruby>agx<rt class="ruby-L_L_L">年齢</rt></ruby>i'], ['premi', '<ruby>premi<rt class="ruby-X_X_X">賞品</rt></ruby>', '<ruby>prem<rt class="ruby-M_M_M">(を)押える</rt></ruby>i'], ['bari', 'bari', '<ruby>bar<rt class="ruby-L_L_L">障害</rt></ruby>i'], ['tempi', '<ruby>tempi<rt class="ruby-L_L_L">こめかみ</rt></ruby>', '<ruby>temp<rt class="ruby-X_X_X">時間</rt></ruby>i'], ['noktu', '<ruby>noktu<rt class="ruby-S_S_S">[鳥]コフクロウ</rt></ruby>', '<ruby>nokt<rt class="ruby-X_X_X">夜</rt></ruby>u'], ['vakcini', 'vakcini', '<ruby>vakcin<rt class="ruby-M_M_M">[薬]ワクチン</rt></ruby>i'], ['procesi', '<ruby>procesi<rt class="ruby-X_X_X">[宗]行列</rt></ruby>', '<ruby>proces<rt class="ruby-L_L_L">[法]訴訟</rt></ruby>i'], ['statu', '<ruby>statu<rt class="ruby-X_X_X">立像</rt></ruby>', '<ruby>stat<rt class="ruby-X_X_X">状態</rt></ruby>u'], ['devi', 'devi', '<ruby>dev<rt class="ruby-L_L_L">must</rt></ruby>i'], ['feri', '<ruby>feri<rt class="ruby-X_X_X">休日</rt></ruby>', '<ruby>fer<rt class="ruby-X_X_X">鉄</rt></ruby>i'], ['fleksi', '<ruby>fleksi<rt class="ruby-M_M_M">[文]語尾変化</rt></ruby>', '<ruby>fleks<rt class="ruby-M_M_M">(を)曲げる</rt></ruby>i'], ['pensi', '<ruby>pensi<rt class="ruby-X_X_X">年金</rt></ruby>', '<ruby>pens<rt class="ruby-X_X_X">思う</rt></ruby>i'], ['jesu', '<ruby>jesu<rt class="ruby-M_M_M">[宗]イエス</rt></ruby>', '<ruby>jes<rt class="ruby-L_L_L">はい</rt></ruby>u'], ['ĵaluzi', 'ĵaluzi', '<ruby>ĵaluz<rt class="ruby-L_L_L">嫉妬深い</rt></ruby>i'], ['konfesi', 'konfesi', '<ruby>konfes<rt class="ruby-M_M_M">(を)告白する</rt></ruby>i'], ['konsili', 'konsili', '<ruby>konsil<rt class="ruby-M_M_M">(を)助言する</rt></ruby>i'], ['legi', '<ruby>legi<rt class="ruby-M_M_M">[史]軍団</rt></ruby>', '<ruby>leg<rt class="ruby-M_M_M">(を)読む</rt></ruby>i'], ['licenci', 'licenci', '<ruby>licenc<rt class="ruby-L_L_L">[商]認可</rt></ruby>i'], ['logxi', '<ruby>logxi<rt class="ruby-L_L_L">[劇]桟敷</rt></ruby>', '<ruby>logx<rt class="ruby-M_M_M">(に)住む</rt></ruby>i'], ['meti', '<ruby>meti<rt class="ruby-L_L_L">手仕事</rt></ruby>', '<ruby>met<rt class="ruby-M_M_M">(を)置く</rt></ruby>i'], ['pasi', '<ruby>pasi<rt class="ruby-X_X_X">情熱</rt></ruby>', '<ruby>pas<rt class="ruby-M_M_M">通過する</rt></ruby>i'], ['revu', '<ruby>revu<rt class="ruby-M_M_M">専門雑誌</rt></ruby>', '<ruby>rev<rt class="ruby-M_M_M">空想する</rt></ruby>u'], ['rabi', '<ruby>rabi<rt class="ruby-M_M_M">[病]狂犬病</rt></ruby>', '<ruby>rab<rt class="ruby-M_M_M">強奪する</rt></ruby>i'], ['religi', '<ruby>religi<rt class="ruby-X_X_X">宗教</rt></ruby>', '<ruby>re<rt class="ruby-M_M_M">再び</rt></ruby><ruby>lig<rt class="ruby-S_S_S">結ぶ;連盟</rt></ruby>i'], ['sagu', '<ruby>sagu<rt class="ruby-M_M_M">[料]サゴ粉</rt></ruby>', '<ruby>sag<rt class="ruby-X_X_X">矢</rt></ruby>u'], ['sekci', '<ruby>sekci<rt class="ruby-X_X_X">部</rt></ruby>', '<ruby>sekc<rt class="ruby-S_S_S">[医]切断する</rt></ruby>i'], ['sendi', '<ruby>sen<rt class="ruby-S_S_S">(~)なしで</rt></ruby><ruby>di<rt class="ruby-X_X_X">神</rt></ruby>', '<ruby>send<rt class="ruby-M_M_M">(を)送る</rt></ruby>i'], ['teni', '<ruby>teni<rt class="ruby-M_M_M">サナダムシ</rt></ruby>', '<ruby>ten<rt class="ruby-M_M_M">支え持つ</rt></ruby>i'], ['vaku', 'vaku', '<ruby>vak<rt class="ruby-S_S_S">あいている</rt></ruby>u'], ['vizi', '<ruby>vizi<rt class="ruby-X_X_X">幻影</rt></ruby>', '<ruby>viz<rt class="ruby-L_L_L">ビザ</rt></ruby>i']]
# ===== 1つ目の Python 出力から得られた値 =====
overlap_1_a = [['buro', 'buro', 'buro'], ['haloo', 'haloo', 'haloo'], ['taŭro', 'taŭro', 'taŭro'], ['unesko', 'unesko', 'unesko']]
overlap_2_a = [['alo', 'aloアロエ', 'al~の方へo'], ['duon', 'du二on分数', 'du二on'], ['okon', 'ok八on分数', 'ok八on']]
overlap_2_2_a = [['sia', 'sia', 'si自分a'], ['eman', 'eman', 'em傾向an'], ['lian', 'lian[植]つる植物', 'li彼an'], ['pian', 'pian[楽]ピアノ', 'pi信心深いan']]
overlap_3_a = [['agat', 'agat[鉱]メノウ', 'ag行動するat受動継続'], ['agit', 'agit(を)扇動する', 'ag行動するit受動完了'], ['amas', 'amas集積;大衆', 'am愛するas現在形'], ['iris', 'iris[解]虹彩', 'ir行くis過去形'], ['irit', 'irit', 'ir行くit受動完了']]
overlap_4_a = [['aĝi', 'aĝi打ち歩', 'aĝ年齢i']]
overlap_5_a = [['nombron', 'nombr数on分数', 'nombr数on'], ['patron', 'patron後援者', 'patr父on'], ['karbon', 'karbon[化]炭素', 'karb炭on'], ['ciklon', 'ciklon低気圧', 'cikl周期on'], ['aldon', 'al~の方へdon与える', 'aldアルトon'], ['balon', 'balon気球', 'bal舞踏会on'], ['baron', 'baron男爵', 'bar障害on'], ['baston', 'baston棒', 'bast[植]じん皮on'], ['magneton', 'magnet[理]磁石on分数', 'magnet[理]磁石on'], ['beton', 'beton', 'betビートon'], ['bombon', 'bombonキャンデー', 'bomb爆弾on'], ['breton', 'breton', 'bret棚on'], ['burĝon', 'burĝon芽', 'burĝブルジョワon'], ['centon', 'cent百on分数', 'cent百on'], ['milon', 'mil千on分数', 'mil千on'], ['kanton', 'kanton(フランスの)郡', 'kant(を)歌うon'], ['citron', 'citron[果]シトロン', 'citr[楽]チターon'], ['platon', 'platon', 'plat平たいon'], ['dekon', 'dek十on分数', 'dek十on'], ['kvaron', 'kvar四on分数', 'kvar四on'], ['kvinon', 'kvin五on分数', 'kvin五on'], ['seson', 'ses六on分数', 'ses六on'], ['trion', 'tri三on分数', 'tri三on'], ['karton', 'karton厚紙', 'kartカードon'], ['foton', 'fot写真を撮るon分数', 'fot写真を撮るon'], ['peron', 'peron階段', 'perよってon'], ['elektron', 'elektr電気on分数', 'elektr電気on'], ['drakon', 'drakon', 'drak竜on'], ['mondon', 'mon金銭don与える', 'mond世界on'], ['pension', 'pension下宿屋', 'pensi年金on'], ['ordon', 'ordon(を)命令する', 'ord順序on'], ['eskadron', 'eskadron', 'eskadr[軍]艦隊on'], ['senton', 'sen(~)なしでton[楽]楽音', 'sent(を)感じるon'], ['eston', 'eston', 'est(~)であるon'], ['fanfaron', 'fanfaron大言壮語する', 'fanfar[楽]ファンファーレon'], ['fero', 'fero', 'fer鉄o'], ['feston', 'feston花綱', 'fest(を)祝うon'], ['flegmon', 'flegmon', 'flegm冷静on'], ['fronton', 'fronton[建]ペディメント', 'front正面on'], ['galon', 'galon[服]モール', 'gal[生]胆汁on'], ['mason', 'mason築く', 'masかたまりon'], ['helikon', 'helikon', 'helik[動]カタツムリon'], ['kanon', 'kanon[軍]大砲', 'kan[植]アシon'], ['kapon', 'kapon去勢オンドリ', 'kap頭on'], ['kokon', 'kokon[虫]繭(まゆ)', 'kokニワトリon'], ['kolon', 'kolon[建]円柱', 'kol[解]首on'], ['komision', 'komision(調査)委員会', 'komisi(を)委託するon'], ['salon', 'salonサロン', 'sal塩on'], ['ponton', 'ponton[軍]平底舟', 'pont橋on'], ['koton', 'koton綿', 'kot泥on'], ['kripton', 'kripton', 'kript[宗]地下聖堂on'], ['kupon', 'kuponクーポン券', 'kup吸い玉on'], ['lakon', 'lakon', 'lakラッカーon'], ['ludon', 'lu賃借するdon与える', 'lud(を)遊ぶon'], ['melon', 'melon[果]メロン', 'melアナグマon'], ['menton', 'menton[解]下あご', 'ment[植]ハッカon'], ['milion', 'milion百万', 'mili[植]キビon'], ['milionon', 'milion百万on分数', 'milion百万on'], ['naŭon', 'naŭ九on分数', 'naŭ九on'], ['violon', 'violon[楽]バイオリン', 'viol[植]スミレon'], ['refoj', 're再びfoj回', 'refリーフoj'], ['trombon', 'trombon[楽]トロンボーン', 'tromb[気]たつまきon'], ['samo', 'samo', 'sam同一のo'], ['savoj', 'savoj', 'sav救助するoj'], ['senson', 'sen(~)なしでson音がする', 'sens[生]感覚on'], ['sepon', 'sep七on分数', 'sep七on'], ['skadron', 'skadron', 'skadr[軍]騎兵中隊on'], ['stadion', 'stadionスタジアム', 'stadi段階on'], ['tetraon', 'tetraon', 'tetraエゾライチョウon'], ['timon', 'timonかじ棒', 'tim恐れるon'], ['valon', 'valon', 'val[地]谷on'], ['veto', 'veto', 'vet賭けるo']]
overlap_6_a = [['dietan', 'diet[医]規定食an会員', 'diet[医]規定食an'], ['afrikan', 'afrik[地名]アフリカan会員', 'afrik[地名]アフリカan'], ['movadan', 'mov動かすad継続行為an会員', 'mov動かすad継続行為an'], ['akcian', 'akci[商]株式an会員', 'akci[商]株式an'], ['montaran', 'mont山ar集団an会員', 'mont山ar集団an'], ['amerikan', 'amerik[地名]アメリカan会員', 'amerik[地名]アメリカan'], ['regnan', 'regn[法]国家an会員', 'regn[法]国家an'], ['dezertan', 'dezert砂漠an会員', 'dezert砂漠an'], ['arĝentan', 'arĝentan', 'arĝent銀an'], ['asocian', 'asoci協会an会員', 'asoci協会an'], ['insulan', 'insul島an会員', 'insul島an'], ['azian', 'aziアジアan会員', 'aziアジアan'], ['ŝtatan', 'ŝtat国家an会員', 'ŝtat国家an'], ['doman', 'dom家an会員', 'dom家an'], ['montan', 'mont山an会員', 'mont山an'], ['familian', 'famili家族an会員', 'famili家族an'], ['urban', 'urb市an会員', 'urb市an'], ['inka', 'inka', 'inkインクa'], ['popolan', 'popol人民an会員', 'popol人民an'], ['dekan', 'dekan学部長', 'dek十an'], ['partian', 'parti[政]党派an会員', 'parti[政]党派an'], ['lokan', 'lok場所an会員', 'lok場所an'], ['ŝipan', 'ŝip船an会員', 'ŝip船an'], ['eklezian', 'eklezi[宗]教会an会員', 'eklezi[宗]教会an'], ['landan', 'land国an会員', 'land国an'], ['orientan', 'orient方位定める;東an会員', 'orient方位定める;東an'], ['lernejan', 'lern(を)学習するej場所an会員', 'lern(を)学習するej場所an'], ['enlandan', 'en中でland国an会員', 'en中でland国an'], ['kalkan', 'kalkan[解]踵', 'kalk[化]石灰an'], ['estraran', 'estr[接尾辞]長ar集団an会員', 'estr[接尾辞]長ar集団an'], ['etnan', 'etn民族an会員', 'etn民族an'], ['eŭropan', 'eŭropヨーロッパan会員', 'eŭropヨーロッパan'], ['fazan', 'fazan[鳥]キジ', 'faz[理]位相an'], ['polican', 'polic警察an会員', 'polic警察an'], ['socian', 'soci社会an会員', 'soci社会an'], ['societan', 'societ会an会員', 'societ会an'], ['grupan', 'grupグループan会員', 'grupグループan'], ['havaj', 'havaj', 'hav持っているaj'], ['ligan', 'lig結ぶ;連盟an会員', 'lig結ぶ;連盟an'], ['nacian', 'naci国民an会員', 'naci国民an'], ['koran', 'koran[宗]コーラン', 'kor心an'], ['religian', 'religi宗教an会員', 'religi宗教an'], ['kuban', 'kub立方体an会員', 'kub立方体an'], ['lama', 'lama[宗]ラマ僧', 'lamびっこのa'], ['majoran', 'major[軍]陸軍少佐an会員', 'major[軍]陸軍少佐an'], ['malaj', 'malaj', 'mal正反対aj'], ['marian', 'marian', 'mariマリアan'], ['nordan', 'nord北an会員', 'nord北an'], ['paran', 'paran', 'par一対an'], ['parizan', 'pariz[地名]パリan会員', 'pariz[地名]パリan'], ['parokan', 'parok[宗]教区an会員', 'parok[宗]教区an'], ['podian', 'podiひな壇an会員', 'podiひな壇an'], ['rusian', 'rusロシア人ian会員', 'rusロシア人ian'], ['satan', 'satan[宗]サタン', 'sat満腹したan'], ['sektan', 'sekt[宗]宗派an会員', 'sekt[宗]宗派an'], ['senatan', 'senat[政]参議院an会員', 'senat[政]参議院an'], ['skisman', 'skism(団体の)分裂an会員', 'skism(団体の)分裂an'], ['sudan', 'sudan', 'sud南an'], ['utopian', 'utopiユートピアan会員', 'utopiユートピアan'], ['vilaĝan', 'vilaĝ村an会員', 'vilaĝ村an']]
overlap_7_a = [['alte', 'alteタチアオイ', 'alt高いe'], ['apoge', 'apoge[天]遠地点', 'apog(を)支えるe'], ['kaze', 'kaze[化]凝乳', 'kaz[文]格e'], ['pere', 'pere破滅する', 'perよってe'], ['kore', 'kore', 'kor心e'], ['male', 'male', 'mal正反対e'], ['sole', 'soleシタビラメ', 'sol唯一のe']]
overlap_8_a = [['regulus', 'regulus', 'regul規則us条件法'], ['akirant', 'akirant', 'akir(を)獲得するant能動;継続'], ['radius', 'radius', 'radi[理]線us条件法'], ['premis', 'premis前提', 'prem(を)押えるis過去形'], ['sonat', 'sonat[楽]ソナタ', 'son音がするat受動継続'], ['format', 'format[印]判', 'form形at受動継続'], ['markot', 'markot[園]取木', 'markしるしot受動将然'], ['nomad', 'nomad遊牧民', 'nom名前ad継続行為'], ['kantat', 'kantat[楽]カンタータ', 'kant(を)歌うat受動継続'], ['kolorad', 'kolorad', 'kolor色ad継続行為'], ['diplomat', 'diplomat外交官', 'diplom免状at受動継続'], ['diskont', 'diskont[商]手形割引する', 'disk円盤ont能動;将然'], ['endos', 'endos', 'end必要os未来形'], ['esperant', 'esperantエスペラント', 'esper(を)希望するant能動;継続'], ['forkant', 'for離れてkant(を)歌う', 'fork[料]フォークant能動;継続'], ['gravit', 'gravit', 'grav重要なit受動完了'], ['konus', 'konus[数]円錐', 'kon知っているus条件法'], ['salat', 'salat[料]サラダ', 'sal塩at受動継続'], ['legat', 'legat[宗]教皇特使', 'leg(を)読むat受動継続'], ['lekant', 'lekant[植]マーガレット', 'lekなめるant能動;継続'], ['lotus', 'lotus[植]ハス', 'lotくじus条件法'], ['malvolont', 'mal正反対volont自ら進んで', 'mal正反対vol意志があるont能動;将然'], ['mankis', 'man手kisキスする', 'mank欠けているis過去形'], ['minus', 'minusマイナス', 'min鉱山us条件法'], ['patos', 'patos[芸]パトス', 'patフライパンos未来形'], ['predikat', 'predikat[文]述部', 'predik(を)説教するat受動継続'], ['rabat', 'rabat[商]割引', 'rab強奪するat受動継続'], ['rabot', 'rabotかんなをかける', 'rab強奪するot受動将然'], ['remont', 'remont', 'rem漕ぐont能動;将然'], ['satirus', 'satirus', 'satir諷刺(詩;文)us条件法'], ['sendat', 'sen(~)なしでdat日付', 'send(を)送るat受動継続'], ['sendot', 'sen(~)なしでdot持参金', 'send(を)送るot受動将然'], ['spirit', 'spirit精神', 'spir呼吸するit受動完了'], ['spirant', 'spirant', 'spir呼吸するant能動;継続'], ['taksus', 'taksus[植]イチイ', 'taks(を)評価するus条件法'], ['tenis', 'tenis', 'ten支え持つis過去形'], ['traktat', 'traktat[政]条約', 'trakt(を)取り扱うat受動継続'], ['trikot', 'trikot[織]トリコット', 'trik編み物をするot受動将然'], ['trilit', 'tri三litベッド', 'tril[楽]トリルit受動完了'], ['vizit', 'vizit(を)訪問する', 'vizビザit受動完了'], ['volont', 'volont自ら進んで', 'vol意志があるont能動;将然']]
overlap_9_a = [['premi', 'premi賞品', 'prem(を)押えるi'], ['bari', 'bari', 'bar障害i'], ['tempi', 'tempiこめかみ', 'temp時間i'], ['noktu', 'noktu[鳥]コフクロウ', 'nokt夜u'], ['vakcini', 'vakcini', 'vakcin[薬]ワクチンi'], ['procesi', 'procesi[宗]行列', 'proces[法]訴訟i'], ['statu', 'statu立像', 'stat状態u'], ['devi', 'devi', 'devmusti'], ['feri', 'feri休日', 'fer鉄i'], ['fleksi', 'fleksi[文]語尾変化', 'fleks(を)曲げるi'], ['pensi', 'pensi年金', 'pens思うi'], ['jesu', 'jesu[宗]イエス', 'jesはいu'], ['konfesi', 'konfesi', 'konfes(を)告白するi'], ['konsili', 'konsili', 'konsil(を)助言するi'], ['legi', 'legi[史]軍団', 'leg(を)読むi'], ['licenci', 'licenci', 'licenc[商]認可i'], ['loĝi', 'loĝi[劇]桟敷', 'loĝ(に)住むi'], ['meti', 'meti手仕事', 'met(を)置くi'], ['pasi', 'pasi情熱', 'pas通過するi'], ['revu', 'revu専門雑誌', 'rev空想するu'], ['rabi', 'rabi[病]狂犬病', 'rab強奪するi'], ['religi', 'religi宗教', 're再びlig結ぶ;連盟i'], ['sagu', 'sagu[料]サゴ粉', 'sag矢u'], ['sekci', 'sekci部', 'sekc[医]切断するi'], ['sendi', 'sen(~)なしでdi神', 'send(を)送るi'], ['teni', 'teniサナダムシ', 'ten支え持つi'], ['vaku', 'vaku', 'vakあいているu'], ['vizi', 'vizi幻影', 'vizビザi']]

# ===== 2つ目の Python 出力から得られた値 =====
overlap_1_b =[['buro', 'buro', 'buro'], ['haloo', 'haloo', 'haloo'], ['taŭro', 'taŭro', 'taŭro'], ['unesko', 'unesko', 'unesko']]
overlap_2_b = [['alo', 'aloアロエ', 'al~の方へo'], ['duon', 'du二on分数', 'du二on'], ['okon', 'ok八on分数', 'ok八on']]
overlap_2_2_b = [['sia', 'sia', 'si自分a'], ['eman', 'eman', 'em傾向an'], ['lian', 'lian[植]つる植物', 'li彼an'], ['pian', 'pian[楽]ピアノ', 'pi信心深いan']]
overlap_3_b = [['agat', 'agat[鉱]メノウ', 'ag行動するat受動継続'], ['agit', 'agit(を)扇動する', 'ag行動するit受動完了'], ['amas', 'amas集積;大衆', 'am愛するas現在形'], ['iris', 'iris[解]虹彩', 'ir行くis過去形'], ['irit', 'irit', 'ir行くit受動完了']]
overlap_4_b = []
overlap_5_b = [['nombron', 'nombr数on分数', 'nombr数on'], ['patron', 'patron後援者', 'patr父on'], ['karbon', 'karbon[化]炭素', 'karb炭on'], ['ciklon', 'ciklon低気圧', 'cikl周期on'], ['aldon', 'al~の方へdon与える', 'aldアルトon'], ['balon', 'balon気球', 'bal舞踏会on'], ['baron', 'baron男爵', 'bar障害on'], ['baston', 'baston棒', 'bast[植]じん皮on'], ['magneton', 'magnet[理]磁石on分数', 'magnet[理]磁石on'], ['beton', 'beton', 'betビートon'], ['bombon', 'bombonキャンデー', 'bomb爆弾on'], ['breton', 'breton', 'bret棚on'], ['burĝon', 'burĝon芽', 'burĝブルジョワon'], ['centon', 'cent百on分数', 'cent百on'], ['milon', 'mil千on分数', 'mil千on'], ['kanton', 'kanton(フランスの)郡', 'kant(を)歌うon'], ['citron', 'citron[果]シトロン', 'citr[楽]チターon'], ['platon', 'platon', 'plat平たいon'], ['dekon', 'dek十on分数', 'dek十on'], ['kvaron', 'kvar四on分数', 'kvar四on'], ['kvinon', 'kvin五on分数', 'kvin五on'], ['seson', 'ses六on分数', 'ses六on'], ['trion', 'tri三on分数', 'tri三on'], ['karton', 'karton厚紙', 'kartカードon'], ['foton', 'fot写真を撮るon分数', 'fot写真を撮るon'], ['peron', 'peron階段', 'perよってon'], ['elektron', 'elektr電気on分数', 'elektr電気on'], ['drakon', 'drakon', 'drak竜on'], ['mondon', 'mon金銭don与える', 'mond世界on'], ['pension', 'pension下宿屋', 'pensi年金on'], ['ordon', 'ordon(を)命令する', 'ord順序on'], ['eskadron', 'eskadron', 'eskadr[軍]艦隊on'], ['senton', 'sen(~)なしでton[楽]楽音', 'sent(を)感じるon'], ['eston', 'eston', 'est(~)であるon'], ['fanfaron', 'fanfaron大言壮語する', 'fanfar[楽]ファンファーレon'], ['fero', 'fero', 'fer鉄o'], ['feston', 'feston花綱', 'fest(を)祝うon'], ['flegmon', 'flegmon', 'flegm冷静on'], ['fronton', 'fronton[建]ペディメント', 'front正面on'], ['galon', 'galon[服]モール', 'gal[生]胆汁on'], ['mason', 'mason築く', 'masかたまりon'], ['helikon', 'helikon', 'helik[動]カタツムリon'], ['kanon', 'kanon[軍]大砲', 'kan[植]アシon'], ['kapon', 'kapon去勢オンドリ', 'kap頭on'], ['kokon', 'kokon[虫]繭(まゆ)', 'kokニワトリon'], ['kolon', 'kolon[建]円柱', 'kol[解]首on'], ['komision', 'komision(調査)委員会', 'komisi(を)委託するon'], ['salon', 'salonサロン', 'sal塩on'], ['ponton', 'ponton[軍]平底舟', 'pont橋on'], ['koton', 'koton綿', 'kot泥on'], ['kripton', 'kripton', 'kript[宗]地下聖堂on'], ['kupon', 'kuponクーポン券', 'kup吸い玉on'], ['lakon', 'lakon', 'lakラッカーon'], ['ludon', 'lu賃借するdon与える', 'lud(を)遊ぶon'], ['melon', 'melon[果]メロン', 'melアナグマon'], ['menton', 'menton[解]下あご', 'ment[植]ハッカon'], ['milion', 'milion百万', 'mili[植]キビon'], ['milionon', 'milion百万on分数', 'milion百万on'], ['naŭon', 'naŭ九on分数', 'naŭ九on'], ['violon', 'violon[楽]バイオリン', 'viol[植]スミレon'], ['refoj', 're再びfoj回', 'refリーフoj'], ['trombon', 'trombon[楽]トロンボーン', 'tromb[気]たつまきon'], ['samo', 'samo', 'sam同一のo'], ['savoj', 'savoj', 'sav救助するoj'], ['senson', 'sen(~)なしでson音がする', 'sens[生]感覚on'], ['sepon', 'sep七on分数', 'sep七on'], ['skadron', 'skadron', 'skadr[軍]騎兵中隊on'], ['stadion', 'stadionスタジアム', 'stadi段階on'], ['tetraon', 'tetraon', 'tetraエゾライチョウon'], ['timon', 'timonかじ棒', 'tim恐れるon'], ['valon', 'valon', 'val[地]谷on'], ['veto', 'veto', 'vet賭けるo']]
overlap_6_b = [['dietan', 'diet[医]規定食an会員', 'diet[医]規定食an'], ['afrikan', 'afrik[地名]アフリカan会員', 'afrik[地名]アフリカan'], ['movadan', 'mov動かすad継続行為an会員', 'mov動かすad継続行為an'], ['akcian', 'akci[商]株式an会員', 'akci[商]株式an'], ['montaran', 'mont山ar集団an会員', 'mont山ar集団an'], ['amerikan', 'amerik[地名]アメリカan会員', 'amerik[地名]アメリカan'], ['regnan', 'regn[法]国家an会員', 'regn[法]国家an'], ['dezertan', 'dezert砂漠an会員', 'dezert砂漠an'], ['asocian', 'asoci協会an会員', 'asoci協会an'], ['insulan', 'insul島an会員', 'insul島an'], ['azian', 'aziアジアan会員', 'aziアジアan'], ['ŝtatan', 'ŝtat国家an会員', 'ŝtat国家an'], ['doman', 'dom家an会員', 'dom家an'], ['montan', 'mont山an会員', 'mont山an'], ['familian', 'famili家族an会員', 'famili家族an'], ['urban', 'urb市an会員', 'urb市an'], ['inka', 'inka', 'inkインクa'], ['popolan', 'popol人民an会員', 'popol人民an'], ['dekan', 'dekan学部長', 'dek十an'], ['partian', 'parti[政]党派an会員', 'parti[政]党派an'], ['lokan', 'lok場所an会員', 'lok場所an'], ['ŝipan', 'ŝip船an会員', 'ŝip船an'], ['eklezian', 'eklezi[宗]教会an会員', 'eklezi[宗]教会an'], ['landan', 'land国an会員', 'land国an'], ['orientan', 'orient方位定める;東an会員', 'orient方位定める;東an'], ['lernejan', 'lern(を)学習するej場所an会員', 'lern(を)学習するej場所an'], ['enlandan', 'en中でland国an会員', 'en中でland国an'], ['kalkan', 'kalkan[解]踵', 'kalk[化]石灰an'], ['estraran', 'estr[接尾辞]長ar集団an会員', 'estr[接尾辞]長ar集団an'], ['etnan', 'etn民族an会員', 'etn民族an'], ['eŭropan', 'eŭropヨーロッパan会員', 'eŭropヨーロッパan'], ['fazan', 'fazan[鳥]キジ', 'faz[理]位相an'], ['polican', 'polic警察an会員', 'polic警察an'], ['socian', 'soci社会an会員', 'soci社会an'], ['societan', 'societ会an会員', 'societ会an'], ['grupan', 'grupグループan会員', 'grupグループan'], ['havaj', 'havaj', 'hav持っているaj'], ['ligan', 'lig結ぶ;連盟an会員', 'lig結ぶ;連盟an'], ['nacian', 'naci国民an会員', 'naci国民an'], ['koran', 'koran[宗]コーラン', 'kor心an'], ['religian', 'religi宗教an会員', 'religi宗教an'], ['kuban', 'kub立方体an会員', 'kub立方体an'], ['lama', 'lama[宗]ラマ僧', 'lamびっこのa'], ['majoran', 'major[軍]陸軍少佐an会員', 'major[軍]陸軍少佐an'], ['malaj', 'malaj', 'mal正反対aj'], ['marian', 'marian', 'mariマリアan'], ['nordan', 'nord北an会員', 'nord北an'], ['paran', 'paran', 'par一対an'], ['parizan', 'pariz[地名]パリan会員', 'pariz[地名]パリan'], ['parokan', 'parok[宗]教区an会員', 'parok[宗]教区an'], ['podian', 'podiひな壇an会員', 'podiひな壇an'], ['rusian', 'rusロシア人ian会員', 'rusロシア人ian'], ['satan', 'satan[宗]サタン', 'sat満腹したan'], ['sektan', 'sekt[宗]宗派an会員', 'sekt[宗]宗派an'], ['senatan', 'senat[政]参議院an会員', 'senat[政]参議院an'], ['skisman', 'skism(団体の)分裂an会員', 'skism(団体の)分裂an'], ['sudan', 'sudan', 'sud南an'], ['utopian', 'utopiユートピアan会員', 'utopiユートピアan'], ['vilaĝan', 'vilaĝ村an会員', 'vilaĝ村an']]
overlap_7_b = [['alte', 'alteタチアオイ', 'alt高いe'], ['apoge', 'apoge[天]遠地点', 'apog(を)支えるe'], ['kaze', 'kaze[化]凝乳', 'kaz[文]格e'], ['pere', 'pere破滅する', 'perよってe'], ['kore', 'kore', 'kor心e'], ['male', 'male', 'mal正反対e'], ['sole', 'soleシタビラメ', 'sol唯一のe']]
overlap_8_b = [['regulus', 'regulus', 'regul規則us条件法'], ['akirant', 'akirant', 'akir(を)獲得するant能動;継続'], ['radius', 'radius', 'radi[理]線us条件法'], ['premis', 'premis前提', 'prem(を)押えるis過去形'], ['sonat', 'sonat[楽]ソナタ', 'son音がするat受動継続'], ['format', 'format[印]判', 'form形at受動継続'], ['markot', 'markot[園]取木', 'markしるしot受動将然'], ['nomad', 'nomad遊牧民', 'nom名前ad継続行為'], ['kantat', 'kantat[楽]カンタータ', 'kant(を)歌うat受動継続'], ['kolorad', 'kolorad', 'kolor色ad継続行為'], ['diplomat', 'diplomat外交官', 'diplom免状at受動継続'], ['diskont', 'diskont[商]手形割引する', 'disk円盤ont能動;将然'], ['endos', 'endos', 'end必要os未来形'], ['esperant', 'esperantエスペラント', 'esper(を)希望するant能動;継続'], ['forkant', 'for離れてkant(を)歌う', 'fork[料]フォークant能動;継続'], ['gravit', 'gravit', 'grav重要なit受動完了'], ['konus', 'konus[数]円錐', 'kon知っているus条件法'], ['salat', 'salat[料]サラダ', 'sal塩at受動継続'], ['legat', 'legat[宗]教皇特使', 'leg(を)読むat受動継続'], ['lekant', 'lekant[植]マーガレット', 'lekなめるant能動;継続'], ['lotus', 'lotus[植]ハス', 'lotくじus条件法'], ['malvolont', 'mal正反対volont自ら進んで', 'mal正反対vol意志があるont能動;将然'], ['mankis', 'man手kisキスする', 'mank欠けているis過去形'], ['minus', 'minusマイナス', 'min鉱山us条件法'], ['patos', 'patos[芸]パトス', 'patフライパンos未来形'], ['predikat', 'predikat[文]述部', 'predik(を)説教するat受動継続'], ['rabat', 'rabat[商]割引', 'rab強奪するat受動継続'], ['rabot', 'rabotかんなをかける', 'rab強奪するot受動将然'], ['remont', 'remont', 'rem漕ぐont能動;将然'], ['satirus', 'satirus', 'satir諷刺(詩;文)us条件法'], ['sendat', 'sen(~)なしでdat日付', 'send(を)送るat受動継続'], ['sendot', 'sen(~)なしでdot持参金', 'send(を)送るot受動将然'], ['spirit', 'spirit精神', 'spir呼吸するit受動完了'], ['spirant', 'spirant', 'spir呼吸するant能動;継続'], ['taksus', 'taksus[植]イチイ', 'taks(を)評価するus条件法'], ['tenis', 'tenis', 'ten支え持つis過去形'], ['traktat', 'traktat[政]条約', 'trakt(を)取り扱うat受動継続'], ['trikot', 'trikot[織]トリコット', 'trik編み物をするot受動将然'], ['trilit', 'tri三litベッド', 'tril[楽]トリルit受動完了'], ['vizit', 'vizit(を)訪問する', 'vizビザit受動完了'], ['volont', 'volont自ら進んで', 'vol意志があるont能動;将然']]
overlap_9_b = [['aĝi', 'aĝi打ち歩', 'aĝ年齢i'], ['premi', 'premi賞品', 'prem(を)押えるi'], ['bari', 'bari', 'bar障害i'], ['tempi', 'tempiこめかみ', 'temp時間i'], ['noktu', 'noktu[鳥]コフクロウ', 'nokt夜u'], ['vakcini', 'vakcini', 'vakcin[薬]ワクチンi'], ['procesi', 'procesi[宗]行列', 'proces[法]訴訟i'], ['statu', 'statu立像', 'stat状態u'], ['devi', 'devi', 'devmusti'], ['feri', 'feri休日', 'fer鉄i'], ['fleksi', 'fleksi[文]語尾変化', 'fleks(を)曲げるi'], ['pensi', 'pensi年金', 'pens思うi'], ['jesu', 'jesu[宗]イエス', 'jesはいu'], ['ĵaluzi', 'ĵaluzi', 'ĵaluz嫉妬深いi'], ['konfesi', 'konfesi', 'konfes(を)告白するi'], ['konsili', 'konsili', 'konsil(を)助言するi'], ['legi', 'legi[史]軍団', 'leg(を)読むi'], ['licenci', 'licenci', 'licenc[商]認可i'], ['loĝi', 'loĝi[劇]桟敷', 'loĝ(に)住むi'], ['meti', 'meti手仕事', 'met(を)置くi'], ['pasi', 'pasi情熱', 'pas通過するi'], ['revu', 'revu専門雑誌', 'rev空想するu'], ['rabi', 'rabi[病]狂犬病', 'rab強奪するi'], ['religi', 'religi宗教', 're再びlig結ぶ;連盟i'], ['sagu', 'sagu[料]サゴ粉', 'sag矢u'], ['sekci', 'sekci部', 'sekc[医]切断するi'], ['sendi', 'sen(~)なしでdi神', 'send(を)送るi'], ['teni', 'teniサナダムシ', 'ten支え持つi'], ['vaku', 'vaku', 'vakあいているu'], ['vizi', 'vizi幻影', 'vizビザi']]

# ------------------------------------------------
# 比較関数
# (前のアシスタント回答例と同じくサブリストを tuple 化して set 比較します)
# ------------------------------------------------
def compare_list_of_lists(list_a, list_b):
    """
    list_a, list_b ともに [['xxx','yyy'], ['zzz','www'], ...] の形式を想定。
    サブリストを tuple 化して set に入れ、差分を表示するための情報を返す。
    """
    set_a = set(tuple(sub) for sub in list_a)
    set_b = set(tuple(sub) for sub in list_b)
    
    only_in_a = set_a - set_b
    only_in_b = set_b - set_a
    
    result = {}
    if only_in_a:
        result['only_in_first'] = list(only_in_a)
    if only_in_b:
        result['only_in_second'] = list(only_in_b)
    
    return result

# ------------------------------------------------
# まとめて比較 & 出力
# ------------------------------------------------
def compare_all():
    print("=== overlap_1 ===")
    pprint(compare_list_of_lists(overlap_1_a, overlap_1_b))
    print()
    
    print("=== overlap_2 ===")
    pprint(compare_list_of_lists(overlap_2_a, overlap_2_b))
    print()
    
    print("=== overlap_2_2 ===")
    pprint(compare_list_of_lists(overlap_2_2_a, overlap_2_2_b))
    print()
    
    print("=== overlap_3 ===")
    pprint(compare_list_of_lists(overlap_3_a, overlap_3_b))
    print()
    
    print("=== overlap_4 ===")
    pprint(compare_list_of_lists(overlap_4_a, overlap_4_b))
    print()
    
    print("=== overlap_5 ===")
    pprint(compare_list_of_lists(overlap_5_a, overlap_5_b))
    print()
    
    print("=== overlap_6 ===")
    pprint(compare_list_of_lists(overlap_6_a, overlap_6_b))
    print()
    
    print("=== overlap_7 ===")
    pprint(compare_list_of_lists(overlap_7_a, overlap_7_b))
    print()
    
    print("=== overlap_8 ===")
    pprint(compare_list_of_lists(overlap_8_a, overlap_8_b))
    print()
    
    print("=== overlap_9 ===")
    pprint(compare_list_of_lists(overlap_9_a, overlap_9_b))
    print()

# -----------------------------
# 実行
# -----------------------------
# if __name__ == "__main__":
#     compare_all()


# In[54]:


# print(count_1,count_2,count_3,count_4)
# print(overlap_1)
# print(overlap_2)
# print(overlap_2_2)
# print(overlap_2_3)
# print(overlap_3)
# print(overlap_4)
# print(overlap_5)
# print(overlap_6)
# print(overlap_7)
# print(overlap_8)
# print(overlap_9)
# print(overlap_10)
# print(overlap_11)
# print(overlap_12)
# print(AN_treatment)
# print(len(overlap_1),len(overlap_2),len(overlap_2_2),len(overlap_3),len(overlap_4),len(overlap_5),len(overlap_6),len(overlap_7),len(overlap_8),len(overlap_9),len(AN_treatment))


# In[55]:


AN=[['dietan', '/diet/an/', '/diet/an'], ['afrikan', '/afrik/an/', '/afrik/an'], ['movadan', '/mov/ad/an/', '/mov/ad/an'], ['akcian', '/akci/an/', '/akci/an'], ['montaran', '/mont/ar/an/', '/mont/ar/an'], ['amerikan', '/amerik/an/', '/amerik/an'], ['regnan', '/regn/an/', '/regn/an'], ['dezertan', '/dezert/an/', '/dezert/an'], ['asocian', '/asoci/an/', '/asoci/an'], ['insulan', '/insul/an/', '/insul/an'], ['azian', '/azi/an/', '/azi/an'], ['ŝtatan', '/ŝtat/an/', '/ŝtat/an'], ['doman', '/dom/an/', '/dom/an'], ['montan', '/mont/an/', '/mont/an'], ['familian', '/famili/an/', '/famili/an'], ['urban', '/urb/an/', '/urb/an'], ['popolan', '/popol/an/', '/popol/an'], ['dekan', '/dekan/', '/dek/an'], ['partian', '/parti/an/', '/parti/an'], ['lokan', '/lok/an/', '/lok/an'], ['ŝipan', '/ŝip/an/', '/ŝip/an'], ['eklezian', '/eklezi/an/', '/eklezi/an'], ['landan', '/land/an/', '/land/an'], ['orientan', '/orient/an/', '/orient/an'], ['lernejan', '/lern/ej/an/', '/lern/ej/an'], ['enlandan', '/en/land/an/', '/en/land/an'], ['kalkan', '/kalkan/', '/kalk/an'], ['estraran', '/estr/ar/an/', '/estr/ar/an'], ['etnan', '/etn/an/', '/etn/an'], ['eŭropan', '/eŭrop/an/', '/eŭrop/an'], ['fazan', '/fazan/', '/faz/an'], ['polican', '/polic/an/', '/polic/an'], ['socian', '/soci/an/', '/soci/an'], ['societan', '/societ/an/', '/societ/an'], ['grupan', '/grup/an/', '/grup/an'], ['ligan', '/lig/an/', '/lig/an'], ['nacian', '/naci/an/', '/naci/an'], ['koran', '/koran/', '/kor/an'], ['religian', '/religi/an/', '/religi/an'], ['kuban', '/kub/an/', '/kub/an'], ['majoran', '/major/an/', '/major/an'], ['nordan', '/nord/an/', '/nord/an'], ['paran', 'paran', '/par/an'], ['parizan', '/pariz/an/', '/pariz/an'], ['parokan', '/parok/an/', '/parok/an'], ['podian', '/podi/an/', '/podi/an'], ['rusian', '/rus/i/an/', '/rus/ian'], ['satan', '/satan/', '/sat/an'], ['sektan', '/sekt/an/', '/sekt/an'], ['senatan', '/senat/an/', '/senat/an'], ['skisman', '/skism/an/', '/skism/an'], ['sudan', 'sudan', '/sud/an'], ['utopian', '/utopi/an/', '/utopi/an'], ['vilaĝan', '/vilaĝ/an/', '/vilaĝ/an'], ['arĝentan', '/arĝent/an/', '/arĝent/an']]
ON=[['duon', '/du/on/', '/du/on'], ['okon', '/ok/on/', '/ok/on'], ['nombron', '/nombr/on/', '/nombr/on'], ['patron', '/patron/', '/patr/on'], ['karbon', '/karbon/', '/karb/on'], ['ciklon', '/ciklon/', '/cikl/on'], ['aldon', '/al/don/', '/ald/on'], ['balon', '/balon/', '/bal/on'], ['baron', '/baron/', '/bar/on'], ['baston', '/baston/', '/bast/on'], ['magneton', '/magnet/on/', '/magnet/on'], ['beton', 'beton', '/bet/on'], ['bombon', '/bombon/', '/bomb/on'], ['breton', 'breton', '/bret/on'], ['burĝon', '/burĝon/', '/burĝ/on'], ['centon', '/cent/on/', '/cent/on'], ['milon', '/mil/on/', '/mil/on'], ['kanton', '/kanton/', '/kant/on'], ['citron', '/citron/', '/citr/on'], ['platon', 'platon', '/plat/on'], ['dekon', '/dek/on/', '/dek/on'], ['kvaron', '/kvar/on/', '/kvar/on'], ['kvinon', '/kvin/on/', '/kvin/on'], ['seson', '/ses/on/', '/ses/on'], ['trion', '/tri/on/', '/tri/on'], ['karton', '/karton/', '/kart/on'], ['foton', '/fot/on/', '/fot/on'], ['peron', '/peron/', '/per/on'], ['elektron', '/elektr/on/', '/elektr/on'], ['drakon', 'drakon', '/drak/on'], ['mondon', '/mon/don/', '/mond/on'], ['pension', '/pension/', '/pensi/on'], ['ordon', '/ordon/', '/ord/on'], ['eskadron', 'eskadron', '/eskadr/on'], ['senton', '/sen/ton/', '/sent/on'], ['eston', 'eston', '/est/on'], ['fanfaron', '/fanfaron/', '/fanfar/on'], ['feston', '/feston/', '/fest/on'], ['flegmon', 'flegmon', '/flegm/on'], ['fronton', '/fronton/', '/front/on'], ['galon', '/galon/', '/gal/on'], ['mason', '/mason/', '/mas/on'], ['helikon', 'helikon', '/helik/on'], ['kanon', '/kanon/', '/kan/on'], ['kapon', '/kapon/', '/kap/on'], ['kokon', '/kokon/', '/kok/on'], ['kolon', '/kolon/', '/kol/on'], ['komision', '/komision/', '/komisi/on'], ['salon', '/salon/', '/sal/on'], ['ponton', '/ponton/', '/pont/on'], ['koton', '/koton/', '/kot/on'], ['kripton', 'kripton', '/kript/on'], ['kupon', '/kupon/', '/kup/on'], ['lakon', 'lakon', '/lak/on'], ['ludon', '/lu/don/', '/lud/on'], ['melon', '/melon/', '/mel/on'], ['menton', '/menton/', '/ment/on'], ['milion', '/milion/', '/mili/on'], ['milionon', '/milion/on/', '/milion/on'], ['naŭon', '/naŭ/on/', '/naŭ/on'], ['violon', '/violon/', '/viol/on'], ['trombon', '/trombon/', '/tromb/on'], ['senson', '/sen/son/', '/sens/on'], ['sepon', '/sep/on/', '/sep/on'], ['skadron', 'skadron', '/skadr/on'], ['stadion', '/stadion/', '/stadi/on'], ['tetraon', 'tetraon', '/tetra/on'], ['timon', '/timon/', '/tim/on'], ['valon', 'valon', '/val/on']]


# In[56]:


import re
for an in AN:
    if an[1].endswith("/an/"):
        i2=an[1]
        i3 = re.sub(r"/an/$", "", i2)# 正規表現を使わないと、etn/a/n　において、etnのnまで削られてしまった。　ここの$は末尾を表す正規表現なので要注意。
        i4=i3+"/an/o"
        i5=i3+"/an/a"
        i6=i3+"/an/e"
        i7=i3+"/a/n/"
        pre_replacements_dict_3[i4.replace('/', '')]=[safe_replace(i4,temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i4.replace('/', ''))-1)*10000+3000]
        pre_replacements_dict_3[i5.replace('/', '')]=[safe_replace(i5,temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i5.replace('/', ''))-1)*10000+3000]
        pre_replacements_dict_3[i6.replace('/', '')]=[safe_replace(i6,temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i6.replace('/', ''))-1)*10000+3000]
        pre_replacements_dict_3[i7.replace('/', '')]=[safe_replace(i7,temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i7.replace('/', ''))-1)*10000+3000]
        # print(i4,i7)
    else:
        i2=an[1]
        i2_2 = re.sub(r"an$", "", i2)
        i3 = re.sub(r"an/$", "", i2_2)
        i4=i3+"an/o"
        i5=i3+"an/a"
        i6=i3+"an/e"
        i7=i3+"/a/n/"
        pre_replacements_dict_3[i4.replace('/', '')]=[safe_replace(i4,temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i4.replace('/', ''))-1)*10000+3000]
        pre_replacements_dict_3[i5.replace('/', '')]=[safe_replace(i5,temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i5.replace('/', ''))-1)*10000+3000]
        pre_replacements_dict_3[i6.replace('/', '')]=[safe_replace(i6,temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i6.replace('/', ''))-1)*10000+3000]
        pre_replacements_dict_3[i7.replace('/', '')]=[safe_replace(i7,temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i7.replace('/', ''))-1)*10000+3000]
        # print(i5,i7)


# In[57]:


for on in ON:
    if on[1].endswith("/on/"):
        i2=on[1]
        i3 = re.sub(r"/on/$", "", i2)# 正規表現を使わないと、etn/a/n　において、etnのnまで削られてしまった。　ここの$は末尾を表す正規表現なので要注意。
        i4=i3+"/on/o"
        i5=i3+"/on/a"
        i6=i3+"/on/e"
        i7=i3+"/o/n/"
        pre_replacements_dict_3[i4.replace('/', '')]=[safe_replace(i4,temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i4.replace('/', ''))-1)*10000+3000]
        pre_replacements_dict_3[i5.replace('/', '')]=[safe_replace(i5,temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i5.replace('/', ''))-1)*10000+3000]
        pre_replacements_dict_3[i6.replace('/', '')]=[safe_replace(i6,temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i6.replace('/', ''))-1)*10000+3000]
        pre_replacements_dict_3[i7.replace('/', '')]=[safe_replace(i7,temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i7.replace('/', ''))-1)*10000+3000]
        # print(i4,i7)
    else:
        i2=on[1]
        i2_2 = re.sub(r"on$", "", i2)
        i3 = re.sub(r"on/$", "", i2_2)
        i4=i3+"on/o"
        i5=i3+"on/a"
        i6=i3+"on/e"
        i7=i3+"/o/n/"
        pre_replacements_dict_3[i4.replace('/', '')]=[safe_replace(i4,temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i4.replace('/', ''))-1)*10000+3000]
        pre_replacements_dict_3[i5.replace('/', '')]=[safe_replace(i5,temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i5.replace('/', ''))-1)*10000+3000]
        pre_replacements_dict_3[i6.replace('/', '')]=[safe_replace(i6,temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i6.replace('/', ''))-1)*10000+3000]
        pre_replacements_dict_3[i7.replace('/', '')]=[safe_replace(i7,temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i7.replace('/', ''))-1)*10000+3000]
        # print(i5,i7)


# In[58]:


# ⇓下記の処理については、1つ下のセルで外部ファイルを読み込む形式に変えた。行われている処理は全く同じである。
# # pre_replacements_dict_3の編集

# newly_defined_word_root_decomposition_list=["vi/n","li/n","si/n","mi/n","ĝi/n","ni/n","ili/n"]# 202412変更
# for i in newly_defined_word_root_decomposition_list:
#     pre_replacements_dict_3[i.replace('/', '')]=[safe_replace(i,temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i.replace('/', ''))-1)*10000+3000]# これらについては数字の大きさはそこまで重要ではない

# # x='mond/o/n'  (例)　後でもやっている
# # pre_replacements_dict_3[x.replace('/', '')]=[safe_replace(x,temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),  (len(x.replace('/', ''))-1)*10000+3000]
# pre_replacements_dict_3['fariĝ'][1]=len('fariĝ')*10000+27500# 優先順位だけ変更

# # 正しく語根分解・文字列(漢字)置換してほしいやつ  anとenは念の為a/n/,e/n/としておく。ant,int,ontは大丈夫  空白を使うのは最終手段。  ","は絶対に使っては駄目
# y1=[["alt/e",33000],["apog/e",43000],["kaz/e/ ",43000],["per/e/",33000],["kor/e/",33000],["mal/e/",33000],["sol/e/",33000],["fer/o",33000],["ref/oj",43000],['sam/o',33000],
#     ['sav/oj',43000],['vet/o',33000],["ink/a",33000],["mal/aj",43000],["hav/aj",43000],["lam/a",33000],
#     ["form/at",53000],["mark/ot",53000],["kant/at",53000],["diplomat",73000],["diskont",63000],["end/os",43000],["for/kant",53000],["kon/us",43000],["salat",43000],["leg/at",43000],["lek/ant",53000],
#     ["lot/us",43000],["mal/volont",83000],["mank/is",53000],["minus",43000],["pat/os",43000],["rabat",43000],["rabot",43000],["rem/ont",53000],
#     ["satir/us",63000],["send/at",53000],["send/ot",53000],["spirit",53000],
#     ["spir/ant",63000],["taks/us",53000],["ten/is",43000],["trakt/at",63000],["trikot",53000],["trilit",53000],["vizit",43000],["volont",53000],
#     ["dom/e/n",43000],["ter/e/n",43000],["post/e/n",53000],["posten/ul",73000],["ordin/at",63000],['gvid/ant/o',73000],['am/as',33000]
#     ]# ["pi/a/n",38000] anをa/n/で分けるのは正しくはないが。  havaj "pi/a/n"だけ8000に
# for i in y1:
#     pre_replacements_dict_3[i[0].replace('/', '')]=[safe_replace(i[0],temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), i[1]]

# # on系の調節(an系は現時点で調節必要なし) 空白を使うのは最終手段であり、稀にしか出てこなさそうなやつに対してのみ。  ","は絶対に使っては駄目   "duon","okon"だけ8000に ??(24/12)
# y1=[['du/on',38000],['tri/on',43000],["kvar/on",53000],["kvin/on",53000],["ses/on",43000],["baston",53000],["bast/o/n ",63000],["beton",43000],["bet/o/n ",53000],["burĝon",63000],["burĝ/o/n ",73000],
#     ["sep/on",43000],["ok/on",38000],["naŭ/on",53000],["dek/on",43000],["al/don",43000],["ald/o/n ",53000],["cent/on",53000],["mil/on",43000],["citron",53000],["citr/o/n ",63000],["elektr/on",73000],["elektr/o/n ",83000],
#     ["mond/o/n",53000],["sent/o/n",53000],["fanfaron",73000],["fanfar/o/n ",83000],["galon",43000],["gal/o/n/ ",53000],["kanon",43000],["kan/o/n ",53000],["lud/o/n",43000],["milion/on",73000],["milion",53000],
#     ["melon",43000],["mel/o/n ",53000],["sens/o/n",53000]]# kapon,kupon,mentonの修正は辞めにした。
# for i in y1:
#     pre_replacements_dict_3[i[0].replace('/', '')]=[safe_replace(i[0],temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), i[1]]
    
# # /o,/a,/eの追加
# y1=[["pian",33000],["amas",33000],["apoge",43000],["kore",43000],["male",33000],["fero",33000],["re/foj",43000],["samo",33000],["savoj",43000],["malaj",43000],["havaj",43000],
#     ["premis",53000], ['markot',53000],["diplomat",73000],["gravit",53000],["konus",43000],["mal/volont",83000],['patos',43000],["sen/dat",53000],["sen/dot",53000],["tenis",43000],["volont",53000],['domen',43000],['teren',43000],["posten",53000],
#     ["procesi",63000],["devi",33000],["feri",33000],["pasi",33000],["revu",33000],["rabi",33000],["religi",53000],["sen/di",43000],["vaku",33000]]# ["pi/a/n",38000] anをa/n/で分けるのは正しくはないが。  havaj
# for i in y1:
#     pre_replacements_dict_3[(i[0]+'/a').replace('/', '')]=[safe_replace((i[0]+'/a'),temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), i[1]+10000]
#     pre_replacements_dict_3[(i[0]+'/e').replace('/', '')]=[safe_replace((i[0]+'/e'),temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), i[1]+10000]
#     pre_replacements_dict_3[(i[0]+'/o').replace('/', '')]=[safe_replace((i[0]+'/o'),temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), i[1]+10000]

# # /o,/aの追加
# y1=[["eman",33000],["lian",33000],["iris",33000],["alte",33000],["kaze",33000],['pere',33000],['sole',33000],["veto",33000],['inka',33000],["lama",33000],
#     ["regulus",63000],["radius",53000],["nomad",43000],["kolorad",63000],["endos",43000],["esperant",73000],["lotus",43000],["man/kis",33000],["remont",53000],['satirus',63000],
#     ["taksus",53000], ['ordinat',63000], ['aĝi',33000], ['premi',43000], ['bari',33000], ['tempi',43000], ['noktu',43000], ['vakcini',43000], ['statu',43000], ['fleksi',53000],
#     ["pensi",43000],["jesu",33000],["ĵaluzi",63000],["konfesi",63000],["konsili",63000],["legi",33000],["licenci",63000],["loĝi",43000],["meti",33000],["sagu",33000],["sekci",43000],["teni",33000],["vizi",33000],
#     ["aĝ/i", 23000]# ["pi/a/n",38000] anをa/n/で分けるのは正しくはないが。  havaj
# for i in y1:
#     pre_replacements_dict_3[(i[0]+'/a').replace('/', '')]=[safe_replace((i[0]+'/a'),temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), i[1]+10000]
#     pre_replacements_dict_3[(i[0]+'/o').replace('/', '')]=[safe_replace((i[0]+'/o'),temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), i[1]+10000]

# # /oの追加
# y1=[["agat",33000],["akirant",63000],["sonat",43000],["format",53000],["kantat",53000],["legat",43000],["lekant",53000],["predikat",73000],['spirant',63000],["traktat",63000]]# ["pi/a/n",38000] anをa/n/で分けるのは正しくはないが。  havaj
# for i in y1:
#     pre_replacements_dict_3[(i[0]+'/o').replace('/', '')]=[safe_replace((i[0]+'/o'),temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), i[1]+10000]

# # 動詞語尾の追加
# y1=[["sen/son/",53000],["irit",33000],["agit",33000],["markot",53000],["nom/ad",43000],["kolor/ad",63000], ["endos",43000],["man/kis",33000],["remont",53000],["premi",53000],["procesi",63000]
#     ,["devi",33000],["posten",53000],["dat/um/",43000],["tra/met/",53000]]
# for i in y1:
#     for k1,k2 in verb_suffix_2l_2.items():
#         pre_replacements_dict_3[(i[0]+k1).replace('/', '')]=[safe_replace(i[0],temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>")+k2, i[1]+len(k1)*10000]
# y1=[["sen/son/",53000],["irit",33000],["agit",33000],["markot",53000],["nom/ad",43000],["kolor/ad",63000], ["endos",43000],["man/kis",33000],["remont",53000],["premi",53000],["procesi",63000]
#     ,["devi",33000],["posten",53000],["dat/um/",43000],["tra/met/",53000]]
# for i in y1:
#     for k in ["u ","i ","u","i"]:
#         pre_replacements_dict_3[(i[0]+k).replace('/', '')]=[safe_replace(i[0],temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>")+k, i[1]+len(k)*10000]

# # 以下は完全手作業
# pre_replacements_dict_3['dat/um/i'.replace('/', '')]=[safe_replace('dat/um/i',temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),  len('dat/um/i'.replace('/', ''))*10000+3000]
# pre_replacements_dict_3['dat/um/u'.replace('/', '')]=[safe_replace('dat/um/u',temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),  len('dat/um/u'.replace('/', ''))*10000+3000]
# # dat/um/u  dat/um/u!
# pre_replacements_dict_3['tra/met/i'.replace('/', '')]=[safe_replace('tra/met/i',temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),  len('tra/met/i'.replace('/', ''))*10000+3000]
# pre_replacements_dict_3['tra/met/u'.replace('/', '')]=[safe_replace('tra/met/u',temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),  len('tra/met/u'.replace('/', ''))*10000+3000]


# In[59]:


# pre_replacements_dict_3={}
# # 上のセルでの処理を外部ファイルを読み込む形式に変えた。行われている処理は全く同じである。
# with open("世界语单词词根分解法user设置.json", "r", encoding="utf-8") as g:
#     change_dec = json.load(g)
# for i in change_dec:
#     if len(i)==3:
#         try:
#             if i[1]==0:
#                 num_char_or=len(i[0].replace('/', ''))*10000
#             else:
#                 num_char_or=i[1]
#             if "动词词尾1" in i[2]:
#                 for k1,k2 in verb_suffix_2l_2.items():
#                     pre_replacements_dict_3[(i[0]+k1).replace('/', '')]=[safe_replace(i[0],temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>")+k2, num_char_or+len(k1)*10000]
#                 i[2].remove("动词词尾1")#　これがあるので、繰り返しには要注意!
#             if "动词词尾2" in i[2]:
#                 for k in ["u ","i ","u","i"]:
#                     pre_replacements_dict_3[(i[0]+k).replace('/', '')]=[safe_replace(i[0],temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>")+k, num_char_or+len(k)*10000]
#                 i[2].remove("动词词尾2")
#             if len(i[2])>=1:
#                 for j in i[2]:
#                     pre_replacements_dict_3[(i[0]+'/'+j).replace('/', '')]=[safe_replace((i[0]+'/'+j),temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), num_char_or+len(j)*10000]
#             else:
#                 pre_replacements_dict_3[i[0].replace('/', '')]=[safe_replace(i[0],temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), num_char_or]
#         except:
#             continue

# pre_replacements_dict_3


# In[ ]:


# 上のセルでの処理を外部ファイルを読み込む形式に変えた。行われている処理は全く同じである。
with open("世界语单词词根分解法user设置.json", "r", encoding="utf-8") as g:
    change_dec = json.load(g)
for i in change_dec:
    if len(i)==3:
        try:
            esperanto_Word_before_replacement = i[0].replace('/', '')
            if i[1]=="dflt":
                num_char_or=len(esperanto_Word_before_replacement)*10000
            else:
                num_char_or=i[1]
                
            Replaced_String = safe_replace(i[0],temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>")
            if "NE" in i[2]:
                pre_replacements_dict_3[esperanto_Word_before_replacement]=[Replaced_String, num_char_or]
                i[2].remove("NE")#　これがあるので、繰り返しには要注意!
            if "Verbo_S1" in i[2]:
                for k1,k2 in verb_suffix_2l_2.items():
                    pre_replacements_dict_3[esperanto_Word_before_replacement + k1]=[Replaced_String+k2, num_char_or+len(k1)*10000]
                i[2].remove("Verbo_S1")
            if "Verbo_S2" in i[2]:
                for k in ["u ","i ","u","i"]:
                    pre_replacements_dict_3[esperanto_Word_before_replacement + k]=[Replaced_String+k, num_char_or+len(k)*10000]
                i[2].remove("Verbo_S2")
            if len(i[2])>=1:
                for j in i[2]:
                    j2 = j.replace('/', '')
                    j3 = safe_replace(j,temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>")
                    pre_replacements_dict_3[esperanto_Word_before_replacement + j2]=[Replaced_String + j3, num_char_or+len(j2)*10000]
            else:
                pre_replacements_dict_3[esperanto_Word_before_replacement]=[Replaced_String, num_char_or]
        except:
            continue

pre_replacements_dict_3


# In[61]:


with open("替换后文字列(汉字)_user设置(基本上完全不推荐).json", "r", encoding="utf-8") as g:
    change_dec = json.load(g)
for i in change_dec:
    if len(i)==4:
        esperanto_Roots_before_replacement = i[0].strip('/').split('/')
        replaced_roots = i[3].strip('/').split('/')
        if len(esperanto_Roots_before_replacement) == len(replaced_roots):
            # try:
            Replaced_String = ""
            for kk in range(len(esperanto_Roots_before_replacement)):
                Replaced_String += output_format(esperanto_Roots_before_replacement[kk],replaced_roots[kk], format_type)
            
            esperanto_Word_before_replacement = i[0].replace('/', '')
            if i[1]=="dflt":
                num_char_or=len(esperanto_Word_before_replacement)*10000
            else:
                num_char_or=i[1]
            if "NE" in i[2]:
                pre_replacements_dict_3[esperanto_Word_before_replacement]=[Replaced_String, num_char_or]
                i[2].remove("NE")#　これがあるので、繰り返しには要注意!
            if "Verbo_S1" in i[2]:
                for k1,k2 in verb_suffix_2l_2.items():
                    pre_replacements_dict_3[esperanto_Word_before_replacement + k1]=[Replaced_String+k2, num_char_or+len(k1)*10000]
                i[2].remove("Verbo_S1")#　これがあるので、繰り返しには要注意!
            if "Verbo_S2" in i[2]:
                for k in ["u ","i ","u","i"]:
                    pre_replacements_dict_3[esperanto_Word_before_replacement + k]=[Replaced_String+k, num_char_or+len(k)*10000]
                i[2].remove("Verbo_S2")
            if len(i[2])>=1:
                for j in i[2]:
                    j2 = j.replace('/', '')
                    j3 = safe_replace(j,temporary_replacements_list_final).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>")
                    pre_replacements_dict_3[esperanto_Word_before_replacement + j2]=[Replaced_String + j3, num_char_or+len(j2)*10000]
            else:
                pre_replacements_dict_3[esperanto_Word_before_replacement]=[Replaced_String, num_char_or]
            # except:
            #     continue

pre_replacements_dict_3


# In[62]:


check_list=['agitas','agit','irit','iritis','iritant','aĝi','arĝentan','arĝentane','ĵaluzia']
for i in check_list:
    print(pre_replacements_dict_3[i])


# In[63]:


check_list = [" fea","sudana","bretona",
    "dekano", "satano", "satana", "etnan", "satan","etnano", "domen", "teren", "domene", "terene","posten", "posten", "postene", "postenas", "postenos",
    "senson", "sensone", "sensona", "postenas", "postenos","parano", "parana", "satan", "ordoni","mondon", "pensiono", "senton", "ordon","drakon", "drakono", "elektron ", "perono",
    "foton", "karton", "platone", "citron ","milion", "milon", "centon", "burĝon","bombone", "aldon ", "aldoni", "ciklon","ciklone", "karbon", "karbone", "patron","gvidanto", "amas", "koran", "lian",
    "inka", "posten", "pere", "fero","korano", "kore", "malaj", "male", "paran", "samo","satan", "savoj", "sudan", "mankis", "iris", "regulus","akirant", "sendate", "mankisa", "kolorad", "iris", "reguluso",
    "sendota", "premis", "markot", "kolorado", "lotus", "mankis","sendot", "remont", "satirus", "sendat", "sendot", "spirant","tenis", "traktat", "alte", "apoge", "domen", "kaze ",
    "konus", "posten", "postenul", "kalkan", "fazan", "havaj", "havajo","pian", "lama", "malaj", "nordane", "refoj", "refoje","pian", "akirant", "format", "solea", "sole","konus", "lekant", "legat", "taksus", "reguluso", "endos",
    "regulusa", "akiranto", "kolorado", "satiruso", "spiranto","traktato", "nordano", "akiranto", "ordinata","sudano", "sudan", "marian", "paran", "parano", "parane","korano", "kore", "koran", "male", "paran", "samo",
    "satan", "savoj", "sudan", "okon", "apogeo", "nacian","amas", "min", "mondon", "gvidanto", "iris", "regulus",'agitas','agit','irit','iritis','iritant','aĝi','arĝentan','arĝentane','ĵaluzia']
for key in check_list:
    print(pre_replacements_dict_3[key],end=" ")


# In[64]:


# ⇓'replacements'リストはコードの前半と後半で内容が変わるので注意が必要。
# リスト'temporary_replacements_list_final'(一時的な置換リストの完成版) と 最終的な置換リスト(replacements_final_list)の一歩手前のリスト(辞書型配列)'pre_replacements_dict_3'は全くの別物である。

check_list = ["amas", "min", "mondon", "gvidanto", "iris", "regulus"]
for key in check_list:
    print(pre_replacements_dict_3[key],safe_replace(key,temporary_replacements_list_final))


# In[94]:


with open("替换用の辞書(字典)型配列(pre_replacements_dict_3).json", "w", encoding="utf-8") as g:
    json.dump(pre_replacements_dict_3, g, ensure_ascii=False, indent=2)  # ensure_ascii=FalseでUnicodeをそのまま出力
# with open("替换用の辞書(字典)型配列(pre_replacements_dict_3).json", "r", encoding="utf-8") as g:
#     pre_replacements_dict_3 = json.load(g)


# In[95]:


# 辞書型をリスト型に戻す。置換優先順位の数字の大きさ順にソートするため。
pre_replacements_list_1=[]
for old,new in  pre_replacements_dict_3.items():
    if isinstance(new[1], int):
        pre_replacements_list_1.append((old,new[0],new[1]))

pre_replacements_list_2= sorted(pre_replacements_list_1, key=lambda x: x[2], reverse=True)# (置換優先順位の数字の大きさ順にソート!)


# In[96]:


with open("替换用のリスト(列表)型配列(pre_replacements_list_2).json", "w", encoding="utf-8") as g:
    json.dump(pre_replacements_list_2, g, ensure_ascii=False, indent=2)  # ensure_ascii=FalseでUnicodeをそのまま出力
# with open("替换用のリスト(列表)型配列(pre_replacements_list_2).json", "r", encoding="utf-8") as g:
#     pre_replacements_list_2 = json.load(g)


# In[97]:


# 'エスペラント語根'、'置換後文字列'、'placeholder(占位符)'の順に並べ、最終的な文字列(漢字)置換に用いる"replacements"リストの元を作成。
pre_replacements_list_3=[]
for kk in range(len(pre_replacements_list_2)):
    if len(pre_replacements_list_2[kk][0])>=3:# 3文字以上でいいのではないか(202412)  la対策として考案された。
        pre_replacements_list_3.append([pre_replacements_list_2[kk][0],pre_replacements_list_2[kk][1],imported_placeholders[kk]])
len(pre_replacements_list_3)


# In[98]:


# エスペラント文の文字列(漢字)置換においては、"大文字"、"小文字"、"頭文字だけ大文字"、の3パターンに対応できるように置換用の'replacements'リストを作成するが、"頭文字だけ大文字"に対応するには、
# HTMLタグをうまく避けながら、頭文字のみを大文字化する必要性がある。("大文字"の場合は、HTML形式の仕様上、HTMLタグごと大文字化しても全く問題ない。)　下記はそれ用の関数。

def capitalize_ruby_and_rt(text):

    pattern = re.compile(
        r'^'              # 行頭／文字列頭
        r'(.*?)'          # グループ1: <ruby> より左側(外側)のテキスト
        r'(<ruby>)'       # グループ2: "<ruby>"
        r'([^<]+)'        # グループ3: "<ruby>"～"<rt" の間にある文字列　親要素(本文)
        r'(<rt[^>]*>)'    # グループ4: "<rt class="xxx"等 >"
        r'([^<]+)'        # グループ5: <rt>～</rt> の中身　子要素(ルビ部分)
        r'(</rt>)'        # グループ6: "</rt>"
        r'(</ruby>)?'     # グループ7: "</ruby>"
        r'(.*)'           # グループ8: 残り(この <ruby> ブロックの後ろのテキストすべて)
        r'$'              # 行末／文字列末
    )

    def replacer(match):
        g1 = match.group(1)# グループ1: <ruby> より左側(外側)のテキスト
        g2 = match.group(2)# グループ2: "<ruby>"
        g3 = match.group(3)# グループ3: "<ruby>"～"<rt" の間にある文字列　親要素(本文)
        g4 = match.group(4)# グループ4: "<rt class="xxx"等 >"
        g5 = match.group(5)# グループ5: <rt>～</rt> の中身　子要素(ルビ部分)
        g6 = match.group(6)# グループ6: "</rt>"
        g7 = match.group(7)# グループ7: "</ruby>"
        g8 = match.group(8)# グループ8: 残り(この <ruby> ブロックの後ろのテキストすべて)
        
        # 左側(外側)のテキストが空ではない場合 → 左側の先頭を大文字化
        if g1.strip():
            return g1.capitalize() + g2 + g3 + g4 + g5 + g6 + g7 + g8
        else:
            # 左側が空の場合 → <ruby> 内の親文字列/ルビ文字列を大文字化
            parent_text = g3.capitalize()
            rt_text = g5.capitalize()
            return g1 + g2 + parent_text + g4 + rt_text + g6 + g7 + g8

    replaced_text = pattern.sub(replacer, text)

    # もし置換が1箇所も行われなかった(=パターン不一致)なら、先頭を大文字化
    if replaced_text == text:
        replaced_text = text.capitalize()

    return replaced_text
    
    

# '大文字'、'小文字'、'文頭だけ大文字'の3パターンに対応。
pre_replacements_list_4=[]
if format_type in ('HTML格式_Ruby文字_大小调整','HTML格式_Ruby文字_大小调整_汉字替换','HTML格式','HTML格式_汉字替换'):
    for old,new,place_holder in pre_replacements_list_3:
        pre_replacements_list_4.append((old,new,place_holder))
        pre_replacements_list_4.append((old.upper(),new.upper(),place_holder[:-1]+'up$'))# placeholderを少し変更する必要がある。
        if old[0]==' ':# 置換対象の文字列の語頭が空白の場合にも対応　語頭に空白を入れている置換対象は殆どない。二文字語根のみ。
            pre_replacements_list_4.append((old[0] + old[1:].capitalize() ,new[0] + capitalize_ruby_and_rt(new[1:]),place_holder[:-1]+'cap$'))
        else:
            pre_replacements_list_4.append((old.capitalize(),capitalize_ruby_and_rt(new),place_holder[:-1]+'cap$'))
elif format_type in ('括弧(号)格式', '括弧(号)格式_汉字替换'):
    for old,new,place_holder in pre_replacements_list_3:
        pre_replacements_list_4.append((old,new,place_holder))
        pre_replacements_list_4.append((old.upper(),new.upper(),place_holder[:-1]+'up$'))
        if old[0]==' ':
            pre_replacements_list_4.append((old[0] + old[1:].capitalize(),new[0] + new[1:].capitalize(),place_holder[:-1]+'cap$'))
        else:
            pre_replacements_list_4.append((old.capitalize(),new.capitalize(),place_holder[:-1]+'cap$'))
elif format_type in ('替换后文字列のみ(仅)保留(简单替换)'):
    for old,new,place_holder in pre_replacements_list_3:
        pre_replacements_list_4.append((old,new,place_holder))
        pre_replacements_list_4.append((old.upper(),new.upper(),place_holder[:-1]+'up$'))
        if old[0]==' ':
            pre_replacements_list_4.append((old[0] + old[1:].capitalize() ,new[0] + new[1:].capitalize() ,place_holder[:-1]+'cap$'))
        else:
            pre_replacements_list_4.append((old.capitalize(),new.capitalize(),place_holder[:-1]+'cap$'))

len(pre_replacements_list_4)


# In[99]:


# 上のセルで定義された関数'capitalize_ruby_and_rt'のテスト
# text = "hello <ruby>kaj<rt>and</rt></ruby>"# <ruby> の前に文字列がある。
# result = capitalize_ruby_and_rt(text)
# print("入力: ", text,"  出力: ", result)
# text = "<ruby>kaj<rt>and</rt></ruby> world"# 行頭が <ruby> で始まる
# result = capitalize_ruby_and_rt(text)
# print("入力: ", text,"  出力: ", result)
# text = "Before <ruby>abc<rt>def"# </ruby> が省略されている
# result = capitalize_ruby_and_rt(text)
# print("入力: ", text,"  出力: ", result)
# text = "<ruby>kaj<rt>and</rt></ruby> <ruby>xyz<rt>zzz</rt></ruby>"# 1行に複数の <ruby> がある
# result = capitalize_ruby_and_rt(text)
# print("入力: ", text,"  出力: ", result)
# text = "hello  <ruby>abc<rt>def <ruby>kaj<rt>and</rt></ruby> <ruby>xyz<rt>zzz</rt></ruby>"# 1行に複数の <ruby> がある
# result = capitalize_ruby_and_rt(text)
# print("入力: ", text,"  出力: ", result)


# In[100]:


replacements_final_list=[]
for old, new, place_holder in pre_replacements_list_4:
    # 新しい変数で空白を追加した内容を保持
    modified_placeholder = place_holder
    if old.startswith(' '):
        modified_placeholder = ' ' + modified_placeholder  # 置換対象の文字列の語頭が空白の場合、placeholderの語頭にも空白を追加する。(空白の競合を防ぐため。)
        if not new.startswith(' '):
            new = ' ' + new
    if old.endswith(' '):
        modified_placeholder = modified_placeholder + ' '  # 置換対象の文字列の語末が空白の場合、placeholderの語末にも空白を追加する。(空白の競合を防ぐため。)
        if not new.endswith(' '):
            new = new + ' '
    # 結果をリストに追加
    replacements_final_list.append((old, new, modified_placeholder))


# In[101]:


# "replacements_final_list"リストの内容を確認

with open("全域替换用のリスト(列表)型配列(replacements_final_list).json", "w", encoding="utf-8") as g:
    json.dump(replacements_final_list, g, ensure_ascii=False, indent=2)  # ensure_ascii=FalseでUnicodeをそのまま出力
# with open("最终的な替换用のリスト(列表)型配列(replacements_final_list).json", "r", encoding="utf-8") as g:
#     replacements_final_list = json.load(g)
len(replacements_final_list)


# In[102]:


import re

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
# 使用例
text = """%L. Zamenhof.% Kongresaj paroladoj
Kongresaj paroladoj
%Lazarj Markoviĉ Zamenhof%

%Kongresaj paroladoj

Serio Scio, №2

La% 1a eldono: %Jekaterinburgo% Ruslanda Esperantisto, 1995.
La 2a eldono: %Kaliningrado%: Sezonoj; %Kaunas: LEA, 2015.%
"""
# プレースホルダーファイルから読み込む
placeholders_for_skipping_replacements = import_placeholders('占位符(placeholders)_%1854%-%4934%_文字列替换skip用.txt')# placeholderに'%'が含まれる必要は全く無いが、雰囲気を揃えるために敢えて入れた。
# リストを作成
replacements_list_for_intact_parts = create_replacements_list_for_intact_parts(text, placeholders_for_skipping_replacements)
sorted_replacements_list_for_intact_parts = sorted(replacements_list_for_intact_parts, key=lambda x: len(x[0]), reverse=True)
# 結果を表示
for item in sorted_replacements_list_for_intact_parts:
    print(item)


# In[103]:


# '@'で囲まれた18文字(PEJVOに収録されている最長語根の文字数)以内の部分を同定し、局所的な文字列(漢字)置換を実行するための関数群

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


# 局所的な文字列(漢字)置換には、最初の"input_csv_file"のみを使って作成した置換リストを用いる。
pre_replacements_list_for_localized_string_1=[]
for _, (E_root, hanzi_or_meaning) in CSV_data_imported.iterrows():
    if pd.notna(E_root) and pd.notna(hanzi_or_meaning) and '#' not in E_root and (E_root != '') and (hanzi_or_meaning != ''):  # 条件を満たす行のみ処理
        pre_replacements_list_for_localized_string_1.append([E_root,output_format(E_root, hanzi_or_meaning, format_type),len(E_root)])
        pre_replacements_list_for_localized_string_1.append([E_root.upper(),output_format(E_root.upper(), hanzi_or_meaning.upper(), format_type),len(E_root)])
        pre_replacements_list_for_localized_string_1.append([E_root.capitalize(),output_format(E_root.capitalize(), hanzi_or_meaning.capitalize(), format_type),len(E_root)])


pre_replacements_list_for_localized_string_2 = sorted(pre_replacements_list_for_localized_string_1, key=lambda x: x[2], reverse=True)
# print(len(pre_replacements_list_for_localized_string_2))

imported_placeholders = import_placeholders('占位符(placeholders)_@20374@-@97648@_局部文字列替换用.txt')# placeholderに'@'が含まれる必要は全く無いが、雰囲気を揃えるために敢えて入れた。
replacements_list_for_localized_string=[]
for kk in range(len(pre_replacements_list_for_localized_string_2)):
    replacements_list_for_localized_string.append([pre_replacements_list_for_localized_string_2[kk][0],pre_replacements_list_for_localized_string_2[kk][1],imported_placeholders[kk]])

with open("局部文字替换用のリスト(列表)型配列(replacements_list_for_localized_string).json", "w", encoding="utf-8") as f:
    json.dump(replacements_list_for_localized_string, f, ensure_ascii=False, indent=2)


import re
def find_strings_in_text_for_localized_replacement(text):
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
def import_placeholders(filename):
    with open(filename, 'r') as file:
        placeholders = [line.strip() for line in file if line.strip()]
    return placeholders
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

# 使用例
text = """@Esper@@anto@ Kongresaj paroladoj
Kongresaj paroladoj
@Lazarj Markoviĉ Zamenhof@

Kongresaj paroladoj

Serio Scio, №2

La 1a eldono: @Jekaterinburgo@ Ruslanda Esperantisto, 1995.
La 2a eldono: @Kaliningrado@: Sezonoj; @Kaunas: LEA, 2015.@
"""
# プレースホルダーファイルから読み込む
placeholders_for_localized_replacement = import_placeholders('占位符(placeholders)_@5134@-@9728@_局部文字列替换结果捕捉用.txt')# placeholderに'@'が含まれる必要は全く無いが、雰囲気を揃えるために敢えて入れた。
# リストを作成
tmp_replacements_list_for_localized_string = create_replacements_list_for_localized_replacement(text, placeholders_for_localized_replacement,replacements_list_for_localized_string)
sorted_replacements_list_for_localized_string = sorted(tmp_replacements_list_for_localized_string, key=lambda x: len(x[0]), reverse=True)
# 結果を表示
# for item in sorted_replacements_list_for_localized_string:
#     print(item)

sorted_replacements_list_for_localized_string


# In[104]:


safe_replace("Esperanto", replacements_list_for_localized_string)


# 以下では2文字語根用の文字列(漢字)置換処理を実装した。 通常、2文字語根単独の置換処理の実装は、本コードのように文字列置換に頼った語根分解では、置換精度の観点から難しいことが多いが、"置換対象の2文字語根が、既に置換された文字列に隣接している場合に限っては実装可能なのではないか"と考えた。

# In[105]:


suffix_2char_roots=['ad', 'ag', 'am', 'ar', 'as', 'at', 'av', 'di', 'ec', 'eg', 'ej', 'em', 'er', 'et', 'id', 'ig', 'il', 'in', 'ir', 'is', 'it', 'lu', 'nj', 'op', 'or', 'os', 'ot', 'ov', 'pi', 'te', 'uj', 'ul', 'um', 'us', 'uz','ĝu','aĵ','iĝ','aĉ','aĝ','ŝu','eĥ']
prefix_2char_roots=['al', 'am', 'av', 'bo', 'di', 'du', 'ek', 'el', 'en', 'fi', 'ge', 'ir', 'lu', 'ne', 'ok', 'or', 'ov', 'pi', 're', 'te', 'uz','ĝu','aĉ','aĝ','ŝu','eĥ']
standalone_2char_roots=['al', 'ci', 'da', 'de', 'di', 'do', 'du', 'el', 'en', 'fi', 'ha', 'he', 'ho', 'ia', 'ie', 'io', 'iu', 'ja', 'je', 'ju','ke', 'la', 'li', 'mi', 'ne', 'ni', 'nu', 'ok', 'ol', 'po', 'se', 'si', 've', 'vi','ŭa','aŭ','ĉe','ĝi','ŝi','ĉu']
# an,onはなしにする。


# In[106]:


imported_placeholders_for_2char = import_placeholders('占位符(placeholders)_$13246$-$19834$_二文字词根替换用.txt')# 文字列(漢字)置換時に用いる"placeholder"ファイルを予め読み込んでおく。

replacements_list_for_suffix_2char_roots=[]
for i in range(len(suffix_2char_roots)):
    replaced_suffix = safe_replace(suffix_2char_roots[i],temporary_replacements_list_final)
    replacements_list_for_suffix_2char_roots.append(["$"+suffix_2char_roots[i],"$"+replaced_suffix,"$"+imported_placeholders_for_2char[i]])
    replacements_list_for_suffix_2char_roots.append(["$"+suffix_2char_roots[i].upper(),"$"+replaced_suffix.upper(),"$"+imported_placeholders_for_2char[i][:-1]+'up$'])
    replacements_list_for_suffix_2char_roots.append(["$"+suffix_2char_roots[i].capitalize(),"$"+capitalize_ruby_and_rt(replaced_suffix),"$"+imported_placeholders_for_2char[i][:-1]+'cap$'])

replacements_list_for_prefix_2char_roots=[]
for i in range(len(prefix_2char_roots)):
    replaced_prefix = safe_replace(prefix_2char_roots[i],temporary_replacements_list_final)
    replacements_list_for_prefix_2char_roots.append([prefix_2char_roots[i]+"$",replaced_prefix+"$",imported_placeholders_for_2char[i+1000]+"$"])
    replacements_list_for_prefix_2char_roots.append([prefix_2char_roots[i].upper()+"$",replaced_prefix.upper()+"$",imported_placeholders_for_2char[i+1000][:-1]+'up$'+"$"])
    replacements_list_for_prefix_2char_roots.append([prefix_2char_roots[i].capitalize()+"$",capitalize_ruby_and_rt(replaced_prefix)+"$",imported_placeholders_for_2char[i+1000][:-1]+'cap$'+"$"])

replacements_list_for_standalone_2char_roots=[]
for i in range(len(standalone_2char_roots)):
    replaced_standalone = safe_replace(standalone_2char_roots[i],temporary_replacements_list_final)
    replacements_list_for_standalone_2char_roots.append([" "+standalone_2char_roots[i]+" "," "+replaced_standalone+" "," "+imported_placeholders_for_2char[i+2000]+" "])
    replacements_list_for_standalone_2char_roots.append([" "+standalone_2char_roots[i].upper()+" "," "+replaced_standalone.upper()+" "," "+imported_placeholders_for_2char[i+2000][:-1]+'up$'+" "])
    replacements_list_for_standalone_2char_roots.append([" "+standalone_2char_roots[i].capitalize()+" "," "+capitalize_ruby_and_rt(replaced_standalone)+" "," "+imported_placeholders_for_2char[i+2000][:-1]+'cap$'+" "])


replacements_list_for_2char=replacements_list_for_standalone_2char_roots+replacements_list_for_suffix_2char_roots+replacements_list_for_prefix_2char_roots

import json
# JSONファイルに保存
with open("二文字词根替换用のリスト(列表)型配列(replacements_list_for_2char).json", "w", encoding="utf-8") as f:
    json.dump(replacements_list_for_2char, f, ensure_ascii=False, indent=2)


# In[107]:


# 実際に文字列(漢字)置換に用いる'replacements'リストを一つのJSONファイルに統合し、出力する。
import json

# --- 結合する処理 ---
combined_3_replacements_lists = {}

combined_3_replacements_lists["全域替换用のリスト(列表)型配列(replacements_final_list)"] = replacements_final_list
combined_3_replacements_lists["二文字词根替换用のリスト(列表)型配列(replacements_list_for_2char)"] = replacements_list_for_2char
combined_3_replacements_lists["局部文字替换用のリスト(列表)型配列(replacements_list_for_localized_string)"] = replacements_list_for_localized_string

# JSONファイルに保存
with open("最终的な替换用リスト(列表)(合并3个JSON文件).json", "w", encoding="utf-8") as f:
    json.dump(combined_3_replacements_lists, f, ensure_ascii=False, indent=2)



# In[108]:


import json
import re


# プレースホルダーを用いた文字列(漢字)置換関数
def enhanced_safe_replace_func_expanded_for_2char_roots(text, replacements, replacements_list_for_2char):
    valid_replacements = {}
    for old, new, placeholder in replacements:
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
    for place_holder_second, new in reversed(valid_replacements_for_2char_roots_2.items()):# ここで、reverseにすることがポイント。
        text = text.replace(place_holder_second, new)# プレースホルダーを置換後の文字列に置き換える。
    for placeholder, new in reversed(valid_replacements_for_2char_roots.items()):
        text = text.replace(placeholder, new)# プレースホルダーを置換後の文字列に置き換える。
    for placeholder, new in valid_replacements.items():
        text = text.replace(placeholder, new)
    return text


# In[109]:


# multiprocessingのための関数群　テキストを行数によって設定プロセス数(num_processes)に等分割して、それぞれのプロセスで並列に置換処理を実行してから、再度分割したテキストを結合する。

import multiprocessing
def process_segment(lines, replacements, replacements_list_for_2char):
    # 文字列のリストを結合してから置換処理を実行 linesには\nが含まれていない状態の文字列群が格納されている。
    segment = '\n'.join(lines)
    segment = enhanced_safe_replace_func_expanded_for_2char_roots(segment, replacements, replacements_list_for_2char)# ここでenhanced_safe_replace_func_expanded_for_2char_roots関数の実行
    return segment
def parallel_process(text, num_processes,replacements_final_list, replacements_list_for_2char):
    # テキストを行で分割
    lines = text.split('\n')
    num_lines = len(lines)
    lines_per_process = num_lines // num_processes
    # 各プロセスに割り当てる行のリストを決定
    ranges = [(i * lines_per_process, (i + 1) * lines_per_process) for i in range(num_processes)]
    ranges[-1] = (ranges[-1][0], num_lines)  # 最後のプロセスが残り全てを処理
    with multiprocessing.Pool(processes=num_processes) as pool:
        # 並列処理を実行
        results = pool.starmap(process_segment, [(lines[start:end], replacements_final_list, replacements_list_for_2char) for start, end in ranges])
    # 結果を結合
    return '\n'.join(result for result in results)


# In[110]:


# 文字列(漢字)置換に用いる'replacements'リストと占位符(placeholders)を呼び出す。
with open("最终的な替换用リスト(列表)(合并3个JSON文件).json", "r", encoding="utf-8") as f:
    combined_3_replacements_lists = json.load(f)
replacements_final_list = combined_3_replacements_lists.get("全域替换用のリスト(列表)型配列(replacements_final_list)", None)
replacements_list_for_localized_string = combined_3_replacements_lists.get("局部文字替换用のリスト(列表)型配列(replacements_list_for_localized_string)", None)
replacements_list_for_2char = combined_3_replacements_lists.get("二文字词根替换用のリスト(列表)型配列(replacements_list_for_2char)", None)

placeholders_for_skipping_replacements = import_placeholders('占位符(placeholders)_%1854%-%4934%_文字列替换skip用.txt')# placeholderに'%'が含まれる必要は全く無いが、雰囲気を揃えるために敢えて入れた。
placeholders_for_localized_replacement = import_placeholders('占位符(placeholders)_@5134@-@9728@_局部文字列替换结果捕捉用.txt')# placeholderに'@'が含まれる必要は全く無いが、雰囲気を揃えるために敢えて入れた。


# In[111]:


import re

with open('例句_Esperanto文本.txt','r', encoding='utf-8') as g:
    text0=g.read()
text1 = unify_halfwidth_spaces(text0)# 半角スペースと視覚的に区別がつきにくい特殊な空白文字を標準的なASCII半角スペース(U+0020)に置換する。 ただし、全角スペース(U+3000)は置換対象に含めていない。
text1=replace_esperanto_chars(text1,hat_to_circumflex)
text1=replace_esperanto_chars(text1,x_to_circumflex)

replacements_list_for_intact_parts = create_replacements_list_for_intact_parts(text1, placeholders_for_skipping_replacements)
sorted_replacements_list_for_intact_parts = sorted(replacements_list_for_intact_parts, key=lambda x: len(x[0]), reverse=True)
for original, place_holder_ in sorted_replacements_list_for_intact_parts:
    text1 = text1.replace(original, place_holder_)# いいのか→多分大丈夫。

tmp_replacements_list_for_localized_string_2 = create_replacements_list_for_localized_replacement(text1, placeholders_for_localized_replacement, replacements_list_for_localized_string)
sorted_replacements_list_for_localized_string = sorted(tmp_replacements_list_for_localized_string_2, key=lambda x: len(x[0]), reverse=True)
for original, place_holder_, replaced_original in sorted_replacements_list_for_localized_string:
    text1 = text1.replace(original, place_holder_)

text1=enhanced_safe_replace_func_expanded_for_2char_roots(text1, replacements_final_list, replacements_list_for_2char)

for original, place_holder_, replaced_original in sorted_replacements_list_for_localized_string:
    text1 = text1.replace(place_holder_, replaced_original.replace("@",""))

for original, place_holder_ in sorted_replacements_list_for_intact_parts:
    text1 = text1.replace(place_holder_, original.replace("%",""))

if format_type in ('HTML格式_Ruby文字_大小调整','HTML格式_Ruby文字_大小调整_汉字替换','HTML格式','HTML格式_汉字替换'):
    # 改行を <br> に変換
    text1 = text1.replace("\n", "<br>\n")
    # 連続する空白を &nbsp; に変換
    text1 = re.sub(r"   ", "&nbsp;&nbsp;&nbsp;", text1)  # 3つ以上の空白を変換
    text1 = re.sub(r"  ", "&nbsp;&nbsp;", text1)  # 2つ以上の空白を変換

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

text1=ruby_style_head+text1+ruby_style_tail

with open('Esperanto_Text_Replacement_Result.html','w', encoding='utf-8') as h:
    h.write(text1)


# In[54]:


# multi_processing 版
num_processes=4
text_repeat_times=10

with open('例句_Esperanto文本.txt','r', encoding='utf-8') as g:
    text0=g.read()*text_repeat_times
text1 = unify_halfwidth_spaces(text0)# 半角スペースと視覚的に区別がつきにくい特殊な空白文字を標準的なASCII半角スペース(U+0020)に置換する。 ただし、全角スペース(U+3000)は置換対象に含めていない。
text1=replace_esperanto_chars(text1,hat_to_circumflex)
text1=replace_esperanto_chars(text1,x_to_circumflex)

replacements_list_for_intact_parts = create_replacements_list_for_intact_parts(text1, placeholders_for_skipping_replacements)
sorted_replacements_list_for_intact_parts = sorted(replacements_list_for_intact_parts, key=lambda x: len(x[0]), reverse=True)
for original, place_holder_ in sorted_replacements_list_for_intact_parts:
    text1 = text1.replace(original, place_holder_)# いいのか→多分大丈夫。

tmp_replacements_list_for_localized_string_2 = create_replacements_list_for_localized_replacement(text1, placeholders_for_localized_replacement, replacements_list_for_localized_string)
sorted_replacements_list_for_localized_string = sorted(tmp_replacements_list_for_localized_string_2, key=lambda x: len(x[0]), reverse=True)
for original, place_holder_, replaced_original in sorted_replacements_list_for_localized_string:
    text1 = text1.replace(original, place_holder_)

text1=parallel_process(text1, num_processes,replacements_final_list, replacements_list_for_2char)

for original, place_holder_, replaced_original in sorted_replacements_list_for_localized_string:
    text1 = text1.replace(place_holder_, replaced_original.replace("@",""))

for original, place_holder_ in sorted_replacements_list_for_intact_parts:
    text1 = text1.replace(place_holder_, original.replace("%",""))

if format_type in ('HTML格式_Ruby文字_大小调整','HTML格式_Ruby文字_大小调整_汉字替换','HTML格式','HTML格式_汉字替换'):
    # 改行を <br> に変換
    text1 = text1.replace("\n", "<br>\n")
    # 連続する空白を &nbsp; に変換
    text1 = re.sub(r"   ", "&nbsp;&nbsp;&nbsp;", text1)  # 3つ以上の空白を変換
    text1 = re.sub(r"  ", "&nbsp;&nbsp;", text1)  # 2つ以上の空白を変換

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

text1=ruby_style_head+text1+ruby_style_tail

with open('Esperanto_Text_Replacement_Result_Multiprocessing.html','w', encoding='utf-8') as h:
    h.write(text)


# In[55]:


# multi_processing 版
# タイム計測　どの処理にどれだけの時間を要しているか？
# ミスの確認を容易にするため、textの変数名についても多様に使い分けて区別した。

num_processes=4
text_repeat_times=10
import time

with open('例句_Esperanto文本.txt','r', encoding='utf-8') as g:
    text0=g.read()*text_repeat_times
text0_5 = unify_halfwidth_spaces(text0)# 半角スペースと視覚的に区別がつきにくい特殊な空白文字を標準的なASCII半角スペース(U+0020)に置換する。 ただし、全角スペース(U+3000)は置換対象に含めていない。    
text1=replace_esperanto_chars(text0_5,x_to_circumflex)
text2=replace_esperanto_chars(text1,hat_to_circumflex)

time1=time.time()
replacements_list_for_intact_parts = create_replacements_list_for_intact_parts(text2, placeholders_for_skipping_replacements)
sorted_replacements_list_for_intact_parts = sorted(replacements_list_for_intact_parts, key=lambda x: len(x[0]), reverse=True)
for original, place_holder_ in sorted_replacements_list_for_intact_parts:
    text2 = text2.replace(original, place_holder_)# いいのか→多分大丈夫。

time2=time.time()
tmp_replacements_list_for_localized_string_2 = create_replacements_list_for_localized_replacement(text2, placeholders_for_localized_replacement, replacements_list_for_localized_string)
sorted_replacements_list_for_localized_string = sorted(tmp_replacements_list_for_localized_string_2, key=lambda x: len(x[0]), reverse=True)
for original, place_holder_, replaced_original in sorted_replacements_list_for_localized_string:
    text2 = text2.replace(original, place_holder_)

time3=time.time()
text3=parallel_process(text2, num_processes,replacements_final_list, replacements_list_for_2char)

time4=time.time()
for original, place_holder_, replaced_original in sorted_replacements_list_for_localized_string:
    text3 = text3.replace(place_holder_, replaced_original.replace("@",""))

time5=time.time()
for original, place_holder_ in sorted_replacements_list_for_intact_parts:
    text3 = text3.replace(place_holder_, original.replace("%",""))

time6=time.time()

if format_type in ('HTML格式_Ruby文字_大小调整','HTML格式_Ruby文字_大小调整_汉字替换','HTML格式','HTML格式_汉字替换'):
    # 改行を <br> に変換
    text3 = text3.replace("\n", "<br>\n")
    # 連続する空白を &nbsp; に変換
    text3 = re.sub(r"   ", "&nbsp;&nbsp;&nbsp;", text3)  # 3つ以上の空白を変換
    text3 = re.sub(r"  ", "&nbsp;&nbsp;", text3)  # 2つ以上の空白を変換

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

text4=ruby_style_head+text3+ruby_style_tail

time7=time.time()

with open('Esperanto_Text_Replacement_Result_Multiprocessing.html','w', encoding='utf-8') as h:
    h.write(text4)

# タイムスタンプをリストにまとめる
timestamps = [time1, time2, time3, time4, time5, time6, time7]

# 隣り合うタイムスタンプの差分を計算
differences = [timestamps[i + 1] - timestamps[i] for i in range(len(timestamps) - 1)]

# 差分を出力
for i, diff in enumerate(differences):
    print(f"time{i+2} - time{i+1}: {diff:.6f} seconds")


# In[56]:


# スマホ・タブレット用のHTML形式
import re

with open('例句_Esperanto文本.txt','r', encoding='utf-8') as g:
    text0=g.read()
text1 = unify_halfwidth_spaces(text0)# 半角スペースと視覚的に区別がつきにくい特殊な空白文字を標準的なASCII半角スペース(U+0020)に置換する。 ただし、全角スペース(U+3000)は置換対象に含めていない。
text1=replace_esperanto_chars(text1,hat_to_circumflex)
text1=replace_esperanto_chars(text1,x_to_circumflex)

replacements_list_for_intact_parts = create_replacements_list_for_intact_parts(text1, placeholders_for_skipping_replacements)
sorted_replacements_list_for_intact_parts = sorted(replacements_list_for_intact_parts, key=lambda x: len(x[0]), reverse=True)
for original, place_holder_ in sorted_replacements_list_for_intact_parts:
    text1 = text1.replace(original, place_holder_)# いいのか→多分大丈夫。

tmp_replacements_list_for_localized_string_2 = create_replacements_list_for_localized_replacement(text1, placeholders_for_localized_replacement, replacements_list_for_localized_string)
sorted_replacements_list_for_localized_string = sorted(tmp_replacements_list_for_localized_string_2, key=lambda x: len(x[0]), reverse=True)
for original, place_holder_, replaced_original in sorted_replacements_list_for_localized_string:
    text1 = text1.replace(original, place_holder_)

text1=enhanced_safe_replace_func_expanded_for_2char_roots(text1, replacements_final_list, replacements_list_for_2char)

for original, place_holder_, replaced_original in sorted_replacements_list_for_localized_string:
    text1 = text1.replace(place_holder_, replaced_original.replace("@",""))

for original, place_holder_ in sorted_replacements_list_for_intact_parts:
    text1 = text1.replace(place_holder_, original.replace("%",""))

if format_type in ('HTML格式_Ruby文字_大小调整','HTML格式_Ruby文字_大小调整_汉字替换','HTML格式','HTML格式_汉字替换'):
    # 改行を <br> に変換
    text1 = text1.replace("\n", "<br>\n")
    # 連続する空白を &nbsp; に変換
    text1 = re.sub(r"   ", "&nbsp;&nbsp;&nbsp;", text1)  # 3つ以上の空白を変換
    text1 = re.sub(r"  ", "&nbsp;&nbsp;", text1)  # 2つ以上の空白を変換

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
  transform: translateX(-0%) translateY(-0.25em); /* スマホ・タブレット用のHTML形式においては、 rtブロックのtop,left行は認識されないため、削除し、その分transform行についても少し調節する。 */
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

text1=ruby_style_head+text1+ruby_style_tail

with open('Esperanto_Text_Replacement_Result_smartphone_tablet_HTML_Format.html','w', encoding='utf-8') as h:
    h.write(text1)


# 以下是附录(以下はおまけ)
