import streamlit as st
import re
import io
from PIL import Image
import pandas as pd
import json

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

# 字上符付き文字の表記形式変換用の辞書型の配列
esperanto_to_x = {
    "ĉ": "cx", "ĝ": "gx", "ĥ": "hx", "ĵ": "jx", "ŝ": "sx", "ŭ": "ux",
    "Ĉ": "Cx", "Ĝ": "Gx", "Ĥ": "Hx", "Ĵ": "Jx", "Ŝ": "Sx", "Ŭ": "Ux",
    "c^": "cx", "g^": "gx", "h^": "hx", "j^": "jx", "s^": "sx", "u^": "ux",
    "C^": "Cx", "G^": "Gx", "H^": "Hx", "J^": "Jx", "S^": "Sx", "U^": "Ux"
}
x_to_jijofu = {'cx': 'ĉ', 'gx': 'ĝ', 'hx': 'ĥ', 'jx': 'ĵ', 'sx': 'ŝ', 'ux': 'ŭ', 'Cx': 'Ĉ',
               'Gx': 'Ĝ', 'Hx': 'Ĥ', 'Jx': 'Ĵ', 'Sx': 'Ŝ', 'Ux': 'Ŭ'}
x_to_hat = {'cx': 'c^', 'gx': 'g^', 'hx': 'h^', 'jx': 'j^', 'sx': 's^', 'ux': 'u^', 'Cx': 'C^',
            'Gx': 'G^', 'Hx': 'H^', 'Jx': 'J^', 'Sx': 'S^', 'Ux': 'U^'}

# 字上符付き文字の表記形式変換用の関数
def replace_esperanto_chars(text, letter_dictionary):
    for esperanto_char, x_char in letter_dictionary.items():
        text = text.replace(esperanto_char, x_char)
    return text

##
import json
import re
# JSONファイルを読み込む
with open("./files_needed_to_get_replacements_list_json_format/ABC_replacements_list_for_2char_Chinese.json", "r", encoding="utf-8") as f:
    imported_data_ABC_replacements_list_for_2char = json.load(f)

# プレースホルダーを用いた文字列置換関数
def enhanced_safe_replace_func_expanded_for_2char_roots(text, replacements, imported_data_ABC_replacements_list_for_2char):
    valid_replacements = {}
    for old, new, placeholder in replacements:
        if old in text:
            text = text.replace(old, placeholder)# 置換前の文字列を一旦プレースホルダーに置き換える。
            valid_replacements[placeholder] = new
# ここで、2文字の語根の置換を実施することとした(202412の変更)。  &%
    valid_replacements_ABC = {}
    for old, new, placeholder in imported_data_ABC_replacements_list_for_2char:
        if old in text:
            text = text.replace(old, placeholder)
            valid_replacements_ABC[placeholder] = new
    valid_replacements_ABC_2 = {}
    for old, new, placeholder in imported_data_ABC_replacements_list_for_2char:
        if old in text:
            place_holder_second="!"+placeholder+"!"##2回目のplace_holderは少し変更を加えたほうが良いはず。
            text = text.replace(old, place_holder_second)
            valid_replacements_ABC_2[place_holder_second] = new
    for place_holder_second, new in reversed(valid_replacements_ABC_2.items()):##ここで、reverseにすることがポイント。
        text = text.replace(place_holder_second, new)# プレースホルダーを置換後の文字列に置き換える。
    for placeholder, new in reversed(valid_replacements_ABC.items()):
        text = text.replace(placeholder, new)# プレースホルダーを置換後の文字列に置き換える。
    for placeholder, new in valid_replacements.items():
        text = text.replace(placeholder, new)
    return text

import re

# "%%"で囲まれた文字列を置換しないで保っておくための関数
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

# 文字列置換関数の実行時に用いるプレースホルダーをファイルから読み込むための関数
def load_placeholders(filename):
    with open(filename, 'r') as file:
        placeholders = [line.strip() for line in file if line.strip()]
    return placeholders
# ?
def create_replacements(text, placeholders):
    # テキストから%%で囲まれた部分を抽出
    matches = find_strings_in_text(text)
    replacements_list_for_intact_parts = []
    # プレースホルダーとマッチを対応させる
    for i, match in enumerate(matches):
        if i < len(placeholders):
            replacements_list_for_intact_parts.append([f"%%{match}%%", placeholders[i]])
        else:
            break  # プレースホルダーが足りなくなった場合は終了(そんなことは殆どないように大量のプレースホルダーが用意されている。)
    return replacements_list_for_intact_parts

