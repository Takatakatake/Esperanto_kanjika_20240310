import streamlit as st
import re
import io

##世界语文本字符格式转换函数(エスペラント文の文字形式の変換関数)
esperanto_to_x = { "ĉ": "cx", "ĝ": "gx", "ĥ": "hx", "ĵ": "jx", "ŝ": "sx", "ŭ": "ux",
                   "Ĉ": "Cx", "Ĝ": "Gx", "Ĥ": "Hx", "Ĵ": "Jx", "Ŝ": "Sx", "Ŭ": "Ux",
                   "c^": "cx", "g^": "gx", "h^": "hx", "j^": "jx", "s^": "sx", "u^": "ux",
                    "C^": "Cx", "G^": "Gx", "H^": "Hx", "J^": "Jx", "S^": "Sx", "U^": "Ux"}
x_to_jijofu={'cx': 'ĉ', 'gx': 'ĝ', 'hx': 'ĥ', 'jx': 'ĵ', 'sx': 'ŝ', 'ux': 'ŭ', 'Cx': 'Ĉ',
             'Gx': 'Ĝ', 'Hx': 'Ĥ', 'Jx': 'Ĵ', 'Sx': 'Ŝ', 'Ux': 'Ŭ'}
x_to_hat={'cx': 'c^', 'gx': 'g^', 'hx': 'h^', 'jx': 'j^', 'sx': 's^', 'ux': 'u^', 'Cx': 'C^',
          'Gx': 'G^', 'Hx': 'H^', 'Jx': 'J^', 'Sx': 'S^', 'Ux': 'U^'}

def replace_esperanto_chars(text,letter_dictionary):
    for esperanto_char, x_char in letter_dictionary.items():
        text = text.replace(esperanto_char, x_char)
    return text

# 用于测试的世界语文本(テスト用のエスペラント文)
text = "Ĝis revido! Mia nomo estas Ĵoĥano. Ĉu vi ŝatas ĥorojn? -Ne, mi s^tas felic^on. C^ S^ H^ c^ s^ h^  Ĉ Ĝ  Gxis revido! Mia nomo estas Jxohxano. Cxu vi sxatas hxorojn? -Ne, mi sxtas felicxon. Cx Sx Hx cx sx hx  Cx Gx"

## 世界语文本字符格式的转换(エスペラント文の文字形式の変換)
# replaced_text = replace_esperanto_chars(text,esperanto_to_x)
# replaced_text =replace_esperanto_chars(text,x_to_jijofu)
# replaced_text =replace_esperanto_chars(text,x_to_hat)

with open('No.10000_500000.txt', 'r') as file:##在汉字转换时预先加载用作"占位符"的文件。(漢字変換時に用いる"place holder"ファイルを予め読み込んでおく。)
    loaded_strings = [line.strip() for line in file]


