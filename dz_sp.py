import re
import requests
from lxml import etree

###解析svg文件 返回y的坐标和汉字
def svg_parser(url,headers):
    r = requests.get(url, headers=headers)
    font = re.findall('" y="(\d+)">(\w+)</text>', r.text, re.M)
    if not font:
        print('222', font)
        font = []
        z = re.findall('" textLength.*?(\w+)</textPath>', r.text, re.M)
        y = re.findall('id="\d+" d="\w+\s(\d+)\s\w+"', r.text, re.M)
        for a, b in zip(y, z):
            font.append((a, b))
    width = re.findall("font-size:(\d+)px", r.text)[0]
    new_font = []
    for i in font:
        new_font.append((int(i[0]), i[1]))
    # print(new_font)
    # print('555',int(width))
    return new_font, int(width)

#获取相对应的替换字典
def get_background(url,headers):
    res=requests.get(url,headers=headers)
    css_url ="http:"+ re.findall('href="(//s3plus.meituan.net.*?svgtextcss.*?.css)', res.text)[0]
    css_content=requests.get(css_url,headers=headers)
    svg_url=re.findall('class\^="(\w+)".*?(//s3plus.*?\.svg)',css_content.text)
    s_parser = []
    for c, u in svg_url:  #c是相当于一个标识符，u是svg的地址
        f, w = svg_parser("http:" + u,headers)  #f相当于是找到的文字，w代表背景宽度
        s_parser.append({"code": c, "font": f, "fw": w})
    #print(s_parser)
    css_list = re.findall('(\w+){background:.*?(\d+).*?px.*?(\d+).*?px;', '\n'.join(css_content.text.split('}')))
    #print('11111',css_list)
    css_list = [(i[0], int(i[1]), int(i[2])) for i in css_list] #获得需要替换的字的坐标（tr74g，448，2351）
    replace_dic = []
    for i in css_list:  # 获得需要替换的字的坐标（tr74g，448，2351）
        #  print('22222',i)
        replace_dic.append({"code": i[0], "word": font_parser(s_parser,i)})  # 把网页上的符合和汉字对应
    return replace_dic

#字体解析
def font_parser(s_parser,ft):#ft:（tr74g，448，2351）
    for i in s_parser:
        #print('3333',i)
        if i["code"] in ft[0]:
            font = sorted(i["font"])
            if ft[2] < int(font[0][0]):
                x = int(ft[1] / i["fw"])
                return font[0][1][x]
            for j in range(len(font)):
                if (j + 1) in range(len(font)):
                    if (ft[2] >= int(font[j][0]) and ft[2] < int(font[j + 1][0])):
                        x = int(ft[1] / i["fw"])
                        return font[j + 1][1][x]
#替换原html中需要转换的文字
def change_words(replace_dic):
    rep = res.text
    for i in range(len(replace_dic)):#更换里面的特殊符号汉字
        # print(replace_dic[i]["code"])
        try:
            if replace_dic[i]["code"] in rep:
                a = re.findall(f'<\w+\sclass="{replace_dic[i]["code"]}"><\/\w+>', rep)[0]
                rep = rep.replace(a, replace_dic[i]["word"])
        except Exception as e:
            print(e)
    return rep


#t提取评论
def get_review(rep):
    html=etree.HTML(rep)
    li_list = html.xpath('//div[@class="reviews-items"]/ul/li')
    pl=[]
    for li in li_list:
        infof1 = li.xpath('.//div[@class="review-truncated-words"]/text()')
        infof2= li.xpath('.//div[@class="review-words"]/text()')
        if infof1:
            pl.append(infof1[0].strip().replace("\n",""))
            #print(infof[0].strip().replace("\n",""))
        if infof2:
            pl.append(infof2[0].strip().replace("\n", ""))
    #print(len(pl))
    for i in pl:
        print(i)

for i in range(1,4):
    url="http://www.dianping.com/shop/G4mSXrPMsR3CXLB4/review_all/p{}?queryType=reviewGrade&queryVal=good".format(i)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
        "Cookie": "_lxsdk_cuid=1741509d29cc8-0d3a1e3d83fa41-3a65420e-e1000-1741509d29cc8; _lxsdk=1741509d29cc8-0d3a1e3d83fa41-3a65420e-e1000-1741509d29cc8; _hc.v=ff2c393f-b74e-b2d8-7339-216ee81fcab1.1598080800; cy=3; cye=hangzhou; s_ViewType=10; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; dper=d8de152e9624b3dcc891c2899013210ce92e0b5a91c0d8d319c7d05bf8e668e25a5896ef384c802fbcd2a62f6367545630a1c8460a931738eb467486b92a5966ca949b5b15d44205df2766dc03728e668443f46eeae24869869abb3b46d7ca78; ua=dpuser_0058019817; ctu=77d9c9b833b056609e6c0d938d027cf4480d4665198a3c47b83b7e2a0e2a068f; ll=7fd06e815b796be3df069dec7836c3df; Hm_lvt_602b80cf8079ae6591966cc70a3940e7=1606871857,1606878735,1607390278,1607477424; dplet=04d2d48be29b9d68ea3afb807a6baca8; Hm_lpvt_602b80cf8079ae6591966cc70a3940e7=1607481240; _lxsdk_s=1764558bf5f-9df-877-375%7C%7C53"
    }
    res = requests.get(url, headers=headers)
    rep=change_words(get_background(url,headers))
    get_review(rep)