# プレースホルダーファイルから読み込む
placeholders = load_placeholders('./files_needed_to_get_replacements_list_json_format/No.1000_9999.txt')



st.title("世界语汉字化")
st.caption('这是一个将世界语文本转换成汉字符号的网络应用程序。')


# サンプルファイルのパス
file_path4 = './files_needed_to_get_replacements_list_json_format/replacements_list_ruby_html_format_中文_対応ruby尺寸更改.txt'
# ファイルを読み込む
with open(file_path4, "rb") as file:
    btn = st.download_button(
            label="下载示例文件4(Ruby_中文_対応ruby尺寸更改)",
            data=file,
            file_name="replacements_list_ruby_html_format_中文_対応ruby尺寸更改.txt",
            mime="text/plain"
        )
    
# サンプルファイルのパス
file_path5 = './files_needed_to_get_replacements_list_json_format/replacements_list_ruby_html_format_日本語_ルビサイズ変更対応.txt'
# ファイルを読み込む
with open(file_path5, "rb") as file:
    btn = st.download_button(
            label="下载示例文件5(Ruby_日本語_ルビサイズ変更対応)",
            data=file,
            file_name="replacements_list_ruby_html_format_日本語_ルビサイズ変更対応.txt",
            mime="text/plain"
        )


uploaded_file = st.file_uploader("上传你的'replacements_list_<html,parentheses,onlyhanzi,ruby>_format.txt'", type=['txt'])
if uploaded_file is not None:
    replacements3 = []
    for line in uploaded_file:
        decoded_line = line.decode('utf-8').rstrip()##strip()では駄目
        parts = decoded_line.split(',')
        if len(parts) == 3:
            replacements3.append((parts[0], parts[1], parts[2]))
else:
    replacements3 = []
    with open("./files_needed_to_get_replacements_list_json_format/最終的な置換用のリスト(replacements_final_list)_Chinese.json", 'r', encoding='utf-8') as g:
        replacements_final_list_2 = json.load(g)
text3=""
with st.form(key='profile_form'):
    letter_type = st.radio('输出字符格式', ('上标字符', 'x形式', '^形式'))
    sentence = st.text_area("世界语句子")
    st.markdown("""通过在前后加上“%%”（形式为“%%<50个字符以内的字符串>%%”），可以保持被“%%”包围的部分不转换为汉字，保留原样。""")
    st.markdown("""“%%”で前後を囲むことによって(“%%<50字以内の文字列>%%”の形式)、“%%”で囲まれた部分を漢字化せずに、元のままに保つことができます。""")

    submit_btn = st.form_submit_button('发送')
    cancel_btn = st.form_submit_button('取消')
    if submit_btn:
        replaced_text = replace_esperanto_chars(sentence, esperanto_to_x)

        replacements_list_for_intact_parts = create_replacements(replaced_text, placeholders)
        sorted_replacements_list_for_intact_parts = sorted(replacements_list_for_intact_parts, key=lambda x: len(x[0]), reverse=True)
        for original, place_holder_ in sorted_replacements_list_for_intact_parts:
            replaced_text = replaced_text.replace(original, place_holder_)
        text3 = enhanced_safe_replace_func_expanded_for_2char_roots(replaced_text, replacements_final_list_2, imported_data_ABC_replacements_list_for_2char)# ここが一番メインの置換　⇑では"%%"で囲まれた部分をプレースホルダーに置き換える作業を、⇓では、プレースホルダーに置き換えられた、"%%"で囲まれた部分を元の文字列に戻す作業を行っている。
        for original, place_holder_ in sorted_replacements_list_for_intact_parts:
            text3 = text3.replace(place_holder_, original.replace("%%",""))
        # ⇓出力文字形式の変換
        if letter_type == '上标字符':
            text3 = replace_esperanto_chars(text3, x_to_jijofu)
        elif letter_type == '^形式':
            text3 = replace_esperanto_chars(text3, x_to_hat)
        
        # 改行を <br> に変換
        text3 = text3.replace("\n", "<br>\n")
        # 連続する空白を &nbsp; に変換
        text3 = re.sub(r"  ", "&nbsp;&nbsp;", text3)  # 2つ以上の空白を変換

        text3=ruby_style+text3+ruby_style_tail

        st.text_area("转换后的文本预览", text3, height=300)

