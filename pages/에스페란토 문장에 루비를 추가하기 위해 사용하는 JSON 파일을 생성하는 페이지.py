
import streamlit as st
import pandas as pd
import io
import os
import re
import json
import unicodedata

# サンプルファイルのパス
file_path0 = './files_needed_to_get_replacements_list_json_format/韓国語訳ルビリスト_202501.csv'
# ファイルを読み込む
with open(file_path0, "rb") as file:
    btn = st.download_button(
            label="샘플 CSV 파일 0 다운로드(한국어 번역 루비 리스트)",
            data=file,
            file_name="한국어 번역 루비 리스트_202501.csv",
            mime="text/csv"
        )

def capitalize_rt_tag(match):
    rt_start, rt_word, rt_end = match.groups()
    return rt_start + rt_word.capitalize() + rt_end
def capitalize_according_to_condition_htmlruby(new_text):
    if new_text.startswith('<ruby>'):
        # <で始まる場合、最初の<rt>タグ内の最初の文字を大文字にする
        new_text = re.sub(r'(<ruby>)(.*?)(<rt)', capitalize_rt_tag, new_text, count=1)
    else:
        # <で始まらない場合、new_textの最初の文字を大文字にする
        new_text = new_text[0].upper() + new_text[1:]
    
    return new_text

# file_path2 = './files_needed_to_get_replacements_list_json_format/Mingeo_san_hanziization.csv' 
# with open(file_path2, "rb") as file:
#     btn = st.download_button(
#             label="下载示例CSV文件2(中国世界语者杨先生(Mingeo,知乎)创建的世界语词根和汉字对应列表)",
#             data=file,
#             file_name="sample_file2.csv",
#             mime="text/csv"
#         )


# 文字列の幅を取得するための関数　全角文字は2、半角文字は1を返す。
def get_character_width(char):
    if unicodedata.east_asian_width(char) in 'FWA':
        return 2
    else:
        return 1
# 文字列の全体幅を取得するための関数　全角文字は2、半角文字は1として計算する
def get_string_width(s):
    return sum(get_character_width(char) for char in s)


# ユーザーが選択した出力形式を出力するための関数
def output_format(main_text, ruby_content, format_type):
    if format_type == 'HTML 형식＿루비 크기 조절':
        if get_string_width(main_text)/get_string_width(ruby_content)<(9/25):
            return '<ruby>{}<rt class="ruby-S_S_S">{}</rt></ruby>'.format(main_text, ruby_content)
        elif  get_string_width(main_text)/get_string_width(ruby_content)<(21/40):
            return '<ruby>{}<rt class="ruby-M_M_M">{}</rt></ruby>'.format(main_text, ruby_content)
        elif  get_string_width(main_text)/get_string_width(ruby_content)<(7/8):
            return '<ruby>{}<rt class="ruby-L_L_L">{}</rt></ruby>'.format(main_text, ruby_content)
        else:
            return '<ruby>{}<rt class="ruby-X_X_X">{}</rt></ruby>'.format(main_text, ruby_content)
    elif format_type == 'HTML形式':
        return '<ruby>{}<rt>{}</rt></ruby>'.format(main_text, ruby_content)
    elif format_type == '괄호 형식':
        return '{}({})'.format(main_text, ruby_content)
    elif format_type == '変換語文字列のみ(単純な置換)':
        return '{}'.format(ruby_content)

# ユーザーに出力形式を選んでもらう
format_type = st.selectbox(
    '출력 형식 선택:',
    ('HTML 형식＿루비 크기 조절', '괄호 형식')
)

# 例示
main_text = '汉字'
ruby_content = 'hanzi'
formatted_text = output_format(main_text, ruby_content, format_type)
st.write('포맷된 텍스트:', formatted_text)