hanzi_level=3##汉字转换的级别设置。'lv1'大约有650个世界语词根会被转换，'lv2'大约有1650个，'lv3'则大约有2650个。
##漢字変換のレベル設定。　'lv1'では650個程度のエスペラント語根が、'lv2'では1650個程度が、'lv3'では2650個程度が、漢字変換される。
# hanzi_level1=['lv1','形1','形2','形3','形4','形5','数1','数4','接1','前1','代1','頭1','動2','動3','動4','動5','尾1','副1','副2','名2','名3','名4','名5']
# hanzi_level2=['lv1','lv2','間7','形1','形2','形3','形4','形5','形6','形7','形8','数1','数4','接1','接8','前1','前7','代1','頭1','動2','動3','動4','動5','動6','動7','動8','尾1','副1','副2','副6','副7','副8','名2','名3','名4','名5','名6','名7','名8']
# hanzi_level3=['lv1','lv2','lv3','間7','間o','擬f','形1','形2','形3','形4','形5','形6','形7','形8','形9','形f','形o','数1','数4','接1','接8','前1','前7','代1','頭1','頭9','動2','動3','動4','動5','動6','動7','動8','動9','動f','動n','動o','尾1','尾9','副1','副2','副6','副7','副8','副9','副b','副f','名2','名3','名4','名5','名6','名7','名8','名9','名b','名f','名i','名n','名o','略f']
Hanzi_Level=[['lv1','形1','形2','形3','形4','形5','数1','数4','接1','前1','代1','頭1','動2','動3','動4','動5','尾1','副1','副2','名2','名3','名4','名5'],['lv1','lv2','間7','形1','形2','形3','形4','形5','形6','形7','形8','数1','数4','接1','接8','前1','前7','代1','頭1','動2','動3','動4','動5','動6','動7','動8','尾1','副1','副2','副6','副7','副8','名2','名3','名4','名5','名6','名7','名8'],['lv1','lv2','lv3','間7','間o','擬f','形1','形2','形3','形4','形5','形6','形7','形8','形9','形f','形o','数1','数4','接1','接8','前1','前7','代1','頭1','頭9','動2','動3','動4','動5','動6','動7','動8','動9','動f','動n','動o','尾1','尾9','副1','副2','副6','副7','副8','副9','副b','副f','名2','名3','名4','名5','名6','名7','名8','名9','名b','名f','名i','名n','名o','略f']]
HANZILEVEL=Hanzi_Level[hanzi_level-1]

replacements_dict = {}##将世界语词根的汉字替换列表以字典数组形式创建，因为这样可以容易地添加词根，所以是个不错的方法。(エスペラント語根の漢字置換リストは辞書式配列で作ると、語根の追加が容易にできるので良い。)
with open("全語根＿約11200個.txt", 'r', encoding='utf-8') as file:
    roots = file.readlines()
    for root in roots:
        root = root.strip()
        if len(root)>4:###只有5个字符以上的世界语词根。这是一个调整点。(5文字以上のエスペラント語根のみ。　調節ポイントである。)
            replacements_dict[root]=[root,len(root)*10000]##为每个世界语词根设置汉字替换后的字符串及其替换顺序。替换顺序的数字越大，越早替换。当然，内容经常会后续更改或更新。
            ##各エスペラント語根に対する漢字置換後の文字列とその置換順序を設定。　置換順序の数字が大きいほど、先に置換される。 もちろん、往々にして内容は後で変更・更新される。
# len(replacements_dict)
            

##读取世界语词根的汉字化列表，并更新上述创建的世界语所有词根的字典数组。(エスペラント語根の漢字化リストを読み込み、上記で作成したエスペラント全語根の辞書式配列を更新する。)
with open('世界语汉字表格_20240312.csv', 'r') as file:
    for line in file:
        line = line.strip()
        j = line.split(',')
        if len(j)==4:
            word,level,hanzi=j[0],j[1],j[2]
            if ("#" in word) or word=='':
                continue
            elif hanzi=='' or (level not in HANZILEVEL):
                replacements_dict[word]=[word,len(word)*10000]##为了提高汉字替换的准确性，这里也可以排除4个字符以下的世界语词根。
                ##漢字置換の精度を高めるため、ここで4文字以下のエスペラント語根を除く方法もありえる。
            elif any(keyword in level for keyword in ['形', '名', '動', '副']):
                replacements_dict[word]=[hanzi+'('+word+')',len(word)*10000+5000]##为了优先于不直接转换的世界语词根进行汉字替换，将替换顺序加+5000~(+4600,+4800,+5000)。
                ##実際に漢字置換するエスペラント語根をそのまま変換しないエスペラント語根より優先するため、置換順序を+5000~(+4600,+4800,+5000)する。
            elif any(keyword in level for keyword in ['尾','数','前']):
                replacements_dict[word]=[hanzi+'('+word+')',len(word)*10000+4800]##为了下述的"提高汉字替换准确性的工夫"，根据世界语词根的词性，稍微调整替换顺序。(後述の"漢字置換の精度を高める工夫"のために、エスペラント語根の品詞によって、置換順序を多少前後させる。)
                ##+5000表示强烈应用"提高汉字替换准确性的工夫"，+4800表示弱化应用，+4600表示不应用。
                ##+5000は"漢字置換の精度を高める工夫"を強く適用、+4800は"漢字置換の精度を高める工夫"を弱く適用、+4600は"漢字置換の精度を高める工夫"を適用しない。
            elif word=='oni' or word=='sxi' or word=='gxi':##在代词中，只有这三个是特别的，为了弱化应用下述的"提高汉字替换准确性的工夫"，加4800。(代名詞の中でこの3つだけは特別で、後述の"漢字置換の精度を高める工夫"を弱く適用するため、+4800する。)
                replacements_dict[word]=[hanzi+'('+word+')',len(word)*10000+4800]
            else:
                replacements_dict[word]=[hanzi+'('+word+')',len(word)*10000+4600]##其他进行汉字替换的世界语词根不应用"提高汉字替换准确性的工夫"，因此加4600。(その他の漢字置換するエスペラント語根は、"漢字置換の精度を高める工夫"を適用しないので、+4600する。)
                
