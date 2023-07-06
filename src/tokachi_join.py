'''
ToKachXMLで作成した項・号ファイルから
結合した条・項ファイルを作成する。
Created on 2023/07/02

@author: sue-t
'''

import c
import d
import e

import config

from TransNum import TransNum
from md import Md


import os
from lxml import etree


class ToKachiJoin(object):
    '''
    classdocs
    Jou_xmlの造りを参照
    '''


    def __init__(self, file, mei, kubun):
        '''
        file 消費税法.xml
        mei 消費税
        kubun 0,1,2
        '''
        tree = etree.parse(file)
#         jou_list = []
        # 本則
        articles = tree.xpath('//MainProvision//Article')
        self.proc_article("＿",  # "本則",
                articles, mei, kubun)
        # 附則
        fusokus = tree.xpath('//SupplProvision')
        for fusoku in fusokus:
            d.dprint(fusoku)
            fusoku_name = fusoku.attrib.get( \
                    "AmendLawNum")
            if fusoku_name == None:
                str_fusoku = "附則"
            else:
                index = fusoku_name.find("日")
                # 漢数字を全角アラビア数字に
                str_hizuke = fusoku_name[:index+1] \
                        .replace('元', '一')
                str_ara = TransNum.k2a(
                        str_hizuke, True)
                str_fusoku = "附則" + str_ara
            articles = fusoku.xpath(".//Article")
            d.dprint(articles)
            if len(articles) != 0:
#                 self.proc_article(str_fusoku,
#                         articles)
                pass
            else:
                # 附則の中には、第Ｘ条がなく、
                # 項のみの場合あり
                self.proc_jou_nashi(str_fusoku,
                        fusoku,
                        mei, kubun)
        self.tree = tree


    def proc_jou_nashi(self, str_fusoku,
            fusoku, mei, kubun):
        '''
        条（article）がないfusokuで示される附則を
        仮の条として、各項を処理して
        str_fusokuは、附則名を示す。
        '''
        d.dprint_method_start()
        paragraphs = fusoku.xpath('Paragraph')
        (file_name, str_title, _kubun_mei, _jou_list) = \
                Md.sakusei_title('',
                mei, kubun,
                str_fusoku,
                ((0,),None,None), '', '')
        d.dprint(file_name)
        d.dprint(str_title)
        jou_data_list = [ str_title ]
