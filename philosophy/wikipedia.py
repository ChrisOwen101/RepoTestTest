import requests
from bs4 import BeautifulSoup 

# 
#   utils
#

def detect_bad_indexes(text, start_char, end_char):
    text_between = ''
    counter = 0
    indexes = []
    start_index = 0
    end_index = 0
    for each in range(text.__len__()):
        if counter > 0:
            text_between += text[each]
        if counter > 0:
            text_between += text[each]
        elif counter < 0 :
            counter = 0
        if text[each] == start_char :
            if  counter == 0 :
                start_index = each
            counter += 1
        if text[each] == end_char:
            counter -= 1
            if counter == 0 :
                end_index = each
                indexes.append((start_index, end_index))
            elif counter < 0 :
                start_index = end_index = 0
    return indexes
def check_a_isbad(a_tag_text, text, bad_indexes):
    a_tag_text_index = text.index(a_tag_text)    
    res = [x for x in bad_indexes  if a_tag_text_index > x[0] and a_tag_text_index < x[1]]
    if  res :
        return True
    else:
        return False
def scrape(link) :
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    div_tag = soup.find('div', attrs={'id':'bodyContent'})
    p_tags = div_tag.find_all("p", recursive = True)
    counter = 1
    # print(p_tags.__len__())
    for each_p in p_tags:
        if each_p.has_attr('class') and each_p['class'][0] == 'mw-empty-elt' :
            continue
        bad_par_indexes = detect_bad_indexes(each_p.text, '(', ')')
        bad_curly_indexes = detect_bad_indexes(each_p.text, '{', '}')
        a_tags =  each_p.find_all('a', recursive = False)
        for each_a in a_tags :
            if each_a != None :
                a_text = each_a.text
                a_href = each_a['href']
                if check_a_isbad(a_text, each_p.text, bad_par_indexes) :
                    continue
                if check_a_isbad(a_text, each_p.text, bad_curly_indexes) :
                    continue
                if each_a.has_attr('class') and each_a['class'][0] in ['new', 'mw-disambig'] :
                    continue
                if 'https://' in a_href or  'http://' in a_href:
                    continue
                ret_val ={
                    'a_text' : each_a.text,
                    'a_href' : each_a['href'],
                    'p_number' : counter,
                }
                return ret_val, True
        counter += 1
    return {}, False