##以下では、ユーザー設定ファイル(後から加える語根リスト(優先順位も決められる).txt)の読み込みを行っている。ユーザーは既存のファイル(エスペラント語根の漢字化リスト)を直接変更することなく、
##"'エスペラント語根'、'エスペラント語根のレベル'、'置換漢字'、'置換順序'"を新たに設定することができ、なおかつその設定は既存のファイル(エスペラント語根の漢字化リスト)よりも優先される。
##在下文中，正在进行用户设置文件（後から加える語根リスト(優先順位も決められる).txt）的读取。
##用户无需直接修改现有文件（世界语词根的汉字化列表），即可新设定“'世界语词根'、'世界语词根的级别'、'替换汉字'、'替换顺序'”，而且这些设置将优先于现有文件（世界语词根的汉字化列表）。

with open('後から加える語根リスト(優先順位も決められる).txt', 'r') as file:
    for line in file:
        line = line.strip()
        j = line.split(',')
        if len(j)==4:
            word,level,hanzi,priority=j[0],j[1],j[2],j[3]
            if level in HANZILEVEL:
                if word==hanzi:
                    replacements_dict[word]=[hanzi,int(priority)]#priority应改为int类型。(priorityはint型に変えておく。)
                else:
                    replacements_dict[word]=[hanzi+'('+word+')',int(priority)]
                    
