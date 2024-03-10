
import streamlit as st
import re
import io

# 置換用の辞書
esperanto_to_x = {
    "ĉ": "cx", "ĝ": "gx", "ĥ": "hx", "ĵ": "jx", "ŝ": "sx", "ŭ": "ux",
    "Ĉ": "Cx", "Ĝ": "Gx", "Ĥ": "Hx", "Ĵ": "Jx", "Ŝ": "Sx", "Ŭ": "Ux",
    "c^": "cx", "g^": "gx", "h^": "hx", "j^": "jx", "s^": "sx", "u^": "ux",
    "C^": "Cx", "G^": "Gx", "H^": "Hx", "J^": "Jx", "S^": "Sx", "U^": "Ux"
}
x_to_jijofu={'cx': 'ĉ', 'gx': 'ĝ', 'hx': 'ĥ', 'jx': 'ĵ', 'sx': 'ŝ', 'ux': 'ŭ', 'Cx': 'Ĉ',
             'Gx': 'Ĝ', 'Hx': 'Ĥ', 'Jx': 'Ĵ', 'Sx': 'Ŝ', 'Ux': 'Ŭ'}
x_to_hat={'cx': 'c^', 'gx': 'g^', 'hx': 'h^', 'jx': 'j^', 'sx': 's^', 'ux': 'u^', 'Cx': 'C^',
          'Gx': 'G^', 'Hx': 'H^', 'Jx': 'J^', 'Sx': 'S^', 'Ux': 'U^'}

def replace_esperanto_chars(text,letter_dictionary):
    # 各エスペラント文字をX形式に置換
    for esperanto_char, x_char in letter_dictionary.items():
        text = text.replace(esperanto_char, x_char)
    return text

# 置換実行
# replaced_text = replace_esperanto_chars(text,esperanto_to_x)
# replaced_text =replace_esperanto_chars(text,x_to_jijofu)
# replaced_text =replace_esperanto_chars(text,x_to_hat)

with open('No.10000_79999.txt', 'r') as file:
    loaded_strings = [line.strip() for line in file]


hanzi_level=3
# hanzi_level1=['lv1','形1','形2','形3','形4','形5','数1','数4','接1','前1','代1','頭1','動2','動3','動4','動5','尾1','副1','副2','名2','名3','名4','名5']
# hanzi_level2=['lv1','lv2','間7','形1','形2','形3','形4','形5','形6','形7','形8','数1','数4','接1','接8','前1','前7','代1','頭1','動2','動3','動4','動5','動6','動7','動8','尾1','副1','副2','副6','副7','副8','名2','名3','名4','名5','名6','名7','名8']
# hanzi_level3=['lv1','lv2','lv3','間7','間o','擬f','形1','形2','形3','形4','形5','形6','形7','形8','形9','形f','形o','数1','数4','接1','接8','前1','前7','代1','頭1','頭9','動2','動3','動4','動5','動6','動7','動8','動9','動f','動n','動o','尾1','尾9','副1','副2','副6','副7','副8','副9','副b','副f','名2','名3','名4','名5','名6','名7','名8','名9','名b','名f','名i','名n','名o','略f']
Hanzi_Level=[['lv1','形1','形2','形3','形4','形5','数1','数4','接1','前1','代1','頭1','動2','動3','動4','動5','尾1','副1','副2','名2','名3','名4','名5'],['lv1','lv2','間7','形1','形2','形3','形4','形5','形6','形7','形8','数1','数4','接1','接8','前1','前7','代1','頭1','動2','動3','動4','動5','動6','動7','動8','尾1','副1','副2','副6','副7','副8','名2','名3','名4','名5','名6','名7','名8'],['lv1','lv2','lv3','間7','間o','擬f','形1','形2','形3','形4','形5','形6','形7','形8','形9','形f','形o','数1','数4','接1','接8','前1','前7','代1','頭1','頭9','動2','動3','動4','動5','動6','動7','動8','動9','動f','動n','動o','尾1','尾9','副1','副2','副6','副7','副8','副9','副b','副f','名2','名3','名4','名5','名6','名7','名8','名9','名b','名f','名i','名n','名o','略f']]
HANZILEVEL=Hanzi_Level[hanzi_level-1]

