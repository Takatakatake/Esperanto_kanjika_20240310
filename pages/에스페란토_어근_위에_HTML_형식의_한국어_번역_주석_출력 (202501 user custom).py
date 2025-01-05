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

# デフォルトとして使用するJSONファイルのパス
default_file_path_json0 = "./files_needed_to_get_replacements_list_json_format/replacements_list_for_2char_Korean.json"
default_file_path_json1 = "./files_needed_to_get_replacements_list_json_format/最終的な置換用のリスト(replacements_final_list)_Korean.json"

# まずはサンプルJSONファイルをダウンロードできるようにする
st.write("## 샘플 JSON 파일 다운로드")

with open(default_file_path_json0, "rb") as file:
    st.download_button(
        label="샘플 JSON 파일 0 다운로드 (replacements_list_for_2char_Korean)",
        data=file,
        file_name="replacements_list_for_2char_Korean.json",
        mime="application/json"
    )

with open(default_file_path_json1, "rb") as file:
    st.download_button(
        label="샘플 JSON 파일 1 다운로드 (replacements_final_list_Korean)",
        data=file,
        file_name="replacements_final_list_Korean.json",
        mime="application/json"
    )

# ユーザーが独自のファイルをアップロードするかどうかの確認
st.write("## JSON 파일 업로드 (선택사항)")

# 1つ目のJSONファイル
uploaded_json0 = st.file_uploader(
    "upload your JSON file for 'replacements_list_for_2char_Korean'",
    type=["json"]
)
if uploaded_json0 is not None:
    # ユーザーがアップロードしたファイルを使用
    imported_data_replacements_list_for_2char = json.load(uploaded_json0)
    st.write("JSON 파일 0이 업로드되었습니다.")
else:
    # アップロードがなければデフォルトファイルを使用
    with open(default_file_path_json0, "r", encoding="utf-8") as f:
        imported_data_replacements_list_for_2char = json.load(f)
    st.write("기본 JSON 파일 0을 사용합니다.")

# 2つ目のJSONファイル
uploaded_json1 = st.file_uploader(
    "JSON 파일을 업로드하세요: '최종 교체 리스트 (replacements_final_list)_Korean'",
    type=["json"]
)
if uploaded_json1 is not None:
    # ユーザーがアップロードしたファイルを使用
    replacements_final_list_2 = json.load(uploaded_json1)
    st.write("JSON 파일 1이 업로드되었습니다.")
else:
    # アップロードがなければデフォルトファイルを使用
    with open(default_file_path_json1, "r", encoding="utf-8") as g:
        replacements_final_list_2 = json.load(g)
    st.write("기본 JSON 파일 1을 사용합니다.")


# プレースホルダーを用いた文字列置換関数
def enhanced_safe_replace_func_expanded_for_2char_roots(text, replacements, imported_data_replacements_list_for_2char):
    valid_replacements = {}
    for old, new, placeholder in replacements:
        if old in text:
            text = text.replace(old, placeholder)# 置換前の文字列を一旦プレースホルダーに置き換える。
            valid_replacements[placeholder] = new
# ここで、2文字の語根の置換を実施することとした(202412の変更)。  &%
    valid_replacements_ABC = {}
    for old, new, placeholder in imported_data_replacements_list_for_2char:
        if old in text:
            text = text.replace(old, placeholder)
            valid_replacements_ABC[placeholder] = new
    valid_replacements_ABC_2 = {}
    for old, new, placeholder in imported_data_replacements_list_for_2char:
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
placeholders = load_placeholders('./files_needed_to_get_replacements_list_json_format/placeholders_&%1854&%-&%9834&%_文字列置換skip用.txt')

# プレースホルダーを用いた文字列置換関数
def enhanced_safe_replace_func_expanded_for_2char_roots(text, replacements, imported_data_replacements_list_for_2char):
    valid_replacements = {}
    for old, new, placeholder in replacements:
        if old in text:
            text = text.replace(old, placeholder)# 置換前の文字列を一旦プレースホルダーに置き換える。
            valid_replacements[placeholder] = new
# ここで、2文字の語根の置換を実施することとした(202412の変更)。  &%
    valid_replacements_ABC = {}
    for old, new, placeholder in imported_data_replacements_list_for_2char:
        if old in text:
            text = text.replace(old, placeholder)
            valid_replacements_ABC[placeholder] = new
    valid_replacements_ABC_2 = {}
    for old, new, placeholder in imported_data_replacements_list_for_2char:
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




st.title("에스페란토_어근_위에_HTML_형식의_한국어_번역_주석_출력")
# st.caption('에스페란토_어근_위에_HTML_형식의_한국어_번역_주석_출력')


text3=""
with st.form(key='profile_form'):
    letter_type = st.radio('출력 문자 형식', ('위첨자 문자', 'x 형식', '^ 형식'))
    sentence = st.text_area("세계어 문장")
    st.markdown("""“%%”로 앞뒤를 감싸면 (“%%<50자 이내의 문자열>%%” 형식), “%%”로 감싸진 부분은 한자화하지 않고 원래 그대로 유지할 수 있습니다.""")

    submit_btn = st.form_submit_button('보내기')
    cancel_btn = st.form_submit_button('취소')
    if submit_btn:
        replaced_text = replace_esperanto_chars(sentence, esperanto_to_x)

        replacements_list_for_intact_parts = create_replacements(replaced_text, placeholders)
        sorted_replacements_list_for_intact_parts = sorted(replacements_list_for_intact_parts, key=lambda x: len(x[0]), reverse=True)
        for original, place_holder_ in sorted_replacements_list_for_intact_parts:
            replaced_text = replaced_text.replace(original, place_holder_)
        text3 = enhanced_safe_replace_func_expanded_for_2char_roots(replaced_text, replacements_final_list_2, imported_data_replacements_list_for_2char)# ここが一番メインの置換　⇑では"%%"で囲まれた部分をプレースホルダーに置き換える作業を、⇓では、プレースホルダーに置き換えられた、"%%"で囲まれた部分を元の文字列に戻す作業を行っている。
        for original, place_holder_ in sorted_replacements_list_for_intact_parts:
            text3 = text3.replace(place_holder_, original.replace("%%",""))
        # ⇓出力文字形式の変換
        if letter_type == '위첨자 문자':
            text3 = replace_esperanto_chars(text3, x_to_jijofu)
        elif letter_type == '^ 형식':
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
        label="텍스트 다운로드",
        data=to_download,
        file_name="processed_text.html",
        mime="text/plain"
    )




# コメント欄の追加
# st.sidebar.title("コメント欄")
# comments = st.sidebar.text_area("ご意見・ご感想をお聞かせください")



# 連絡先の追加
st.title("앱의 GitHub 저장소")
st.markdown("https://github.com/Takatakatake/Esperanto_kanjika_20240310/tree/main")