#为了提高汉字替换的准确性，在“弱应用”中，将'a,i,u,e,o,j,n'添加到词尾，在“强应用”中，则在词根的开头和结尾添加前缀和后缀，并将这些形式新加入到世界语词根的汉字替换列表中。
#"漢字置換の精度を高める工夫"の'弱い適用'では語尾に'a,i,u,e,o,j,n'を、'強い適用'では語頭と語尾に接頭辞と接尾辞を追加した形をエスペラント語根の漢字置換リストに新たに追加する。
# prefix_2l={'bo':'bo', 'ek':'ek', 'ge':'ge', 're':'re'}
# prefix_3l={'cxef':'cxef', 'dis':'dis', 'eks':'eks', 'for':'for', 'mal':'mal', 'post':'post'}
# suffix_2l={'as':'as', 'is':'is', 'os':'os', 'us':'us', 'um':'um','at':'at','it':'it','ot':'ot', 'ad':'ad','an':'an','ar':'ar','ec':'ec', 'eg':'eg',	'ej':'ej', 'em':'em', 'er':'er', 'et':'et',	'id':'id', 'ig':'ig', 'il':'il', 'in':'in', 'on':'on', 'op':'op', 'uj':'uj', 'ul':'ul'}
# suffix_3l={'acx':'acx',	'ajx':'ajx'	, 'ebl':'ebl',	'end':'end','estr':'estr','igx':'igx','ind':'ind','ing':'ing','ism':'ism','ist':'ist','obl':'obl','ant':'ant','int':'int','ont':'ont'}
# prefix_2l_2={'bo': 'bo', 'ek': 'ek', 'ge': 'ge', 're': 're'}
# prefix_3l_2={'cxef': '首(cxef)','dis': '散(dis)','eks': '前(eks)','for': '离(for)','mal': '非(mal)','post': '后(post)'}
# suffix_2l_2={'as':'as', 'is':'is', 'os':'os', 'us':'us', 'um':'um','at':'at','it':'it','ot':'ot', 'ad':'ad','an':'an','ar':'ar','ec':'ec', 'eg':'eg',	'ej':'ej', 'em':'em', 'er':'er', 'et':'et',	'id':'id', 'ig':'ig', 'il':'il', 'in':'in', 'on':'on', 'op':'op', 'uj':'uj', 'ul':'ul'}
# suffix_3l_2={'acx': '劣(acx)','ajx': '物(ajx)','ebl': '能(ebl)','end': '必(end)','estr': '长(estr)','igx': '成(igx)','ind': '价(ind)','ing': '壳(ing)','ism': '义(ism)','ist': '家(ist)','obl': '倍(obl)','ant': 'ant','int': 'int','ont': 'ont'}
# suffix_3l_2={}
# for d1,d2 in suffix_3l.items():
#     suffix_3l_2[d1]=safe_replace(d2, replacements)
# suffix_3l_2
# prefix_3l_2={}
# for d1,d2 in prefix_3l.items():
#     prefix_3l_2[d1]=safe_replace(d2, replacements)
#prefix_3l_2
                    
prefix_2l_2={'ek': 'ek', 're': 're'}
prefix_3l_2={'dis': '散(dis)','for': '离(for)','mal': '非(mal)'}
suffix_2l_2={'as':'as', 'is':'is', 'os':'os', 'us':'us', 'um':'um','at':'at','it':'it','ot':'ot', 'ad':'ad','an':'an','ar':'ar','ec':'ec', 'eg':'eg',	'ej':'ej', 'em':'em', 'er':'er', 'et':'et', 'ig':'ig', 'il':'il', 'in':'in', 'uj':'uj', 'ul':'ul'}
suffix_3l_2={'acx': '劣(acx)','ajx': '物(ajx)','ebl': '能(ebl)','end': '必(end)','estr': '长(estr)','igx': '成(igx)','ind': '价(ind)','ism': '义(ism)','ist': '家(ist)','ant': 'ant','int': 'int','ont': 'ont'}       

###最重要的巧思点
###一番の工夫ポイント

root_de_fusiyo=['min','amas','mas','vin','boj','tas','lin']##几乎仅用于词根本身，容易导致误转换的世界语词根列表。(語根だけで用いることが殆どなく、誤変換の要因になりやすいエスペラント語根のリスト。)
pre_replacements=[]
for old,new in replacements_dict.items():
    if old not in root_de_fusiyo:
        pre_replacements.append((old,new[0],new[1]))
    if (24500 <= new[1] <= 24700) or (34500 <= new[1] <= 34700) or (44500 <= new[1] <= 44700):
        continue
    if (24700 <= new[1] <= 24900) or (34700 <= new[1] <= 34900) or (44700 <= new[1] <= 44900) or (54700 <= new[1] <= 54900):##“提高汉字替换准确性的技巧”之“弱应用”：将'a,i,u,e,o,j,n'添加至词尾的形式新加入到世界语词根的汉字替换列表中。
        #"漢字置換の精度を高める工夫"の'弱い適用':語尾に'a,i,u,e,o,j,n'を追加した形をエスペラント語根の漢字置換リストに新たに追加する。
        for aiueo in list("aiueojn"):
            pre_replacements.append((old+aiueo,new[0]+aiueo,new[1]+10000))
    if (24900 <= new[1] <= 25100) or (34900 <= new[1] <= 35100) or (44900 <= new[1] <= 45100) or (54900 <= new[1] <= 55100):##“提高汉字替换准确性的技巧”之“强应用”：将前缀和后缀添加至词头和词尾的形式新加入到世界语词根的汉字替换列表中。
        #"漢字置換の精度を高める工夫"の'強い適用':語頭と語尾に接頭辞と接尾辞を追加した形をエスペラント語根の漢字置換リストに新たに追加する。
        for d1,d2 in suffix_3l_2.items():
            pre_replacements.append((old+d1,new[0]+d2,new[1]+20000))#本来是+30000的，但暂时设为+20000。(本来は+30000だが、+20000にしておく。)
        for d1,d2 in prefix_3l_2.items():
            pre_replacements.append((d1+old,d2+new[0],new[1]+20000))#本来是+30000的，但暂时设为+20000。(本来は+30000だが、+20000にしておく。)           
        for d1,d2 in suffix_2l_2.items():
            pre_replacements.append((old+d1,new[0]+d2,new[1]+20000))
        for d1,d2 in prefix_2l_2.items():
            pre_replacements.append((d1+old,d2+new[0],new[1]+20000))       
        for aiueo in list("aiueojn"):
            pre_replacements.append((old+aiueo,new[0]+aiueo,new[1]+10000))            
            