if text3:
    to_download = io.BytesIO(text3.encode('utf-8'))
    to_download.seek(0)
    st.download_button(
        label="下载文本",
        data=to_download,
        file_name="processed_text.html",
        mime="text/plain"
    )




# コメント欄の追加
# st.sidebar.title("コメント欄")
# comments = st.sidebar.text_area("ご意見・ご感想をお聞かせください")


# 操作方法の説明
st.title("操作方法(下に日本語訳が有ります。)")
st.markdown("""
如果您想在世界语文本的汉字转换中使用自制的世界语词根-汉字对照表,
首先,请下载并参考'make replacement file'中附带的'下载示例文件',
并创建如下附图所示格式的csv文件。(请使用X形式的世界语词根。)""")
                               
# エスペラント語根と対応する漢字の例画像を表示
image2 = Image.open('エスペラント語根-漢字対応表(csv形式)の作り方.png')
st.image(image2, caption='世界语词根-汉字对照表(csv格式)的创建方法', use_column_width=False, width=450)  # 画像にキャプションを追加し、サイズを調整          
st.markdown("""
接下来,请将创建的csv文件上传到'make replacement file'
并创建和下载'replacements_list_<html,parentheses,onlyhanzi>_format.txt'。
(在此过程中,请从'html格式(HTML Format)'、'括号格式(Parentheses Format)'、'仅汉字格式(Only Hanzi)'中选择汉字转换格式。)
上传csv文件后,'replacements_list_<html,parentheses,onlyhanzi>_format.txt'的创建将自动开始。创建完成大约需要20秒。
最后,将创建的'replacements_list_<html,parentheses,onlyhanzi>_format.txt'上传到'main',
选择'输出字符格式',在'世界语句子'中粘贴要转换为汉字的世界语句子,按下'发送'按钮,
转换为汉字的世界语句子将作为预览输出,按'下载文本'按钮,可以将转换为汉字的世界语句子作为文本文件下载并保存。
(如果是html格式,可以在Google Chrome等网络浏览器中打开,就能看到干净整洁的注音(注音字母)。)                                                        
""")


# 操作方法の説明
st.title("操作方法")
st.markdown("""
自作のエスペラント語根-漢字対応表をエスペラント文の漢字変換に用いたい場合、
まず、'make replacement file'に添付されている'下载示例文件'をダウンロード・参照し、
以下の添付画像ような形式のcsvファイルを作成してください。(エスペラント語根はX形式でお願いします。)""")
                               
# エスペラント語根と対応する漢字の例画像を表示
image2 = Image.open('エスペラント語根-漢字対応表(csv形式)の作り方.png')
st.image(image2, caption='エスペラント語根-漢字対応表(csv形式)の作り方', use_column_width=False, width=450)  # 画像にキャプションを追加し、サイズを調整                

st.markdown("""
次に、作成したcsvファイルを'make replacement file'にアップロードし、
'replacements_list_<html,parentheses,onlyhanzi>_format.txt'を作成、ダウンロードします。(このときに、
漢字変換の形式を、'html形式(HTML Format)','括弧形式(Parentheses Format)','漢字のみの形式(Only Hanzi)'
から選択してください。)
csvファイルをアップロードした段階で自動的に'replacements_list_<html,parentheses,onlyhanzi>_format.txt'
の作成が始まります。作成完了まで20秒程かかります。
最後に作成された'replacements_list_<html,parentheses,onlyhanzi>_format.txt'を'main'にアップロードし、
'出力文字形式'を選択、'世界语句子'に漢字変換したいエスペラント文を貼り付け、
'发送' ボタンを押せば、漢字変換されたエスペラント文がプレビューとして
出力され、'下载文本'ボタンを押すと、 漢字変換されたエスペラント文を
テキストファイルとしてダウンロード保存することが出来ます。
(html形式であれば、google chromeなどのウェブブラウザで開くと綺麗にふりがな
(ふりアルファベット)がついているのを見ることが出来ます。)                                                        
""")







# 画像をページの下部に配置
st.markdown("---")  # 水平線を追加して区切りを作成
image = Image.open('エスペラントの漢字化の理想図.png')
st.image(image, caption='世界语汉字化的理想图', use_column_width=False, width=450)  # 画像にキャプションを追加し、サイズを調整

# 連絡先の追加
st.title("应用程序的github仓库")
st.markdown("https://github.com/Takatakatake/Esperanto_kanjika_20240310/tree/main")