# Streamlitでファイルアップロード機能を追加
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=['csv'])
if uploaded_file is not None:
    # Streamlitの環境でファイルを読み込むために必要な変更
    dataframe = pd.read_csv(uploaded_file)
    dataframe.to_csv("./files_needed_to_get_replacements_list_json_format/世界语词根列表＿user.csv", index=False)

    with open("./files_needed_to_get_replacements_list_json_format/PEJVO(世界语全部单词列表)全部について、词尾(a,i,u,e,o,n等)をカットし、コンマ(,)で隔てて品詞と併せて记录した列表(stem_with_part_of_speech_list).json", "r", encoding="utf-8") as g:
        stem_with_part_of_speech_list = json.load(g)

    # 上の作業で抽出した、'語末(a,i,e,o,n等)だけをカットした、完全に語根分解された状態の全単語リスト'(stem_with_part_of_speech_list)を(漢字)置換するための、(漢字)置換リストを作成していく。
    # "'語末(a,i,e,o,n等)だけをカットした、完全に語根分解された状態の全単語リスト'(stem_with_part_of_speech_list)を(漢字)置換し終えたリスト"こそが最終的な(漢字)置換リストの大元になる。
    # '既に完全に語根分解された状態の単語'が対象であれば、文字数の多い語根順に(漢字)置換するだけで、理論上完璧な精度の(漢字)置換ができるはず。
    # ただし、その完璧な精度の(漢字)置換のためにはあらかじめ"世界语全部单词列表_约44100个(原pejvo.txt)_utf8化_第二部分以後中心に修正_更に修正_最终版202412.txt"から"202412＿世界语全部单词列表_约44100个(原pejvo.txt)_utf8化_第二部分以後中心に修正_更に修正_最终版202412.txt＿から＿世界语全部词根_约11127个_202412＿を抽出.ipynb"を用いてエスペラントの全語根を抽出しておく必要がある。

    # 一旦辞書型を使う。(後で内容(value)を更新するため)
    temporary_replacements_dict={}
    with open("./files_needed_to_get_replacements_list_json_format/世界语全部词根_约11127个_202412.txt", 'r', encoding='utf-8') as file:
        # "世界语全部词根_约11127个_202412.txt"は"世界语全部单词列表_约44100个(原pejvo.txt)_utf8化_第二部分以後中心に修正_更に修正_最终版202412.txt"から"202412＿世界语全部单词列表_约44100个(原pejvo.txt)_utf8化_第二部分以後中心に修正_更に修正_最终版202412.txt＿から＿世界语全部词根_约11127个_202412＿を抽出.ipynb"を用いて抽出したエスペラントの全語根である。
        roots = file.readlines()
        for root in roots:
            root = root.strip()
            if not root.isdigit():# 混入していた数字の'10'と'7'を削除
                temporary_replacements_dict[root]=[root,len(root)]# 各エスペラント語根に対する'置換後の単語'(この作業では元の置換対象の語根のまま)と、その置換順序として、'置換対象の語根の文字数'を設定。　置換順序の数字が大きい('置換対象の語根の文字数が多い')ほど、先に置換されるようにする。


    ##上の作業に引き続き、"'単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(result)を漢字置換するための、漢字置換リスト"を作成していく。　
    ##ここでは自分で作成したエスペラント語根の漢字化リストを反映させる。

    input_file="./files_needed_to_get_replacements_list_json_format/世界语词根列表＿user.csv"
    # input_file="世界语汉字表格_20240312.csv"
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            j = line.split(',')
            if len(j)>=2:
                E_word,hanzi_or_meaning=j[0],j[1]
                if (hanzi_or_meaning!='') and (E_word!='') and ('#' not in E_word):
                    temporary_replacements_dict[E_word]=[output_format(E_word, hanzi_or_meaning, format_type),len(E_word)]#辞書型配列では要素(key)に対する値(value)を後から更新できることを利用している。


    # 辞書型をリスト型に戻した上で、文字数順に並び替え。
    # "'単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト(stem_with_part_of_speech_list)'を(漢字)置換するための、(漢字)置換リスト"を置換順序の数字の大きさ順(ここでは文字数順)にソート。
    temporary_replacements_list_1=[]
    for old,new in temporary_replacements_dict.items():
        temporary_replacements_list_1.append((old,new[0],new[1]))
    temporary_replacements_list_2 = sorted(temporary_replacements_list_1, key=lambda x: x[2], reverse=True)
    # '(漢字)置換リスト'の各置換に対してplaceholderを追加し、リスト'temporary_replacements_list_3'として完成させる。
    # placeholder法とは、既に置換を終えた文字列が後続の置換によって重複して置換されてしまうことを避けるために、その置換を終えた部分に一時的に無関係な文字列(placeholder)を置いておいて、
    #全ての置換が終わった後に、改めてその'無関係な文字列(placeholder)'から'目的の置換後文字列'に変換していく手法である。

    with open('./files_needed_to_get_replacements_list_json_format/placeholders_$20987$-$499999$.txt', 'r', encoding='utf-8') as file:##(漢字)置換時に用いる"placeholder"ファイルを予め読み込んでおく。
        imported_placeholders = [line.strip() for line in file]

    temporary_replacements_list_3=[]
    for kk in range(len(temporary_replacements_list_2)):
        temporary_replacements_list_3.append([temporary_replacements_list_2[kk][0],temporary_replacements_list_2[kk][1],imported_placeholders[kk]])


    ##置換に用いる関数。正規表現、C++など様々な形式の置換を試したが、pythonでplaceholderを用いる形式の置換が、最も処理が高速であった。(しかも大変シンプルでわかりやすい。)
    def safe_replace(text, replacements):
        valid_replacements = {}
        # 置換対象(old)をplaceholderに一時的に置換
        for old, new, placeholder in replacements:
            if old in text:
                text = text.replace(old, placeholder)
                valid_replacements[placeholder] = new# 後で置換後の文字列(new)に置換し直す必要があるplaceholderを辞書(valid_replacements)に記録しておく。
        #placeholderを置換後の文字列(new)に置換)
        for placeholder, new in valid_replacements.items():
            text = text.replace(placeholder, new)
        return text

    # このセルの処理が全体を通して一番時間がかかる(数十秒)
    # '単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(stem_with_part_of_speech_list)を実際にリスト'temporary_replacements_list_3'((漢字)置換リストの完成版)によって(漢字)置換。　
    # ここで作成される、"(漢字)置換し終えた辞書型配列"(pre_replacements_dict_1)が最終的な(漢字)置換リストの大元になる。
    # リスト'stem_with_part_of_speech_list'までは情報の損失は殆どないはず。

    pre_replacements_dict_1={}
    for j in stem_with_part_of_speech_list:##20秒ほどかかる。　先にリストの要素を全て結合して、一つの文字列にしてから(漢字)置換する方法を試しても(上述)、さほど高速化しなかった。
        if len(j)==2:##(j[0]がエスペラント語根、j[1]が品詞。)
            if len(j[0])>=2:##2文字以上のエスペラント語根のみが対象  3で良いのでは(202412)
                if j[0] in pre_replacements_dict_1:
                    if j[1] not in pre_replacements_dict_1[j[0]][1]:
                        pre_replacements_dict_1[j[0]] = [pre_replacements_dict_1[j[0]][0],pre_replacements_dict_1[j[0]][1] + ',' + j[1]]##複数品詞の追加  空白は必要ないのでは(2024/12)
                else:
                    pre_replacements_dict_1[j[0]]=[safe_replace(j[0], temporary_replacements_list_3),j[1]]##辞書敷配列の追加法

    keys_to_remove = ['domen', 'teren','posten']###後でdomen/o,domen/a,domen/e等を追加する。　→確認済み(24/12)
    for key in keys_to_remove:
        pre_replacements_dict_1.pop(key, None)  # 'None' はキーが存在しない場合に返すデフォルト
    
    ## pre_replacements_dict_1→pre_replacements_dict_2  ("'単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(stem_with_part_of_speech_list)を(漢字)置換し終えたリスト"(pre_replacements_dict_1)を最終的な(漢字)置換リストに成形していく。)
    ##pre_replacements_dict_1の'置換対象の単語'、'(漢字)置換後の単語'から"/"を抜く(html形式にしたい場合、"</rt></ruby>"は"/"を含むので要注意！)。
    ##新たに置換優先順位を表す数字を追加し((漢字)置換する単語は'文字数×10000'、(漢字)置換しない単語は'文字数×10000-3000')、辞書型配列pre_replacements_dict_2として保存。
    pre_replacements_dict_2={}
    for i,j in pre_replacements_dict_1.items():##(iが置換対象の単語、j[0]が(漢字)置換後の単語、j[1]が品詞。)
        if i==j[0]:##(漢字)置換しない単語  ⇓はhtml形式でなくてもしても大丈夫な処理なので、出力形式が'괄호 형식'や'変換語文字列のみ(単純な置換)'であっても心配無用。
            pre_replacements_dict_2[i.replace('/', '')]=[j[0].replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),j[1],len(i.replace('/', ''))*10000-3000]##(漢字)置換しない単語は優先順位を下げる
        else:
            pre_replacements_dict_2[i.replace('/', '')]=[j[0].replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),j[1],len(i.replace('/', ''))*10000]
    
    ### 基本的には动词に対してのみ活用語尾を追加し、置換対象の単語の文字数を増やす(置換の優先順位を上げる。)
    verb_suffix_2l={'as':'as', 'is':'is', 'os':'os', 'us':'us','at':'at','it':'it','ot':'ot', 'ad':'ad','igx':'igx','ig':'ig','ant':'ant','int':'int','ont':'ont'}
    ##接頭辞接尾時の追加については、主に动词が対象である。
    verb_suffix_2l_2={}
    for original_verb_suffix,replaced_verb_suffix in verb_suffix_2l.items():
        verb_suffix_2l_2[original_verb_suffix]=safe_replace(replaced_verb_suffix, temporary_replacements_list_3)

    ###一番の工夫ポイント(如何にして置換の優先順位を定め、置換精度を向上させるか。)
    ##基本は単語の文字数が多い順に置換していくことになるが、
    ##例えば、"置換対象の単語に接頭辞、接尾辞を追加し、単語の文字数を増やし、置換の優先順位を上げたものを、置換対象の単語として新たに追加する。"などが、置換精度を上げる方策として考えられる。
    ##しかし、いろいろ試した結果、动词に対してのみ活用語尾を追加し、置換対象の単語の文字数を増やす(置換の優先順位を上げる。)のが、ベストに近いことがわかった。

    ## pre_replacements_dict_1→pre_replacements_dict_2→pre_replacements_dict_3  ("'単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(stem_with_part_of_speech_list)を(漢字)置換し終えたリスト"(pre_replacements_dict_1)を最終的な(漢字)置換リストに成形していく。)
    unchangeable_after_creation_list=[]
    adj_1,adj_2,adj_3,adj_4=0,0,0,0
    ### pre_replacements_dict_3内での重複の検査をし、それを元に、以下のセルにおける修正がなされている。
    pre_replacements_dict_3={}
    # 辞書をコピーする
    pre_replacements_dict_2_copy = pre_replacements_dict_2.copy()##これがあるので、2回繰り返しするときは2個前のセルに戻ってpre_replacements_dict_2を作り直してからでないといけない。
    for i,j in pre_replacements_dict_2_copy.items():##j[0]:置換後の文字列　j[1]:品詞 j[2]:置換優先順位
        if (j[1] == "名词") and (len(i)<=6) and not(j[2]==60000 or j[2]==50000 or j[2]==40000 or j[2]==30000 or j[2]==20000):##名词だけで、6文字以下で、(漢字)置換しないやつ  ##置換ミスを防ぐための条件(20240614) altajo,aviso,malm,abes 固有名词対策  意味ふりがなのときは再検討
            for k in ["o"]:
                if not i+k in pre_replacements_dict_2_copy:
                    pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-2000]#実質8000 #既存でないものは優先順位を大きく下げる→普通の品詞接尾辞が既存でないという言い方はおかしい気もするが。(202412)
                ##elif j[0]+k != pre_replacements_dict_2_copy[i+k][0]:# ←本当はこちらの条件のほうが、既に存在してなおかつ語根分解も異なる単語を抽出して来れるため、より良い。
                ##else:##既に存在するのであれば、元々の語根分解を優先し、何もしない。                ## ['buro', 'haloo', 'tauxro', 'unesko']の4個
            pre_replacements_dict_2.pop(i, None)

    for i,j in pre_replacements_dict_2.items():##j[0]:置換後の文字列　j[1]:品詞 j[2]:置換優先順位
        if j[2]==20000:##2文字で(漢字)置換するやつ##len(i)<=2:#1文字は存在しないはずではある。
            ##基本的に非动词の2文字の語根単体を以て(漢字)置換することはない。　ただし、世界语全部单词_大约44100个(原pejvo.txt).txtに最初から含まれている2文字の語根は既に(漢字)置換されており、実際の(漢字)置換にも反映されることになる。
            ##2文字の語根でも、动词については活用語尾を追加することで、自動的に+2文字以上できるので追加した。
            if "名词" in j[1]:
                for k in ["o","on",'oj']:##"ojn"は不要か
                    if not i+k in pre_replacements_dict_2:
                        pre_replacements_dict_3[' '+i+k]=[' '+j[0]+k,j[2]+(len(k)+1)*10000-5000]
            if "形容词" in j[1]:
                for k in ["a","aj",'an']:##"ajn"は不要か  ##sia pian ,'an 'も不要
                    if not i+k in pre_replacements_dict_2:##if not なしのほうが良い
                        pre_replacements_dict_3[' '+i+k]=[' '+j[0]+k,j[2]+(len(k)+1)*10000-5000]
                    else:##if not なしのほうが良いというのは既に存在しようとしまいと新しく作った方の語根分解を優先するということ。if not を付けたとしても、elseの方でも同じ処理をするようにすれば何の問題もない。
                        pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-5000]# ここは空白なしにすることに(2412)
                        unchangeable_after_creation_list.append(i+k)# 新しく定めた語根分解が後で更新されてしまわないように、unchangeable_after_creation_list に追加。
                adj_1+=1
            if "副词" in j[1]:
                for k in ["e"]:
                    pre_replacements_dict_3[' '+i+k]=[' '+j[0]+k,j[2]+(len(k)+1)*10000-5000]
            if "动词" in j[1]:
                for k1,k2 in verb_suffix_2l_2.items():
                    if not i+k1 in pre_replacements_dict_2:##j[0]:置換後の文字列　j[1]:品詞 j[2]:置換優先順位
                        pre_replacements_dict_3[i+k1]=[j[0]+k2,j[2]+len(k1)*10000-3000]
                    elif j[0]+k2 != pre_replacements_dict_2[i+k1][0]:
                        pre_replacements_dict_3[i+k1]=[j[0]+k2,j[2]+len(k1)*10000-3000]# 新しく作った方の語根分解を優先する
                        print(i+k1,pre_replacements_dict_3[i+k1],[j[0]+k2,j[2]+len(k1)*10000-3000])
                        unchangeable_after_creation_list.append(i+k1)# 新しく定めた語根分解が後で更新されてしまわないように、unchangeable_after_creation_list に追加。
                for k in ["u ","i ","u","i"]:##动词の"u","i"単体の接尾辞は後ろが空白と決まっているので、2文字分増やすことができる。
                    if not i+k in pre_replacements_dict_2:
                        pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]
            continue

        else:
            if not i in unchangeable_after_creation_list:# unchangeable_after_creation_list に含まれる場合は除外。(上記で新しく定めた語根分解が更新されてしまわないようにするため。)
                pre_replacements_dict_3[i]=[j[0],j[2]]##品詞情報はここで用いるためにあった。以後は不要なので省いていく。
            if j[2]==60000 or j[2]==50000 or j[2]==40000 or j[2]==30000:##文字数が比較的少なく(<=5)、実際に(漢字)置換するエスペラント語根(文字数×10000)のみを対象とする 
                if "名词" in j[1]:##名词については形容词、副词と違い、(漢字)置換しないものにもoをつける。
                    for k in ["o","on",'oj']:
                        if not i+k in pre_replacements_dict_2:
                            pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]#既存でないものは優先順位を大きく下げる→普通の品詞接尾辞が既存でないという言い方はおかしい気がしてきた。(20240612)
                        elif j[0]+k != pre_replacements_dict_2[i+k][0]:
                            pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]# 新しく作った方の語根分解を優先する
                            unchangeable_after_creation_list.append(i+k)
                if "形容词" in j[1]:
                    for k in ["a","aj",'an']:
                        if not i+k in pre_replacements_dict_2:
                            pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]
                        elif j[0]+k != pre_replacements_dict_2[i+k][0]:
                            pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]# 新しく作った方の語根分解を優先する つまり、"an"は形容詞語尾として語根分解する。
                            unchangeable_after_creation_list.append(i+k)
                if "副词" in j[1]:
                    for k in ["e"]:
                        if not i+k in pre_replacements_dict_2:
                            pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]
                        elif j[0]+k != pre_replacements_dict_2[i+k][0]:
                            pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]# 新しく作った方の語根分解を優先する
                            unchangeable_after_creation_list.append(i+k)
                if "动词" in j[1]:
                    for k1,k2 in verb_suffix_2l_2.items():
                        if not i+k1 in pre_replacements_dict_2:
                            pre_replacements_dict_3[i+k1]=[j[0]+k2,j[2]+len(k1)*10000-3000]
                        elif j[0]+k2 != pre_replacements_dict_2[i+k1][0]:
                            pre_replacements_dict_3[i+k1]=[j[0]+k2,j[2]+len(k1)*10000-3000]# 新しく作った方の語根分解を優先する
                            unchangeable_after_creation_list.append(i+k1)
                    for k in ["u ","i ","u","i"]:##动词の"u","i"単体の接尾辞は後ろが空白と決まっているので、2文字分増やすことができる。
                        if not i+k in pre_replacements_dict_2:
                            pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]
                        elif j[0]+k != pre_replacements_dict_2[i+k][0]:
                            pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-3000]# 新しく作った方の語根分解を優先する
                            unchangeable_after_creation_list.append(i+k)
            elif len(i)>=3 and len(i)<=6:##3文字から6文字の語根で(漢字)置換しないもの　　結局2文字の語根で(漢字)置換しないものについては、完全に除外している。
                if "名词" in j[1]:##名词については形容词、副词と違い、(漢字)置換しないものにもoをつける。
                    for k in ["o"]:
                        if not i+k in pre_replacements_dict_2:
                            pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-5000]#実質3000#既存でないものは優先順位を大きく下げる→普通の品詞接尾辞が既存でないという言い方はおかしい気がしてきた。(20240612)
                if "形容词" in j[1]:
                    for k in ["a"]:
                        if not i+k in pre_replacements_dict_2:
                            pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-5000]
                if "副词" in j[1]:
                    for k in ["e"]:
                        if not i+k in pre_replacements_dict_2:
                            pre_replacements_dict_3[i+k]=[j[0]+k,j[2]+len(k)*10000-5000]

    AN=[['dietan', '/diet/an/', '/diet/an'], ['afrikan', '/afrik/an/', '/afrik/an'], ['movadan', '/mov/ad/an/', '/mov/ad/an'], ['akcian', '/akci/an/', '/akci/an'], ['montaran', '/mont/ar/an/', '/mont/ar/an'], ['amerikan', '/amerik/an/', '/amerik/an'], ['regnan', '/regn/an/', '/regn/an'], ['dezertan', '/dezert/an/', '/dezert/an'], ['asocian', '/asoci/an/', '/asoci/an'], ['insulan', '/insul/an/', '/insul/an'], ['azian', '/azi/an/', '/azi/an'], ['sxtatan', '/sxtat/an/', '/sxtat/an'], ['doman', '/dom/an/', '/dom/an'], ['montan', '/mont/an/', '/mont/an'], ['familian', '/famili/an/', '/famili/an'], ['urban', '/urb/an/', '/urb/an'], ['popolan', '/popol/an/', '/popol/an'], ['dekan', '/dekan/', '/dek/an'], ['partian', '/parti/an/', '/parti/an'], ['lokan', '/lok/an/', '/lok/an'], ['sxipan', '/sxip/an/', '/sxip/an'], ['eklezian', '/eklezi/an/', '/eklezi/an'], ['landan', '/land/an/', '/land/an'], ['orientan', '/orient/an/', '/orient/an'], ['lernejan', '/lern/ej/an/', '/lern/ej/an'], ['enlandan', '/en/land/an/', '/en/land/an'], ['kalkan', '/kalkan/', '/kalk/an'], ['estraran', '/estr/ar/an/', '/estr/ar/an'], ['etnan', '/etn/an/', '/etn/an'], ['euxropan', '/euxrop/an/', '/euxrop/an'], ['fazan', '/fazan/', '/faz/an'], ['polican', '/polic/an/', '/polic/an'], ['socian', '/soci/an/', '/soci/an'], ['societan', '/societ/an/', '/societ/an'], ['grupan', '/grup/an/', '/grup/an'], ['ligan', '/lig/an/', '/lig/an'], ['nacian', '/naci/an/', '/naci/an'], ['koran', '/koran/', '/kor/an'], ['religian', '/religi/an/', '/religi/an'], ['kuban', '/kub/an/', '/kub/an'], ['majoran', '/major/an/', '/major/an'], ['nordan', '/nord/an/', '/nord/an'], ['paran', 'paran', '/par/an'], ['parizan', '/pariz/an/', '/pariz/an'], ['parokan', '/parok/an/', '/parok/an'], ['podian', '/podi/an/', '/podi/an'], ['rusian', '/rus/i/an/', '/rus/ian'], ['satan', '/satan/', '/sat/an'], ['sektan', '/sekt/an/', '/sekt/an'], ['senatan', '/senat/an/', '/senat/an'], ['skisman', '/skism/an/', '/skism/an'], ['sudan', 'sudan', '/sud/an'], ['utopian', '/utopi/an/', '/utopi/an'], ['vilagxan', '/vilagx/an/', '/vilagx/an']]
    ON=[['duon', '/du/on/', '/du/on'], ['okon', '/ok/on/', '/ok/on'], ['nombron', '/nombr/on/', '/nombr/on'], ['patron', '/patron/', '/patr/on'], ['karbon', '/karbon/', '/karb/on'], ['ciklon', '/ciklon/', '/cikl/on'], ['aldon', '/al/don/', '/ald/on'], ['balon', '/balon/', '/bal/on'], ['baron', '/baron/', '/bar/on'], ['baston', '/baston/', '/bast/on'], ['magneton', '/magnet/on/', '/magnet/on'], ['beton', 'beton', '/bet/on'], ['bombon', '/bombon/', '/bomb/on'], ['breton', 'breton', '/bret/on'], ['burgxon', '/burgxon/', '/burgx/on'], ['centon', '/cent/on/', '/cent/on'], ['milon', '/mil/on/', '/mil/on'], ['kanton', '/kanton/', '/kant/on'], ['citron', '/citron/', '/citr/on'], ['platon', 'platon', '/plat/on'], ['dekon', '/dek/on/', '/dek/on'], ['kvaron', '/kvar/on/', '/kvar/on'], ['kvinon', '/kvin/on/', '/kvin/on'], ['seson', '/ses/on/', '/ses/on'], ['trion', '/tri/on/', '/tri/on'], ['karton', '/karton/', '/kart/on'], ['foton', '/fot/on/', '/fot/on'], ['peron', '/peron/', '/per/on'], ['elektron', '/elektr/on/', '/elektr/on'], ['drakon', 'drakon', '/drak/on'], ['mondon', '/mon/don/', '/mond/on'], ['pension', '/pension/', '/pensi/on'], ['ordon', '/ordon/', '/ord/on'], ['eskadron', 'eskadron', '/eskadr/on'], ['senton', '/sen/ton/', '/sent/on'], ['eston', 'eston', '/est/on'], ['fanfaron', '/fanfaron/', '/fanfar/on'], ['feston', '/feston/', '/fest/on'], ['flegmon', 'flegmon', '/flegm/on'], ['fronton', '/fronton/', '/front/on'], ['galon', '/galon/', '/gal/on'], ['mason', '/mason/', '/mas/on'], ['helikon', 'helikon', '/helik/on'], ['kanon', '/kanon/', '/kan/on'], ['kapon', '/kapon/', '/kap/on'], ['kokon', '/kokon/', '/kok/on'], ['kolon', '/kolon/', '/kol/on'], ['komision', '/komision/', '/komisi/on'], ['salon', '/salon/', '/sal/on'], ['ponton', '/ponton/', '/pont/on'], ['koton', '/koton/', '/kot/on'], ['kripton', 'kripton', '/kript/on'], ['kupon', '/kupon/', '/kup/on'], ['lakon', 'lakon', '/lak/on'], ['ludon', '/lu/don/', '/lud/on'], ['melon', '/melon/', '/mel/on'], ['menton', '/menton/', '/ment/on'], ['milion', '/milion/', '/mili/on'], ['milionon', '/milion/on/', '/milion/on'], ['nauxon', '/naux/on/', '/naux/on'], ['violon', '/violon/', '/viol/on'], ['trombon', '/trombon/', '/tromb/on'], ['senson', '/sen/son/', '/sens/on'], ['sepon', '/sep/on/', '/sep/on'], ['skadron', 'skadron', '/skadr/on'], ['stadion', '/stadion/', '/stadi/on'], ['tetraon', 'tetraon', '/tetra/on'], ['timon', '/timon/', '/tim/on'], ['valon', 'valon', '/val/on']]


    for an in AN:
        if an[1].endswith("/an/"):
            i2=an[1]
            i3 = re.sub(r"/an/$", "", i2)##正規表現を使わない,
            i4=i3+"/an/o"
            i5=i3+"/an/a"
            i6=i3+"/an/e"
            i7=i3+"/a/n/"
            pre_replacements_dict_3[i4.replace('/', '')]=[safe_replace(i4,temporary_replacements_list_3).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i4.replace('/', ''))-1)*10000+3000]
            pre_replacements_dict_3[i5.replace('/', '')]=[safe_replace(i5,temporary_replacements_list_3).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i5.replace('/', ''))-1)*10000+3000]
            pre_replacements_dict_3[i6.replace('/', '')]=[safe_replace(i6,temporary_replacements_list_3).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i6.replace('/', ''))-1)*10000+3000]
            pre_replacements_dict_3[i7.replace('/', '')]=[safe_replace(i7,temporary_replacements_list_3).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i7.replace('/', ''))-1)*10000+3000]
        else:
            i2=an[1]
            i2_2 = re.sub(r"an$", "", i2)##正規表現を使わないと、etn/a/n　において、etnのnまで削られてしまった。
            i3 = re.sub(r"an/$", "", i2_2)##正規表現を使わないと、etn/a/n　において、etnのnまで削られてしまった。
            i4=i3+"an/o"
            i5=i3+"an/a"
            i6=i3+"an/e"
            i7=i3+"/a/n/"
            pre_replacements_dict_3[i4.replace('/', '')]=[safe_replace(i4,temporary_replacements_list_3).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i4.replace('/', ''))-1)*10000+3000]
            pre_replacements_dict_3[i5.replace('/', '')]=[safe_replace(i5,temporary_replacements_list_3).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i5.replace('/', ''))-1)*10000+3000]
            pre_replacements_dict_3[i6.replace('/', '')]=[safe_replace(i6,temporary_replacements_list_3).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i6.replace('/', ''))-1)*10000+3000]
            pre_replacements_dict_3[i7.replace('/', '')]=[safe_replace(i7,temporary_replacements_list_3).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i7.replace('/', ''))-1)*10000+3000]


    for on in ON:
        if on[1].endswith("/on/"):
            i2=on[1]
            i3 = re.sub(r"/on/$", "", i2)##正規表現を使わないと、etn/a/n　において、etnのnまで削られてしまった。
            i4=i3+"/on/o"
            i5=i3+"/on/a"
            i6=i3+"/on/e"
            i7=i3+"/o/n/"
            pre_replacements_dict_3[i4.replace('/', '')]=[safe_replace(i4,temporary_replacements_list_3).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i4.replace('/', ''))-1)*10000+3000]
            pre_replacements_dict_3[i5.replace('/', '')]=[safe_replace(i5,temporary_replacements_list_3).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i5.replace('/', ''))-1)*10000+3000]
            pre_replacements_dict_3[i6.replace('/', '')]=[safe_replace(i6,temporary_replacements_list_3).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i6.replace('/', ''))-1)*10000+3000]
            pre_replacements_dict_3[i7.replace('/', '')]=[safe_replace(i7,temporary_replacements_list_3).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i7.replace('/', ''))-1)*10000+3000]
        else:
            i2=on[1]
            i2_2 = re.sub(r"on$", "", i2)##正規表現を使わないと、etn/a/n　において、etnのnまで削られてしまった。
            i3 = re.sub(r"on/$", "", i2_2)##正規表現を使わないと、etn/a/n　において、etnのnまで削られてしまった。
            i4=i3+"on/o"
            i5=i3+"on/a"
            i6=i3+"on/e"
            i7=i3+"/o/n/"
            pre_replacements_dict_3[i4.replace('/', '')]=[safe_replace(i4,temporary_replacements_list_3).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i4.replace('/', ''))-1)*10000+3000]
            pre_replacements_dict_3[i5.replace('/', '')]=[safe_replace(i5,temporary_replacements_list_3).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i5.replace('/', ''))-1)*10000+3000]
            pre_replacements_dict_3[i6.replace('/', '')]=[safe_replace(i6,temporary_replacements_list_3).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i6.replace('/', ''))-1)*10000+3000]
            pre_replacements_dict_3[i7.replace('/', '')]=[safe_replace(i7,temporary_replacements_list_3).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), (len(i7.replace('/', ''))-1)*10000+3000]

    # 外部ファイルを読み込む形式に変えた。行われている処理は全く同じ。
    with open("./files_needed_to_get_replacements_list_json_format/世界语单词词根分解法user设置.json", "r", encoding="utf-8") as g:
        change_dec = json.load(g)
    for i in change_dec:
        if len(i)==3:
            try:
                if i[1]==0:
                    num_char_or=len(i[0].replace('/', ''))*10000
                else:
                    num_char_or=i[1]
                if "动词词尾1" in i[2]:
                    for k1,k2 in verb_suffix_2l_2.items():
                        pre_replacements_dict_3[(i[0]+k1).replace('/', '')]=[safe_replace(i[0],temporary_replacements_list_3).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>")+k2, num_char_or+len(k1)*10000]
                    i[2].remove("动词词尾1")#　これがあるので、このセルの繰り返しには要注意!
                if "动词词尾2" in i[2]:
                    for k in ["u ","i ","u","i"]:
                        pre_replacements_dict_3[(i[0]+k).replace('/', '')]=[safe_replace(i[0],temporary_replacements_list_3).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>")+k, num_char_or+len(k)*10000]
                    i[2].remove("动词词尾2")
                if len(i[2])>=1:
                    for j in i[2]:
                        pre_replacements_dict_3[(i[0]+'/'+j).replace('/', '')]=[safe_replace((i[0]+'/'+j),temporary_replacements_list_3).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), num_char_or+len(j)*10000]
                else:
                    pre_replacements_dict_3[i[0].replace('/', '')]=[safe_replace(i[0],temporary_replacements_list_3).replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"), num_char_or]
            except:
                continue

    pre_replacements_list_1=[]
    for old,new in  pre_replacements_dict_3.items():
        if isinstance(new[1], int):
            pre_replacements_list_1.append((old,new[0],new[1]))

    pre_replacements_list_2= sorted(pre_replacements_list_1, key=lambda x: x[2], reverse=True)##(置換順序の数字の大きさ順にソート!)

    ##'エスペラント語根'、'置換漢字'、placeholderの順に並べ、最終的な置換に用いる"replacements"リストを作成。
    pre_replacements_list_3=[]
    for kk in range(len(pre_replacements_list_2)):
        if len(pre_replacements_list_2[kk][0])>=3:##3文字以上でいいのではないか(202412)  la対策として考案された。
            pre_replacements_list_3.append([pre_replacements_list_2[kk][0],pre_replacements_list_2[kk][1],imported_placeholders[kk]])

    ##'エスペラント語根'、'置換漢字'、placeholderの順に並べ、最終的な置換に用いる"replacements"リストを作成。
    # エスペラント文の文字列置換に用いるに必要な置換用テキストは、大文字、小文字、頭文字だけ大文字、の3種類に対応させるように作るが、その際、htmlタグまでその影響を受けないようにしたい?
    def capitalize_rt_tag(match):
        rt_start, rt_word, rt_end = match.groups()
        return rt_start + rt_word.capitalize() + rt_end
    def capitalize_according_to_condition_htmlruby(new_text):
        if new_text.startswith('<ruby>'):
            # <で始まる場合、最初の<rt>タグ内の最初の文字を大文字にする
            new_text = re.sub(r'(<ruby>)(.*?)(<rt)', capitalize_rt_tag, new_text, count=1)
        else:
            # <で始まらない場合、new_textの最初の文字を大文字にする
            new_text = new_text[0].upper() + new_text[1:]
        return new_text
    ##'大文字'、'小文字'、'文頭だけ大文字'のケースに対応。
    pre_replacements_list_4=[]
    if format_type == 'HTML 형식＿루비 크기 조절' or 'HTML形式':
        for old,new,place_holder in pre_replacements_list_3:
            pre_replacements_list_4.append((old,new,place_holder))
            pre_replacements_list_4.append((old.upper(),new.upper(),place_holder[:-1]+'up$'))##placeholderを少し変更する必要があった。
            if old[0]==' ':
                pre_replacements_list_4.append((old[0] + old[1].upper() + old[2:],new[0] + capitalize_according_to_condition_htmlruby(new[1:]),place_holder[:-1]+'cap$'))##new[0] + new[1].upper() + new[2:]は本当は怪しいが。。  
            else:
                pre_replacements_list_4.append((old.capitalize(),capitalize_according_to_condition_htmlruby(new),place_holder[:-1]+'cap$'))
    else:
        for old,new,place_holder in pre_replacements_list_3:
            pre_replacements_list_4.append((old,new,place_holder))
            pre_replacements_list_4.append((old.upper(),new.upper(),place_holder[:-1]+'up$'))##placeholderを少し変更する必要があった。
            if old[0]==' ':
                pre_replacements_list_4.append((old[0] + old[1].upper() + old[2:],new[0] + new[1].upper() + new[2:],place_holder[:-1]+'cap$'))##new[0] + new[1].upper() + new[2:]は本当は怪しいが。。  
            else:
                pre_replacements_list_4.append((old.capitalize(),new.capitalize(),place_holder[:-1]+'cap$'))

    replacements_final_list=[]
    for old, new, place_holder in pre_replacements_list_4:
        # 新しい変数でスペースを追加した内容を保持
        modified_placeholder = place_holder
        if old.startswith(' '):
            modified_placeholder = ' ' + modified_placeholder  # 語頭にスペースを追加
            if not new.startswith(' '):
                new = ' ' + new
        if old.endswith(' '):
            modified_placeholder = modified_placeholder + ' '  # 語末にスペースを追加
            if not new.endswith(' '):
                new = new + ' '
        # 結果をリストに追加
        replacements_final_list.append((old, new, modified_placeholder))

    with open("./files_needed_to_get_replacements_list_json_format/最終的な置換用のリスト(replacements_final_list)_anytype.json", "w", encoding="utf-8") as g:
        json.dump(replacements_final_list, g, ensure_ascii=False, indent=2)  # ensure_ascii=FalseでUnicodeをそのまま出力


    suffix_2char_roots=['ad', 'ag', 'am', 'ar', 'as', 'at', 'av', 'di', 'ec', 'eg', 'ej', 'em', 'er', 'et', 'id', 'ig', 'il', 'in', 'ir', 'is', 'it', 'lu', 'nj', 'op', 'or', 'os', 'ot', 'ov', 'pi', 'te', 'uj', 'ul', 'um', 'us', 'uz']
    prefix_2char_roots=['al', 'am', 'av', 'bo', 'di', 'ek', 'el', 'en', 'ge', 'ir', 'lu', 'ne', 'or', 'ov', 'pi', 'te', 'uz']
    standalone_2char_roots=['al', 'ci', 'da', 'de', 'di', 'do', 'du', 'el', 'en', 'fi', 'he', 'ho', 'je', 'ju', 'la', 'li', 'mi', 'ne', 'ni', 'nu', 'ok', 'ol', 'pi', 'po', 'se', 'si', 've', 'vi','ke']
    ##an,onはなしにする。

    with open('./files_needed_to_get_replacements_list_json_format/placeholders_$18542$-$19834$_二文字词根用.txt', 'r', encoding='utf-8') as file:##(漢字)置換時に用いる"placeholder"ファイルを予め読み込んでおく。
        imported_placeholders_for_2char = [line.strip() for line in file]

    replacements_list_for_suffix_2char_roots=[]
    for i in range(len(suffix_2char_roots)):
        replacements_list_for_suffix_2char_roots.append(["$"+suffix_2char_roots[i],"$"+safe_replace(suffix_2char_roots[i],temporary_replacements_list_3),"$"+imported_placeholders_for_2char[i]])
        replacements_list_for_suffix_2char_roots.append(["$"+suffix_2char_roots[i].upper(),"$"+safe_replace(suffix_2char_roots[i],temporary_replacements_list_3),"$"+imported_placeholders_for_2char[i][:-1]+'up$'])
        replacements_list_for_suffix_2char_roots.append(["$"+suffix_2char_roots[i].capitalize(),"$"+safe_replace(suffix_2char_roots[i],temporary_replacements_list_3),"$"+imported_placeholders_for_2char[i][:-1]+'cap$'])

    replacements_list_for_prefix_2char_roots=[]
    for i in range(len(prefix_2char_roots)):
        replacements_list_for_prefix_2char_roots.append([prefix_2char_roots[i]+"$",safe_replace(prefix_2char_roots[i],temporary_replacements_list_3)+"$",imported_placeholders_for_2char[i+300]+"$"])
        replacements_list_for_prefix_2char_roots.append([prefix_2char_roots[i].upper()+"$",safe_replace(prefix_2char_roots[i],temporary_replacements_list_3)+"$",imported_placeholders_for_2char[i+300][:-1]+'up$'+"$"])
        replacements_list_for_prefix_2char_roots.append([prefix_2char_roots[i].capitalize()+"$",safe_replace(prefix_2char_roots[i],temporary_replacements_list_3)+"$",imported_placeholders_for_2char[i+300][:-1]+'cap$'+"$"])

    replacements_list_for_standalone_2char_roots=[]
    for i in range(len(standalone_2char_roots)):
        replacements_list_for_standalone_2char_roots.append([" "+standalone_2char_roots[i]+" "," "+safe_replace(standalone_2char_roots[i],temporary_replacements_list_3)+" "," "+imported_placeholders_for_2char[i+600]+" "])
        replacements_list_for_standalone_2char_roots.append([" "+standalone_2char_roots[i].upper()+" "," "+safe_replace(standalone_2char_roots[i],temporary_replacements_list_3)+" "," "+imported_placeholders_for_2char[i+600][:-1]+'up$'+" "])
        replacements_list_for_standalone_2char_roots.append([" "+standalone_2char_roots[i].capitalize()+" "," "+safe_replace(standalone_2char_roots[i],temporary_replacements_list_3)+" "," "+imported_placeholders_for_2char[i+600][:-1]+'cap$'+" "])

    replacements_list_for_2char=replacements_list_for_standalone_2char_roots+replacements_list_for_suffix_2char_roots+replacements_list_for_prefix_2char_roots

    import json
    # JSONファイルに保存
    with open("./files_needed_to_get_replacements_list_json_format/replacements_list_for_2char.json", "w", encoding="utf-8") as f:
        json.dump(replacements_list_for_2char, f, ensure_ascii=False, indent=2)
    
    # JSONファイルの内容を直接ダウンロード
    with open("./files_needed_to_get_replacements_list_json_format/最終的な置換用のリスト(replacements_final_list)_anytype.json", "r", encoding="utf-8") as g:
        download_data = g.read()  # ファイルを文字列として読み込み

    if format_type == 'HTML 형식＿루비 크기 조절':
        st.download_button(
            label="Download replacements_list_ruby_html_format.json",
            data=download_data,  # ファイルの文字列データ
            file_name="replacements_list_ruby_html_format.json",
            mime='application/json'
        )
    elif format_type == '괄호 형식':
        st.download_button(
            label="Download replacements_list_ruby_parentheses_format.json",
            data=download_data,  # ファイルの文字列データ
            file_name="replacements_list_ruby_parentheses_format.json",
            mime='application/json'
        )
        
    with open("./files_needed_to_get_replacements_list_json_format/replacements_list_for_2char.json", "r", encoding="utf-8") as g:
        download_data_2 = g.read()  # ファイルを文字列として読み込み

    if format_type == 'HTML 형식＿루비 크기 조절':
        st.download_button(
            label="Download replacements_list_ruby_html_forma_for_2char.json",
            data=download_data_2,  # ファイルの文字列データ
            file_name="replacements_list_ruby_html_format_for_2char.json",
            mime='application/json'
        )
    elif format_type == '괄호 형식':
        st.download_button(
            label="Download replacements_list_ruby_parentheses_format_for_2char.json",
            data=download_data_2,  # ファイルの文字列データ
            file_name="replacements_list_ruby_parentheses_format_for_2char.json",
            mime='application/json'
        )