##对应'大写字母'、'小写字母'、'句首仅大写字母'的情况。('大文字'、'小文字'、'文頭だけ大文字'のケースに対応。)
pre_replacements2=[]
for old,new,priority in pre_replacements:
    pre_replacements2.append((old,new,priority))
    pre_replacements2.append((old.upper(),new.upper(),priority))
    pre_replacements2.append((old.capitalize(),new.capitalize(),priority))

pre_replacements3 = sorted(pre_replacements2, key=lambda x: x[2], reverse=True)##按照替换顺序数字的大小顺序进行排序。(置換順序の数字の大きさ順にソート。)


#确认世界语词根的汉字替换列表内容。按照'世界语词根'、'替换汉字'、'替换顺序'的顺序排列。
#エスペラント語根の漢字置換リストの内容を確認。'エスペラント語根'、'置換漢字'、'置換順序'の順に並べられている。
# with open("pre_replacements3.txt", 'w', encoding='utf-8') as file:
#     for old,new,priority in pre_replacements3:
#         file.write(f'{old},{new},{priority}\n')

##按照'世界语词根'、'替换汉字'、'占位符'的顺序排列，创建用于最终替换的"replacements"列表。
##'エスペラント語根'、'置換漢字'、'place holder'の順に並べ、最終的な置換に用いる"replacements"リストを作成。
replacements=[]
for kk in range(len(pre_replacements3)):
    replacements.append([pre_replacements3[kk][0],pre_replacements3[kk][1],loaded_strings[kk]])
    
##用于替换的函数。尝试了正则表达式、C++等多种形式的替换，但使用Python中的'占位符'进行替换，处理速度最快。（而且非常简单易懂。）
##置換に用いる関数。正規表現、C++など様々な形式の置換を試したが、pythonで'place holder'を用いる形式の置換が、最も処理が高速であった。(しかも大変シンプルでわかりやすい。)
def safe_replace(text, replacements):
    valid_replacements = {}
    # 置换对象(old)暂时替换为'占位符'  (置換対象(old)を'place holder'に一時的に置換)
    for old, new, placeholder in replacements:
        if old in text:
            text = text.replace(old, placeholder)
            valid_replacements[placeholder] = new#记录需要稍后重新替换为替换后字符串(new)的'占位符'到字典(valid_replacements)中。
            # 後で置換後の文字列(new)に置換し直す必要がある'place holder'を辞書(valid_replacements)に記録しておく。
    # 将'占位符'替换为替换后的字符串(new)。  ('place holder'を置換後の文字列(new)に置換)
    for placeholder, new in valid_replacements.items():
        text = text.replace(placeholder, new)
    return text



st.title("世界语汉字化")
st.caption('这是一个将世界语文本转换成汉字符号的网络应用程序。')





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

