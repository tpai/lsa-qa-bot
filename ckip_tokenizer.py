# -*- coding: utf-8 -*-

import re
from ckiptagger import WS, construct_dictionary

ws = WS("./data")

def remove_special_characters(string): #移除特殊字元，僅保留英數字及中日韓統一表意文字(CJK Unified Ideographs)
    filters = re.compile(u'[^0-9a-zA-Z\u4e00-\u9fff]+', re.UNICODE)
    return filters.sub('', string) #remove special characters

def convert_arabic_to_chinese(num):
    if num == 0:
        return '零'
    chinese_num = ''
    digits = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九']
    units = ['', '十', '百', '千', '萬']
    num_str = str(num)
    num_len = len(num_str)
    for i in range(num_len):
        digit = int(num_str[i])
        unit = units[num_len - i - 1]
        if digit == 0:
            if unit == '萬':
                chinese_num += '萬'
            elif i < num_len - 1 and int(num_str[i+1]) != 0:
                chinese_num += '零'
        else:
            if i == num_len - 2 and digit == 1:
                chinese_num += '十'
            else:
                chinese_num += digits[digit] + unit
    return chinese_num

no_dict = {"前項": 1}
for i in range(1, 201):
    no_dict[f"第{convert_arabic_to_chinese(i)}章"] = 1
    no_dict[f"第{convert_arabic_to_chinese(i)}條"] = 1
    no_dict[f"第{convert_arabic_to_chinese(i)}項"] = 1
    no_dict[f"第{convert_arabic_to_chinese(i)}款"] = 1
    no_dict[f"{convert_arabic_to_chinese(i)}年"] = 1
    no_dict[f"{convert_arabic_to_chinese(i)}個月"] = 1
    no_dict[f"{convert_arabic_to_chinese(i)}星期"] = 1
    no_dict[f"{convert_arabic_to_chinese(i)}日"] = 1
    no_dict[f"{convert_arabic_to_chinese(i)}小時"] = 1
    no_dict[f"{convert_arabic_to_chinese(i)}分鐘"] = 1
    no_dict[f"{convert_arabic_to_chinese(i)}次"] = 1

article_item_map = {}

import re
def replace_article(string):
    global article_str
    global replace_str
    while True:
        article_search = re.search(r'第\s(\d+之?\d?)\s條', string)
        if article_search is not None:
            article_num = article_search.group(1)
            article_str = f'第{article_num}條'
            article_str = re.sub(r'\d+', lambda x: convert_arabic_to_chinese(int(x.group())), article_str)
            article_item_map[article_str] = 2
            replace_str = article_str
            return article_str

        sub_item_search = re.search(r'^([一二三四五六七八九零十百千萬]+)、', string)
        if sub_item_search is not None:
            sub_item_index = sub_item_search.start()
            sub_item_str = sub_item_search.group()
            sub_item_num = sub_item_search.group(1)
            sub_replace_str=f'{replace_str}第{sub_item_num}款'
            sub_replace_str = re.sub(r'^[一二三四五六七八九零十百千萬]+、', lambda x: convert_arabic_to_chinese(int(x.group())), sub_replace_str)
            article_item_map[sub_replace_str] = 2
            string = string[:sub_item_index] + sub_replace_str + string[sub_item_index+len(sub_item_str):];
            return string

        item_search = re.search(r'(\d+)\s{2}', string)
        if item_search is None:
            return string
        item_index = item_search.start()
        item_str = item_search.group()
        item_num = item_search.group(1)
        replace_str=f'{article_str}第{item_num}項'
        replace_str = re.sub(r'\d+', lambda x: convert_arabic_to_chinese(int(x.group())), replace_str)
        article_item_map[replace_str] = 2
        string = string[:item_index] + replace_str + string[item_index+len(item_str):]
        return string

files = ['labor_standard_act_zhtw.txt', 'labor_pension_act_zhtw.txt']
for file in files:
    my_file=f"./files/{file}"
    cut_file=f"./files/cut/{file}"
    with open(cut_file, 'w') as f:
        f.write('')
        f.close()
    with open(my_file, "r", encoding='utf-8') as f:
        for line in f:
            data = line.replace('-', '之')
            data = replace_article(data)
            file_content = remove_special_characters(data)
            output=ws([file_content], coerce_dictionary=construct_dictionary({**no_dict, **article_item_map}))
            cut_data = " ".join([w for w in output[0]])
            if file == 'labor_standard_act_zhtw.txt' and '本 法' in cut_data:
                cut_data = cut_data.replace('本 法', '勞動基準法')
            if file == 'labor_pension_act_zhtw.txt' and '本 條例' in cut_data:
                cut_data = cut_data.replace('本 條例', '勞工退休金條例')
            with open(cut_file, 'a') as f:
                f.write('\n')
                if re.match(r'^第.*條$', cut_data):
                    f.write('\n')
                f.write(cut_data)
                f.close()
del ws