#         kou = self.create_kou(str_fusoku, midashi=None,
#                 jou_bangou_tuple=(0,),
#                 paragraph=paragraphs[0])
#         jou = Jou_jou(bangou_tuple=(0,), kou=kou)
#         for paragraph in paragraphs[1:]:
#             kou = self.create_kou(str_fusoku,
#                     midashi=None,
#                     jou_bangou_tuple=(0,),
#                     paragraph=paragraph)
#             jou.tsuika_kou(kou)
#         jou.set_kubun((None, None,
#                 None, None, None))
#         jou.set_soku(str_fusoku)
# #         jou.set_midashi(midashi)
#         jou_list.append(jou)
#         jou_str = TransNum.bangou_tuple2str(
#                 ((0,),None,None))
#         midashi = jou.get_midashi()
#         if midashi != None:
#             index_list.append(
#                     '[' + jou_str[0] + midashi + '](')
#         else:
#             index_list.append(
#                     '[' + jou_str[0] + '](')
#         (file_name, _str_title, _kubun_mei, _jou_list) = \
#                 Md.sakusei_title('',
#                 mei, kubun,
#                 str_fusoku,
#                 ((0,),None,None), '', '')
#         index_list.append(file_name + ')\n\n')
#         d.dprint(index_list)
        d.dprint_method_end()


    def proc_article(self, soku, articles, mei, kubun):
        '''
        articlesで示される本則、附則内の全条文を処理し、
        sokuは、本則か附則（附則名）を示す。
        '''
        d.dprint_method_start()
        for article in articles:
            num = article.get('Num')
            if ':' in num:
                # '29:30' 削除のパターン
                continue
            jou_bangou_tuple = self.num2tuple(num)
            # 見出し
            title = article.xpath("ArticleCaption")
            if len(title) != 0:
                midashi = title[0].text
            else:
                midashi = ""
            jou_data_list = [ midashi, "\n\n" ]

            d.dprint(jou_bangou_tuple)
            (file_name, str_title,
                _kubun_mei, _jou_list) = \
                    Md.sakusei_title('',
                    mei, kubun,
                    soku,
                    (jou_bangou_tuple,None,None), '', '')
            d.dprint(file_name)
            d.dprint(str_title)
            jou_data_list.append(str_title)
            jou_data_list.append("\n\n")

            paragraphs = article.xpath('Paragraph')
            (kou_data_list, kou_guide_list) = \
                    self.proc_kou(
                    soku, midashi,
                    jou_bangou_tuple, paragraphs,
                    mei, kubun)
            jou_data_list.extend(kou_data_list)

            jou_data_list.append('---\n\n')
            zenjou = article.xpath(
                    'preceding-sibling::Article[position()=1]')
            if len(zenjou) == 1:
                zenjou_num = zenjou[0].get('Num')
                zenjou_bangou_tuple \
                        = self.num2tuple(zenjou_num)
                zenjou_name = \
                        Md.sakusei_file_name(
                        mei, kubun, soku,
                        (zenjou_bangou_tuple, None, None),
                        midashi, '_')
    #             d.dprint(zenjou_name)
                jou_data_list.append('[前条(全)←](' \
                        + zenjou_name + ')  ')
            else:
                jou_data_list.append('~~前条(全)←~~　')
            jijou = article.xpath(
                    'following-sibling::Article[position()=1]')
            if len(jijou) == 1:
                jijou_num = jijou[0].get('Num')
                if not ':' in jijou_num:
                    jijou_bangou_tuple \
                            = self.num2tuple(jijou_num)
                    jijou_name = \
                            Md.sakusei_file_name(
                            mei, kubun, soku,
                            (jijou_bangou_tuple, None, None),
                            midashi, '_')
        #             d.dprint(jijou_name)
                    jou_data_list.append('  [→次条(全)](' \
                            + jijou_name + ')')
                else:
                    jou_data_list.append('~~→次条(全)~~')
            else:
                jou_data_list.append('~~→次条(全)~~')
            jou_data_list.append('\n\n')

            jou_data_list.extend(kou_guide_list)

#         kou_list = jou_jou.get_kou_list()
#         kou_list_full = []
#         kou_list_part = []
#         if kubun == Md.kubunHou:
#             kubun_mei = '法＿＿＿＿'
#         elif kubun == Md.kubunRei:
#             kubun_mei = '法施行＿令'
#         else:
#             assert(kubun == Md.kubunKi)
#             kubun_mei = '法施行規則'
#         for kou in kou_list:
#             kou_bangou_tuple = \
#                     kou.get_jou_bangou_tuple()
#             d.dprint(kou_bangou_tuple)
#             kou_name = kou.get_kou_bangou()
#             d.dprint(kou_name)
#             kou_file_name = \
#                     TransNum.create_link_name(
#                     zeihou_mei, kubun_mei,
#                     (kou_bangou_tuple, kou_name, None),
#                     jou_jou.soku)
#             kou_zenkaku = TransNum.i2z(kou_name)
#             kou_list_full.append(
#                     '[第' + kou_zenkaku + '項(全)](' \
#                     + kou_file_name + '_.md)  ')
#             kou_list_part.append(
#                     '[第' + kou_zenkaku + '項 　 ](' \
#                     + kou_file_name + '.md)  ')
#         list_bun.extend(kou_list_full)
#         list_bun.append('\n\n')
#         list_bun.extend(kou_list_part)
#         list_bun.append('\n\n')
#
# #         list_bun.append(str_tag)
#         str_index_guid = cls.create_index_guid(
#                 zeihou_mei, kubun)
#         list_bun.append(str_index_guid)
# #         d.dprint(list_bun)
#         file_bun = ''.join(list_bun)
#         del list_bun
#
# #         d.dprint_method_end()
#         return (file_name, file_bun)
#
#             zenjou = article.xpath(
# #                     'preceding-sibling::Article[position()=last()]')
#                     'preceding-sibling::Article[position()=1]')
#             if len(zenjou) == 1:
#                 zenjou_num = zenjou[0].get('Num')
#                 if not ':' in zenjou_num:
#                     zenjou_bangou_tuple \
#                             = self.num2tuple(zenjou_num)
#                     jou.set_zenjou(zenjou_bangou_tuple)
#             jijou = article.xpath(
#                     'following-sibling::Article[position()=1]')
#             if len(jijou) == 1:
#                 jijou_num = jijou[0].get('Num')
#                 if not ':' in jijou_num:
#                     jijou_bangou_tuple \
#                             = self.num2tuple(jijou_num)
#                     jou.set_jijou(jijou_bangou_tuple)
# #             d.dprint("========")
# #             d.dprint(jou_bangou_tuple)
# #             d.dprint(zenjou)
# #             d.dprint("========")
#             jou_list.append(jou)
#         d.dprint(jou_data_list)
        jou_data = ''.join(jou_data_list)
        del jou_data_list
        d.dprint(jou_data)
        d.dprint_method_end()


    def proc_kou(self, soku,
            midashi, jou_bangou_tuple,
            paragraphs, mei, kubun):
        '''
        paragraphsで示される全部の項を
        項別に全項のファイルを作り、
        全条のファイル用にデータを返す。
        '''
        d.dprint_method_start()
