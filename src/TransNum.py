'''
Created on 2022/10/01

@author: sue-t
'''

import re

# import mojimoji


class TransNum(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''

    tt_ksuji = str.maketrans('一二三四五六七八九', '123456789')
    tt_zsuji = str.maketrans('1234567890', '１２３４５６７８９０')

    re_suji = re.compile(r'[十百千\d]+')
    re_kunit = re.compile(r'[十百千]|\d+')
    re_manshin = re.compile(r'[万億兆]|[^万億兆]+')

    TRANSUNIT = {'十': 10,
                 '百': 100,
                 '千': 1000}
    TRANSMANS = {'万': 10000,
                 '億': 100000000,
                 '兆': 1000000000000}


    @classmethod
    def create_link_name(cls, zeihou_mei, kubun_mei,
                joubun_tuple, soku=None):
        '''
        ハイパーリンク用の文字列を作成する。
        soku : ＿ または 附則……
        '''
        if kubun_mei == "法":
            kubun_file_mei = '法＿＿＿＿'
        elif kubun_mei == '法施行令':
            kubun_file_mei = '法施行＿令'
        elif kubun_mei == '法施行規則':
            assert(kubun_mei == '法施行規則')
            kubun_file_mei = '法施行規則'
        else:
            kubun_file_mei = kubun_mei
        list_name = [zeihou_mei, kubun_file_mei]
        if soku != None:
            list_name.append(soku)

        jou_list = TransNum.bangou_tuple2str(
                joubun_tuple)
        list_name.extend(jou_list)
        # jou_bangouが項か号の前提イロハは想定していない
        # 前提として項、号以下であり、条のことはない
        # 条も想定することに変更
        assert(jou_list[0] != '')
#         assert(jou_list[1] != '')
#         print(list_name)
        link_name = ''.join(list_name)
        del list_name
        return link_name


    @classmethod
    def bangou_tuple2str(cls, bangou_tuple):
        '''
        条項号の番号タプルを条文番号文字列に変換
        ((3,2),2,(1,2,3))
        -> ['第３条の２','第２項', '第１号の２の３']
        '''
        # 条の処理
        list_jou = [ '第' ]
        zen = TransNum.i2z(bangou_tuple[0][0])
        list_jou.append(zen)
        list_jou.append('条')
        if len(bangou_tuple[0]) > 1:
            list_jou.append('の')
            zen = TransNum.i2z(bangou_tuple[0][1])
            list_jou.append(zen)
            if len(bangou_tuple[0]) > 2:
                list_jou.append('の')
                zen = TransNum.i2z(bangou_tuple[0][2])
                list_jou.append(zen)
                if len(bangou_tuple[0]) > 3:
                    list_jou.append('の')
                    zen = TransNum.i2z(bangou_tuple[0][3])
                    list_jou.append(zen)
#                     print(bangou_tuple)
                    assert(len(bangou_tuple[0]) == 4)
        # 項の処理
        if bangou_tuple[1] != None:
            list_kou = ['第']
            zen = TransNum.i2z(bangou_tuple[1])
            list_kou.append(zen)
            list_kou.append('項')
        else:
            list_kou = ['']
        # 号の処理
        list_gou = ['']
        if bangou_tuple[2] != None:
            list_gou.append('第')
            zen = TransNum.i2z(bangou_tuple[2][0])
            list_gou.append(zen)
            list_gou.append('号')
            if len(bangou_tuple[2]) > 1:
                list_gou.append('の')
                zen = TransNum.i2z(bangou_tuple[2][1])
                list_gou.append(zen)
                if len(bangou_tuple[2]) > 2:
                    list_gou.append('の')
                    zen = TransNum.i2z(bangou_tuple[2][2])
                    list_gou.append(zen)
                    if len(bangou_tuple[2]) > 3:
                        list_gou.append('の')
                        zen = TransNum.i2z(bangou_tuple[2][3])
                        list_gou.append(zen)
                        assert(len(bangou_tuple[2]) == 4)
        # 現状は号まで、イロハに拡張するかも
        assert(len(bangou_tuple) < 4)
        jou_list = [''.join(list_jou), ''.join(list_kou),
                ''.join(list_gou)]
        del list_jou, list_kou, list_gou
        return jou_list


    @classmethod
    def i2z(cls, num: int):
        """整数を全角数字に変換"""
        str_num = str(num)
        list_zen = []
        for s in str_num:
            list_zen.append(chr(0xff10 + int(s)))
        zen = ''.join(list_zen)
        return zen

    @classmethod
#     def kansuji2arabic(cls, kstring: str, zenkaku=False):
    def k2a(cls, kstring: str, zenkaku=False):
        """漢数字をアラビア数字・全角数字に変換"""
        if isinstance(kstring, int):
            return kstring
        kstring = kstring.replace('〇', '十')
        transuji = kstring.translate(TransNum.tt_ksuji)
        for suji in sorted(set(TransNum.re_suji.findall(transuji)),
                key=lambda s: len(s),
                reverse=True):
            if not suji.isdecimal():
                arabic = TransNum._transvalue(suji,
                        TransNum.re_manshin, TransNum.TRANSMANS)
                arabic = str(arabic)
                transuji = transuji.replace(suji, arabic)
        if zenkaku:
            transuji = transuji.translate(TransNum.tt_zsuji)
        return transuji


    @classmethod
    def k2a_double(cls, kstring: str):
        """漢数字をアラビア数字と全角数字に変換"""
        kstring = kstring.replace('〇', '十')
        transuji = kstring.translate(TransNum.tt_ksuji)
        for suji in sorted(set(TransNum.re_suji.findall(transuji)),
                key=lambda s: len(s),
                reverse=True):
            if not suji.isdecimal():
                arabic = TransNum._transvalue(suji,
                        TransNum.re_manshin, TransNum.TRANSMANS)
                arabic = str(arabic)
                transuji = transuji.replace(suji, arabic)
        tranzensuji = transuji.translate(TransNum.tt_zsuji)
        return (transuji, tranzensuji)


    @classmethod
    def _transvalue(cls, sj: str, re_obj=re_kunit,
            transdic=TRANSUNIT):
        unit = 1
        result = 0
        for piece in reversed(re_obj.findall(sj)):
            if piece in transdic:
                if unit > 1:
                    result += unit
                unit = transdic[piece]
            else:
                val = int(piece) if piece.isdecimal() \
                        else TransNum._transvalue(piece)
                result += val * unit
                unit = 1

        if unit > 1:
            result += unit

        return result


if __name__ == '__main__':
    moto = "七十七"
    go = TransNum.k2a(moto, True)
    print(go)
#     moto = "国税通則法＿＿＿＿附則平成三一年三月二九日第１条第１項"
    moto = "昭和四〇年三月二六日"
    go = TransNum.k2a(moto, True)
    print(go)
    jou = ((11,22,43),54,(125,1026,7,8))
    str_jou = TransNum.bangou_tuple2str(jou)
    print(str_jou)