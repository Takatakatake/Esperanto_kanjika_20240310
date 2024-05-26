
import streamlit as st
import pandas as pd
import io
import os
import re


# サンプルファイルのパス
file_path = './files_needed_to_get_replacements_text/20240316世界语词根列表＿包含2个字符的世界语词根.csv'

# ファイルを読み込む
with open(file_path, "rb") as file:
    btn = st.download_button(
            label="サンプルファイルをダウンロード",
            data=file,
            file_name="sample_file.csv",
            mime="text/csv"
        )
    
def conversion_format(hanzi, word, format_type):
    if format_type == 'HTML Format':
        return '<ruby>{}<rt>{}</rt></ruby>'.format(hanzi, word)
    elif format_type == 'Parentheses Format':
        return '{}({})'.format(hanzi, word)
    elif format_type == 'Only Hanzi':
        return '{}'.format(hanzi)

# ユーザーに出力形式を選んでもらう
format_type = st.selectbox(
    'Choose the output format:',
    ('HTML Format', 'Parentheses Format', 'Only Hanzi')
)

# 例示
hanzi = '漢字'
word = 'kanji'
formatted_text = conversion_format(hanzi, word, format_type)
st.write('Formatted Text:', formatted_text)

# Streamlitでファイルアップロード機能を追加
uploaded_file = st.file_uploader("Upload your file", type=['csv'])
if uploaded_file is not None:
    # Streamlitの環境でファイルを読み込むために必要な変更
    dataframe = pd.read_csv(uploaded_file)
    dataframe.to_csv("./files_needed_to_get_replacements_text/20240316世界语词根列表＿包含2个字符的世界语词根.csv", index=False)


    result = []
    # ファイルを読み込み
    with open("./files_needed_to_get_replacements_text/检查世界语所有单词的结尾是否被正确切除(result).txt", "r", encoding='utf-8') as file:
        for line in file:
            # 改行文字を除去し、カンマで分割
            parts = line.strip().split(',')
            # 分割されたデータが2つの要素を持つことを確認
            if len(parts) == 2:
                result.append((parts[0], parts[1]))



    ##上の作業で抽出した、'単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(result)を漢字置換するための、漢字置換リストを作成していく。
    ##"'単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(result)を漢字置換し終えたリスト"こそが最終的な漢字置換リストの大元になる。
    ##'既に完全に語根分解された状態の単語'が対象であれば、文字数の多い語根順に漢字置換するだけで完璧な精度の漢字置換ができる!
    ##ただし、その完璧な漢字置換のためにはあらかじめ"世界语全部单词_大约44100个(原pejvo.txt).txt"から"从世界语全部单词_大约44100个(原pejvo.txt).txt中提取并输出世界语所有词根_大约11360个.txt_带中文日文注释.ipynb"を用いてエスペラントの全語根を抽出しておく必要がある。

    replacements_dict={}##一旦辞書型を使う。(後で内容(value)を更新するため)
    with open("./files_needed_to_get_replacements_text/世界语所有词根_大约11360个.txt", 'r', encoding='utf-8') as file:
        ##"世界语所有词根_大约11360个.txt"は"世界语全部单词_大约44100个(原pejvo.txt).txt"から"从世界语全部单词_大约44100个(原pejvo.txt).txt中提取并输出世界语所有词根_大约11360个.txt_带中文日文注释.ipynb"を用いて抽出したエスペラントの全語根である。
        roots = file.readlines()
        for root in roots:
            root = root.strip()
            if not root.isdigit():##混入していた数字の'10'と'7'を削除
                replacements_dict[root]=[root,len(root)]##各エスペラント語根に対する'置換後の単語'(この作業では元の置換対象の語根のまま)と、その置換順序として、'置換対象の語根の文字数'を設定。　置換順序の数字が大きい('置換対象の語根の文字数が多い')ほど、先に置換される仕組みにする。


    ##上の作業に引き続き、"'単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(result)を漢字置換するための、漢字置換リスト"を作成していく。　
    ##ここでは自分で作成したエスペラント語根の漢字化リストを反映させる。

    input_file="./files_needed_to_get_replacements_text/20240316世界语词根列表＿包含2个字符的世界语词根.csv"
    # input_file="世界语汉字表格_20240312.csv"
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            j = line.split(',')
            if len(j)==2:
                word,hanzi=j[0],j[1]
                if (hanzi!='') and (word!='') and ('#' not in word):
                    replacements_dict[word]=[conversion_format(hanzi,word,format_type),len(word)]#辞書式配列では要素(key)に対する値(value)を後から更新できることを利用している。

    ##"'単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(result)を漢字置換するための、漢字置換リスト"を置換順序の数字の大きさ順にソート。
    pre_replacements=[]
    for old,new in replacements_dict.items():
        pre_replacements.append((old,new[0],new[1]))
    pre_replacements3 = sorted(pre_replacements, key=lambda x: x[2], reverse=True)


    ##"'単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(result)を漢字置換するための、漢字置換リスト"の各置換に対して'place holder'を追加し、'replacements'リストとして完成させた。
    ##'place holder'法とは、既に置換を終えた文字列が後続の置換によって重複して置換されてしまうことを避けるために、その置換を終えた部分に一時的に無関係な文字列(place holder)を置いておいて、
    ##全ての置換が終わった後に、改めてその'無関係な文字列(place holder)'から'目的の置換後文字列'に変換していく手法である。

    with open('./files_needed_to_get_replacements_text/No.10000_500000.txt', 'r', encoding='utf-8') as file:##漢字置換時に用いる"place holder"ファイルを予め読み込んでおく。
        loaded_strings = [line.strip() for line in file]

    replacements=[]
    for kk in range(len(pre_replacements3)):
        replacements.append([pre_replacements3[kk][0],pre_replacements3[kk][1],loaded_strings[kk]])


    ##置換に用いる関数。正規表現、C++など様々な形式の置換を試したが、pythonで'place holder'を用いる形式の置換が、最も処理が高速であった。(しかも大変シンプルでわかりやすい。)
    def safe_replace(text, replacements):
        valid_replacements = {}
        # 置換対象(old)を'place holder'に一時的に置換
        for old, new, placeholder in replacements:
            if old in text:
                text = text.replace(old, placeholder)
                valid_replacements[placeholder] = new# 後で置換後の文字列(new)に置換し直す必要がある'place holder'を辞書(valid_replacements)に記録しておく。
        #'place holder'を置換後の文字列(new)に置換)
        for placeholder, new in valid_replacements.items():
            text = text.replace(placeholder, new)
        return text

    # '単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(result)の要素を全て結合して、一つの文字列にしてから漢字置換を実施すれば
    #高速化できるのではないかと試してみたが、大して速くならなかった。
    # combined = "#%".join([entry[0] for entry in result])
    # (safe_replace(combined, replacements)).split("#%")[:20]  

    ##'単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(result)を実際にreplacementsリスト(漢字置換リストの完成版)によって漢字置換。　
    ##ここで作成される、"'単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(result)を漢字置換し終えたリスト(辞書型)"(SS)が最終的な漢字置換リストの大元になる。

    SS={}
    for j in result:##20秒ほどかかる。　先にリストの要素を全て結合して、一つの文字列にしてから漢字置換する方法を試しても(上述)、さほど高速化しなかった。
        if len(j)==2:##(j[0]がエスペラント語根、j[1]が品詞。)
            if len(j[0])>=2:##2文字以上のエスペラント語根のみが対象
                if j[0] in SS:
                    if j[1] not in SS[j[0]][1]:
                        SS[j[0]] = [SS[j[0]][0],SS[j[0]][1] + ', ' + j[1]]
                else:
                    SS[j[0]]=[safe_replace(j[0], replacements),j[1]]

    #上の作業で作成した辞書型リスト(SS)の最初から20個分を表示
    for key, value in dict(list(SS.items())[:20]).items():
        print(f"{key}: {value}")

    ##更改替换方式(关于如何更改汉字转换,请编辑第一个csv文件)  (置換の仕方の変更(漢字変換の仕方の変更については最初のcsvファイルを編集する))
    # never_used_as_roots_only=[" vin "," lin "," min "," amas "]
    # for i in never_used_as_roots_only:
    #     SS[i]=[i,"無詞"]

    ## SS→QQ  ("'単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(result)を漢字置換し終えたリスト"(SS)を最終的な漢字置換リストに成形していく。)
    ##SSの'置換対象の単語'、'漢字置換後の単語'から"/"を抜く(html形式にしたい場合、"</rt></ruby>"は"/"を含むので要注意！)。
    ##新たに置換優先順位を表す数字を追加し(漢字化する単語は'文字数×10000'、漢字化しない単語は'文字数×10000-2500')、辞書式配列QQとして保存。

    QQ={}
    for i,j in SS.items():##(iが置換対象の単語、j[0]が漢字置換後の単語、j[1]が品詞。)
        if i==j[0]:##漢字化しない単語
            QQ[i.replace('/', '')]=[j[0].replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),j[1],len(i.replace('/', ''))*10000-2500]##漢字化しない単語は優先順位を下げる
        else:
            QQ[i.replace('/', '')]=[j[0].replace("</rt></ruby>","%%%").replace('/', '').replace("%%%","</rt></ruby>"),j[1],len(i.replace('/', ''))*10000]


    ### 基本的には動詞に対してのみ活用語尾を追加し、置換対象の単語の文字数を増やす(置換の優先順位を上げる。)
    noun_prefix_2l={}
    noun_suffix_2l={}
    adj_prefix_2l={}
    adj_suffix_2l={}
    adv_prefix_2l={}
    adv_suffix_2l={}
    verb_prefix_2l={}
    verb_suffix_2l={'as':'as', 'is':'is', 'os':'os', 'us':'us','at':'at','it':'it','ot':'ot', 'ad':'ad','igx':'igx','ant':'ant','int':'int','ont':'ont'}
    ##接頭辞接尾時の追加については、主に動詞が対象である。

    noun_prefix_2l_2={}
    for d1,d2 in noun_prefix_2l.items():
        noun_prefix_2l_2[d1]=safe_replace(d2, replacements)
    noun_suffix_2l_2={}
    for d1,d2 in noun_suffix_2l.items():
        noun_suffix_2l_2[d1]=safe_replace(d2, replacements)
    adj_prefix_2l_2={}
    for d1,d2 in adj_prefix_2l.items():
        adj_prefix_2l_2[d1]=safe_replace(d2, replacements)
    adj_suffix_2l_2={}
    for d1,d2 in adj_suffix_2l.items():
        adj_suffix_2l_2[d1]=safe_replace(d2, replacements)
    adv_prefix_2l_2={}
    for d1,d2 in adv_prefix_2l.items():
        adv_prefix_2l_2[d1]=safe_replace(d2, replacements)
    adv_suffix_2l_2={}
    for d1,d2 in adv_suffix_2l.items():
        adv_suffix_2l_2[d1]=safe_replace(d2, replacements)
    verb_prefix_2l_2={}
    for d1,d2 in verb_prefix_2l.items():
        verb_prefix_2l_2[d1]=safe_replace(d2, replacements)
    verb_suffix_2l_2={}
    for d1,d2 in verb_suffix_2l.items():
        verb_suffix_2l_2[d1]=safe_replace(d2, replacements)

    ###一番の工夫ポイント(如何にして置換の優先順位を定め、置換精度を向上させるか。)
    ##基本は単語の文字数が多い順に置換していくことになるが、
    ##例えば、"置換対象の単語に接頭辞、接尾辞を追加し、単語の文字数を増やし、置換の優先順位を上げたものを、置換対象の単語として新たに追加する。"などが、置換精度を上げる方策として考えられる。
    ##しかし、いろいろ試した結果、動詞に対してのみ活用語尾を追加し、置換対象の単語の文字数を増やす(置換の優先順位を上げる。)のが、ベストに近いことがわかった。

    ## SS→QQ→RR  ("'単語の語尾だけをカットした、完全に語根分解された状態の全単語リスト'(result)を漢字置換し終えたリスト"(SS)を最終的な漢字置換リストに成形していく。)
    RR={}
    for i,j in QQ.items():##j[0]:置換後の文字列　j[1]:品詞 j[2]:置換優先順位
        # if len(i)<=2 and i==j[0]:##2文字以下の語根で漢字化されないものは削除 もしくは2文字以下の語根すべてを削除するのも有りかもしれない。
        if len(i)==2 and ("動詞"  not in j[1]):
            ##基本的に非動詞の2文字の語根単体を以て漢字置換することはない。　ただし、世界语全部单词_大约44100个(原pejvo.txt).txtに最初から含まれている2文字の語根は既に漢字化されており、実際の漢字置換にも反映されることになる。
            ##2文字の語根でも、動詞については活用語尾を追加することで、自動的に+2文字以上できるので追加した。
            continue
        else:
            RR[i]=[j[0],j[2]]##品詞情報はここで用いるためにあった。以後は不要なので省いていく。
            if j[2]==50000 or j[2]==40000 or j[2]==30000 or j[2]==20000:##実際に漢字化するエスペラント語根のみが対象
                if "名詞" in j[1]:
                    for k1,k2 in noun_prefix_2l.items():
                        if not k1+i in QQ:
                            RR[k1+i]=[k2+j[0],j[2]+2*10000-5000]#既存でないものは優先順位を大きく下げる
                    for k1,k2 in noun_suffix_2l.items():##"obl","on","op",
                        if not i+k1 in QQ:
                            RR[i+k1]=[j[0]+k2,j[2]+2*10000-5000]#既存でないものは優先順位を大きく下げる
                    for k in ["o"]:
                        if not i+k in QQ:
                            RR[i+k]=[j[0]+k,j[2]+1*10000-5000]#既存でないものは優先順位を大きく下げる 
                if "形容詞" in j[1]:
                    for k1,k2 in adj_prefix_2l.items():
                        if not k1+i in QQ:
                            RR[k1+i]=[k2+j[0],j[2]+2*10000-5000]
                    for k1,k2 in adj_suffix_2l.items():
                        if not i+k1 in QQ:
                            RR[i+k1]=[j[0]+k2,j[2]+2*10000-5000]
                    for k in ["a"]:
                        if not i+k in QQ:
                            RR[i+k]=[j[0]+k,j[2]+1*10000-5000] 
                if "副詞" in j[1]:
                    for k1,k2 in adv_prefix_2l.items():
                        if not k1+i in QQ:
                            RR[k1+i]=[k2+j[0],j[2]+2*10000-5000]
                    for k1,k2 in adv_suffix_2l.items():
                        if not i+k1 in QQ:
                            RR[i+k1]=[j[0]+k2,j[2]+2*10000-5000]
                    for k in ["e"]:
                        if not i+k in QQ:
                            RR[i+k]=[j[0]+k,j[2]+1*10000-5000]  
                if "動詞" in j[1]:
                    for k1,k2 in verb_prefix_2l.items():
                        if not k1+i in QQ:
                            RR[k1+i]=[k2+j[0],j[2]+2*10000-5000]
                    for k1,k2 in verb_suffix_2l.items():
                        if not i+k1 in QQ:
                            RR[i+k1]=[j[0]+k2,j[2]+2*10000-5000]
                    for k in ["u ","i "]:##動詞の"u","i"単体の接尾辞は後ろが空白と決まっているので、2文字分増やすことができる。
                        if not i+k in QQ:
                            RR[i+k]=[j[0]+k,j[2]+2*10000-5000]


    ##RRの編集(主に置換の優先順位の変更) ここでも置換の仕方の変更ができないことはないが、品詞の種類に応じて接尾辞や接頭辞を追加するところをスキップすることになってしまう。
    never_used_as_roots_only=["vin","lin","min","amas"]
    for i in never_used_as_roots_only:
        RR[i]=[i,i,len(i)*10000-2500]

    TT=[]
    for old,new in  RR.items():
        TT.append((old,new[0],new[1]))

    pre_replacements3= sorted(TT, key=lambda x: len(x[0]), reverse=True)##(置換順序の数字の大きさ順にソート。)

    ##'エスペラント語根'、'置換漢字'、'place holder'の順に並べ、最終的な置換に用いる"replacements"リストを作成。
    replacements=[]
    for kk in range(len(pre_replacements3)):
        if len(pre_replacements3[kk][0])>1:
            replacements.append([pre_replacements3[kk][0],pre_replacements3[kk][1],loaded_strings[kk]])

    replacements2=[]
    for old,new,place_holder in replacements:
        replacements2.append((old,new,place_holder))
        replacements2.append((old.upper(),new.upper(),place_holder))
        replacements2.append((old.capitalize(),new.capitalize(),place_holder))

    #"replacements2"リストの内容を確認
    with open("./files_needed_to_get_replacements_text/replacements2_list_html.txt", 'w', encoding='utf-8') as file:
        for old,new,place_holder in replacements2:
            file.write(f'{old},{new},{place_holder}\n')
    
    # 最終的な置換リストをファイルとしてダウンロード
    with open("./files_needed_to_get_replacements_text/replacements2_list_html.txt", 'r', encoding='utf-8') as file:
        download_data = file.read()

    st.download_button(
        label="Download replacements2_list_html.txt",
        data=download_data,
        file_name="replacements2_list_html.txt",
        mime='text/plain'
    )