#             (kou_data_list, kou_guid_list) = self.proc_kou(
#                     soku, midashi, paragraphs,
#                     mei, kubun)
        kou_data_for_jou = []
        kou_guide_list_for_jou = []
        for paragraph in paragraphs:
            # 第１項の処理に注意
            num = paragraph.get('Num')
            if ':' in num:
                nums = num.split(':')
                num = nums[0]   # 暫定処理
            kou_bangou = int(num)
    #         d.dprint(jou_bangou_tuple)
    #         d.dprint(kou_bangou)

            (file_name, str_title, kubun_mei, jou_list) = \
                    Md.sakusei_title('',
                    mei, kubun, soku,
                    (jou_bangou_tuple, kou_bangou, None),
                    midashi, '')

            d.dprint(file_name)

            read_text = ToKachiJoin.load_line(
                    config.folder_name, file_name)
            d.dprint(read_text)
            for row in range(3, len(read_text)):
                d.dprint(read_text[row])
                if read_text[row] == '---\n':
                    d.dprint("guide")
                    d.dprint(read_text[row])
                    data_list = read_text[:row]
# [条(全)](国税通則法施行＿令＿第１４条_.md)  [項(全)](国税通則法施行＿令＿第１４条第１項_.md)
# [条(全)](国税通則法施行＿令＿第１４条_.md)  [項](国税通則法施行＿令＿第１４条第１項.md)
                    guide_list = ['\n']
                    guide_str = read_text[row+2]
                    d.dprint(guide_str)
                    index = guide_str.rfind("]")
                    guide_new_str = \
                            guide_str[:index-3] + \
                            guide_str[index:-6] + ".md)"
                    d.dprint(guide_new_str)
                    guide_list.append(guide_new_str)
                    guide_list.append('\n')
                    guide_list.extend(read_text[row+3:-1])
                    d.dprint(guide_list)
                    break
            else:
                data_list = read_text[:]
                guide_list = []

            items = paragraph.xpath('.//Item')

            for item in items:
#                 (gou_data_list, gou_guide) = \
                gou_data_list = \
                        self.proc_gou(
                        soku, midashi,
                        jou_bangou_tuple, kou_bangou,
                        item,
                        mei, kubun)
                d.dprint(gou_data_list)
                data_list.extend(gou_data_list)