replacements_dict = {}##単語の追加は辞書式配列でするのが簡単
with open("全語根＿約11200個.txt", 'r', encoding='utf-8') as file:
    roots = file.readlines()
    for root in roots:
        root = root.strip()
        if len(root)>4:###5文字以上のみ 調節ポイント
            replacements_dict[root]=[root,len(root)*10000]##漢字化するかどうかで置換の優先順位が変わるので、漢字化しないものはすべての並べ替えが終わってから、
            

with open('./20240306世界语词根列表_0308.csv', 'r') as file:
    for line in file:
        line = line.strip()
        j = line.split(',')
        if len(j)==4:
            word,level,hanzi=j[0],j[1],j[2]
            if ("#" in word) or word=='':
                continue
            elif hanzi=='' or (level not in HANZILEVEL):
                replacements_dict[word]=[word,len(word)*10000]##ここで4文字以下を除く手もある。
            else:
                replacements_dict[word]=[hanzi+word+")",len(word)*10000+5000]##実際に漢字化するものを優先するため        
            
with open('後から加える語根リスト(優先順位も決められる).txt', 'r') as file:
    for line in file:
        line = line.strip()
        j = line.split(',')
        if len(j)==4:
            word,level,hanzi,priority=j[0],j[1],j[2],j[3]
            if level in HANZILEVEL:
                if word==hanzi:
                    replacements_dict[word]=[hanzi,int(priority)]##一旦整数に変えておく。(どちらでも良い)
                else:
                    replacements_dict[word]=[hanzi+word+')',int(priority)]##一旦整数に変えておく。(どちらでも良い)          


pre_replacements=[]
for old,new in replacements_dict.items():
    pre_replacements.append((old,new[0],new[1]))
    if (24000 <= new[1] <= 26000) or (34000 <= new[1] <= 36000) or (44000 <= new[1] <= 46000):##調節　実際に漢字化する3,4文字のエスペラント語根のみ
        for aiueo in list("aiueo"):
            pre_replacements.append((old+aiueo,new[0]+aiueo,new[1]))
            
pre_replacements2=[]
for old,new,priority in pre_replacements:
    pre_replacements2.append((old,new,priority))
    pre_replacements2.append((old.upper(),new.upper(),priority))
    pre_replacements2.append((old.capitalize(),new.capitalize(),priority))

pre_replacements3 = sorted(pre_replacements2, key=lambda x: x[2], reverse=True)

replacements=[]
for kk in range(len(pre_replacements3)):
    replacements.append([pre_replacements3[kk][0],pre_replacements3[kk][1],loaded_strings[kk]])
    
def safe_replace(text, replacements):
    # 必要な置換を記録するための辞書を初期化
    valid_replacements = {}
    # テキスト内の各置換対象文字列をチェックし、プレースホルダーに置換
    for old, new, placeholder in replacements:
        if old in text:
            text = text.replace(old, placeholder)
            # この置換が後で実際に行う必要があることを辞書に記録
            valid_replacements[placeholder] = new
    # プレースホルダーを実際の新しい文字列に置換
    for placeholder, new in valid_replacements.items():
        text = text.replace(placeholder, new)

    return text



st.title("世界语汉字化")
st.caption('这是一个将世界语文本转换成汉字符号的网络应用程序。')

code = '''
import streamlit as st
'''
st.code(code,language='python')





#画像
from PIL import Image

image = Image.open('エスペラントの漢字化の理想図.png')
st.image(image)
##動画も可能

with st.form(key='profile_form'):
    # テキストボックス
    

    # ラジオボタン
    letter_type = st.radio('文字形式',('字上符','x形式','^形式'))###select_boxでもいい

    sentence = st.text_area('世界语句子')
    
    # ボタン
    submit_btn = st.form_submit_button('发送')
    cancel_btn = st.form_submit_button('取消')
    if submit_btn:
        replaced_text = replace_esperanto_chars(sentence,esperanto_to_x)
        # replaced_text = replace_esperanto_chars(text,esperanto_to_x)
# replaced_text =replace_esperanto_chars(text,x_to_jijofu)
# replaced_text =replace_esperanto_chars(text,x_to_hat)
        text=safe_replace(replaced_text, replacements)
        if letter_type=='字上符':   
            text = replace_esperanto_chars(text,x_to_jijofu)
        elif letter_type=='^形式':
            text = replace_esperanto_chars(text,x_to_hat)
        st.text_area("", text, height=300)
          
        
to_download = io.BytesIO(text.encode())
st.download_button(
label="下载文本",
data=to_download,
file_name="processed_text.txt",
mime="text/plain"
)

# print(name)