#                 guide_list.append(gou_guide)

            data_list.append('---\n\n')
            data_list.extend(guide_list)
            del guide_list
            data_list.append(read_text[-1])

            d.dprint(data_list)
            data_bun = ''.join(data_list)
            del data_list
            (file_name_all, str_title, kubun_mei, jou_list) = \
                    Md.sakusei_title('',
                    mei, kubun, soku,
                    (jou_bangou_tuple, kou_bangou, None),
                    midashi, '_')
            ToKachiJoin.save(
                    config.folder_name, file_name_all,
                    data_bun)

        kou_data_for_jou = []
        kou_guide_list_for_jou = []
        d.dprint_method_end()
        return (kou_data_for_jou, kou_guide_list_for_jou)


    def proc_gou(self, soku,
            midashi, jou_bangou_tuple, kou_bangou,
            item, mei, kubun):
        '''
        itemで示される号を
        全項のファイル用、全条のファイル用に
        データを返す。
        '''
        d.dprint_method_start()
        num = item.get('Num')
        if ':' in num:  # 略や削除のときに、ある
            return None
        titles = item.xpath('./ItemTitle')
        if (len(titles) != 0) and \
                (titles[0].text != None):
            gou_data_list = [ titles[0].text, '　' ]
        else:
            gou_data_list = []
        gou_bangou_tuple = self.num2tuple(num)
        (file_name, str_title,
            _kubun_mei, _jou_list) = \
                Md.sakusei_title('',
                mei, kubun,
                soku,
                (jou_bangou_tuple,kou_bangou,gou_bangou_tuple),
                '', '')
        d.dprint(file_name)
        d.dprint(str_title)
        read_text = ToKachiJoin.load_line(
                config.folder_name, file_name)
        d.dprint(read_text)
        for row in range(3, len(read_text)):
            if read_text[row] == '---\n':
                gou_data_list.extend(read_text[3:row])
                break
        else:
            gou_data_list.extend(read_text[3:])
#         guide_list = [ '[第' ]
#         d.dprint(gou_bangou_tuple)
#         guide_list.append('](')
#         guide_list.append(file_name)
#         guide_list.append(')')
#         guide = ''.join(guide_list)
#         del guide_list
        d.dprint_method_end()
#         return (gou_data_list, guide)
        return gou_data_list


    @classmethod
    def save(cls, folder_name, file_name, file_bun ):
        # d.dprint_method_start()
        full_name = os.path.join(folder_name, file_name)
        with open(full_name,
            mode='w',
            encoding='UTF-8') as f:
            f.write(file_bun)
        d.dprint_method_end()
        return


    @classmethod
    def load_line(cls, folder_name, file_name):
        '''
        指定されたフォルダ・ファイル名のファイルを
        読込み、Mdデータを作成する。
        ファイル名は、
        税法名
        法律区分、
        本則（"＿"）、附則（'附則令和五年三月三十一日'）の区別
        条文番号（'第ＸＸ条第Ｙ項第Ｚ号'）
        で構成されている前提
        folder_name:
            フォルダ名
        file_name:
            ファイル名（拡張子付き）
        '''
        d.dprint_method_start()
        full_name = os.path.join(folder_name, file_name)
        try:
            f = open(full_name,
                    "r",
                    encoding="UTF-8")
            read_list = f.readlines()
            f.close()
        except OSError as e:
#             messagebox.showwarning(
#                     'ファイル読込失敗', e)
            return None
#         read_text = ''.join(read_list)
#         del read_list
        d.dprint(read_list)
        d.dprint_method_end()
        return read_list


    def num2tuple(self, num):
        list_num = num.split('_')
        if len(list_num) == 1:
            tup = (int(list_num[0]),)
        elif len(list_num) == 2:
            tup = (int(list_num[0]), int(list_num[1]))
        elif len(list_num) == 3:
            tup = (int(list_num[0]), int(list_num[1]),
                   int(list_num[2]))
        elif len(list_num) == 4:
            tup = (int(list_num[0]), int(list_num[1]),
                   int(list_num[2]), int(list_num[3]))
        else:
            return 0
#             eprint("num2tuple over")
        return tup

if __name__ == '__main__':
        folder = '.\\org'
        config.folder_name = folder

#         file = "国税通則"
        file = "地方法人税"
        mei = file
        ToKachiJoin(file + '法.xml', mei, 0)
#         jou_list = jou_xml.get_jou_list()
#         index_list = jou_xml.get_index_list()
#         for jou_jou in jou_list:
#             save_file( \
#                     folder, \
#                     mei, 0, jou_jou)
#         appdx_list = jou_xml.create_appdxTable(
#                 index_list, mei, 0)
#         for (title, text) in appdx_list:
# #             file_name = file + '法＿＿＿＿' + title + '.md'
#             file_name = mei + '法＿＿＿＿' + title + '.md'
#             file_name = os.path.join(folder, file_name)
#             with open(file_name,
#                 mode='w',
#                 encoding='UTF-8') as f:
#                 f.write(text)

