'''
Created on 2022/10/05

@author: sue-t
'''

import os
import re
from tkinter import messagebox

import c
import d
import e
from TransNum import TransNum
from pickle import NONE
# from bun import Bun


class Md(object):
    '''
    条文の項・号ごとの
    マークダウンファイルの内容を
    管理する
    '''

    kubunHou = 0    # ～税法
    kubunRei = 1    # ～税法施行令
    kubunKi = 2     # ～税法施行規則

    # matchFileName = re.compile(
    #         r'(?![._])([^法令規]+)' \
    #         '(法＿＿＿＿|法施行＿令|法施行規則)' \
    #         '(第([１２３４５６７８９０]+)条' \
    #         '(の([１２３４５６７８９０]+)' \
    #         '(の([１２３４５６７８９０]+))?)?)' \
    #         '(第([１２３４５６７８９０]+)項' \
    #         '((第([１２３４５６７８９０]+)号' \
    #         '(の([１２３４５６７８９０]+)' \
    #         '(の([１２３４５６７８９０]+))?)?))?)?' \
    #         '\..*'
    #         )

    # (.[^法令規]+) .がないと「法人税法」がマッチしない
#     matchFileName = re.compile(
#             r'(?![._])(.[^法令規]+)' \
#             '(法＿＿＿＿|法施行＿令|法施行規則)' \
#             '([^第]+)' \
#             '(第([１２３４５６７８９０]+)条' \
#             '(の([１２３４５６７８９０]+)' \
#             '(の([１２３４５６７８９０]+))?)?)' \
#             '(第([１２３４５６７８９０]+)項' \
#             '((第([１２３４５６７８９０]+)号' \
#             '(の([１２３４５６７８９０]+)' \
#             '(の([１２３４５６７８９０]+))?)?))?)?' \
#             '\..*'
#             )
    matchFileName = re.compile(
            r'(?![._])(.*)' \
            '(法＿＿＿＿|法施行＿令|法施行規則)' \
            '([^第]+)' \
            '(第([１２３４５６７８９０]+)条' \
            '(の([１２３４５６７８９０]+)' \
            '(の([１２３４５６７８９０]+))?)?)' \
            '(第([１２３４５６７８９０]+)項' \
            '((第([１２３４５６７８９０]+)号' \
            '(の([１２３４５６７８９０]+)' \
            '(の([１２３４５６７８９０]+))?)?))?)?' \
            '\..*'
            )


    def __init__(self, zeihou_mei, kubun,
                joubun_bangou, honbun,
                file_name=None, file_bun=None):
#                 file_name=None, file_bun=None,
#                 jou_kou=None):
        '''
        zeihou_mei:
            税法名を示す文字列
            ex. "消費税"
        kubun:
            法、令、規則を区分するデータ
        joubun_bangou:
            条文の番号を示すタプル
            ex. ((1,),2,(3,)) 第１条第２項第３号
        honbun:
            条文の本文（加工文）を示す文字列
            （先頭の全角空白なし）
            ただし、ヘッダ・フッタ付きの
            文字列の場合あり
        file_name:
            ファイル名（パス名、拡張子付き）
        file_bun:
            ヘッダ・フッタ付きの加工文を示す文字列
        '''
        self.zeihou_mei = zeihou_mei
        self.kubun = kubun
        self.joubun_bangou = joubun_bangou
        self.honbun = honbun
#         if jou_kou == None:
#             self.honbun = honbun
#         else:
#             text = [honbun, '\n\n']
#             for jou_koumoku in jou_kou.koumoku_list:
#                 koumoku_honbun = \
#                         jou_koumoku.get_honbun()
#                 text.append(koumoku_honbun)
#                 text.append('\n\n')
#             self.honbun = ''.join(text)
        self.file_name = file_name
        self.file_bun = file_bun
        self.soku = None
        self.midashi = None
        self.kou = None
        self.gou = None

    def set_file_bun(self, kakou_bun):
        self.file_bun = kakou_bun
        return

    def set_soku(self, soku):
        self.soku = soku
        return

    def set_midashi(self, midashi):
        self.midashi = midashi
        return

    def set_kou(self, kou):
        self.kou = kou

    def set_gou(self, gou):
        self.gou = gou

    @classmethod
    def create_file_name(cls, zeihou_mei, kubun,
            soku,
            joubun_bangou):
        '''
        ファイル名を生成する
        '''
#         d.dprint_method_start()
#         d.dprint(zeihou_mei)
#         d.dprint(kubun)
#         d.dprint(joubun_bangou)
        if kubun == Md.kubunHou:
            kubun_mei = '法＿＿＿＿'
        elif kubun == Md.kubunRei:
            kubun_mei = '法施行＿令'
        else:
            assert(kubun == Md.kubunKi)
            kubun_mei = '法施行規則'
        list_name = [zeihou_mei, kubun_mei]
        if soku == None:
            list_name.append("＿")
            e.eprint("エラー")
        elif soku == "本則":
            list_name.append("＿")
        else:
            # 附則
            list_name.append(soku)
        jou_list = TransNum.bangou_tuple2str(
                joubun_bangou)
        list_name.extend(jou_list)
        list_name.append('.md')
        file_name = ''.join(list_name)
        del list_name
#         d.dprint(file_name)
#         d.dprint_method_end()
        return file_name


    def set_part(self, part):
        #         self.kubun = (None, None, None, None, None)
        # 編、章、節、款、目
        self.part = part

    def sakusei_file(self, folder):
        '''
        ファイルの内容(file_name,file_bun)を
        作成する
        '''
#         d.dprint_method_start()
        (file_name, str_title, kubun_mei, jou_list) = \
                self.sakusei_title(folder,
                self.zeihou_mei, self.kubun, self.soku,
                self.joubun_bangou, self.midashi, '')
        self.file_name = file_name
        list_bun = [str_title]
        list_bun.append('\n\n')
        list_bun.append(self.honbun)
#         list_bun.append(self.get_honbun())
        list_bun.append('\n\n')

        list_bun.append('---\n\n')
        if self.joubun_bangou[2] == None:
            # 項
            list_guid = self.create_kou_guid(
                    self.kou, self.kou.get_gou_list(),
                    False)
            list_bun.extend(list_guid)
        else:
            # 号
            list_guid = self.create_gou_guid(
                    self.gou)
            list_bun.extend(list_guid)

#         str_tag = self.sakusei_tag(
#                 self.zeihou_mei, kubun_mei,
#                 self.soku, self.part, self.midashi,
#                 jou_list)
        del jou_list
#         list_bun.append(str_tag)
        str_index_guid = Md.create_index_guid(
                self.zeihou_mei, self.kubun)
        list_bun.append(str_index_guid)
        self.file_bun = ''.join(list_bun)
        del list_bun

#         d.dprint_method_end()
        return

    @classmethod
    def sakusei_file_full_jou(cls, folder,
            zeihou_mei, kubun, jou_jou):
        '''
        ファイルの内容(file_name,file_bun)を
        返す。
        file_bunは、条なら全部の項、号
        項なら全部の号を含む。
        file_nameは、最後は「_.md」とする
        '''
#         d.dprint_method_start()
        (file_name, str_title, kubun_mei, jou_list) = \
                cls.sakusei_title(folder,
                zeihou_mei, kubun, jou_jou.soku,
                jou_jou.bangou_tuple,
                jou_jou.midashi, '_')
        list_bun = [str_title]
        for kou in jou_jou.kou_list:
            list_bun.append('\n\n')
            title = kou.get_item_title()
            if title != None:
                list_bun.append(title)
            else:
                list_bun.append('１')
            list_bun.append('　')
            honbun = kou.honbun
            list_bun.append(honbun)
            gou_list = kou.get_gou_list()
            for gou in gou_list:
                title = gou.get_item_title()
                list_bun.append('\n\n')
                list_bun.append(title)
                list_bun.append('　')
                honbun = gou.get_honbun()
                list_bun.append(honbun)
        list_bun.append('\n\n')
#         str_tag = cls.sakusei_tag(
#                 zeihou_mei, kubun_mei,
#                 jou_jou.soku, jou_jou.kubun,
#                 jou_jou.midashi,
#                 jou_list)
        del jou_list

        list_bun.append('---\n\n')
        zenjou = jou_jou.get_zenjou()
#         d.dprint(zenjou)
        if zenjou != None:
            zenjou_name = \
                    cls.sakusei_file_name(
                    zeihou_mei, kubun, jou_jou.soku,
                    (zenjou, None, None),
                    jou_jou.midashi, '_')
#             d.dprint(zenjou_name)
            list_bun.append('[前条(全)←](' \
                    + zenjou_name + ')  ')
        else:
            list_bun.append('~~前条(全)←~~　')
        jijou = jou_jou.get_jijou()
#         d.dprint(jijou)
        if jijou != None:
            jijou_name = \
                    cls.sakusei_file_name(
                    zeihou_mei, kubun, jou_jou.soku,
                    (jijou, None, None),
                    jou_jou.midashi, '_')
#             d.dprint(jijou_name)
            list_bun.append('  [→次条(全)](' \
                    + jijou_name + ')')
        else:
            list_bun.append('~~→次条(全)~~')
        list_bun.append('\n\n')

        kou_list = jou_jou.get_kou_list()
        kou_list_full = []
        kou_list_part = []
        if kubun == Md.kubunHou:
            kubun_mei = '法＿＿＿＿'
        elif kubun == Md.kubunRei:
            kubun_mei = '法施行＿令'
        else:
            assert(kubun == Md.kubunKi)
            kubun_mei = '法施行規則'
        for kou in kou_list:
            kou_bangou_tuple = \
                    kou.get_jou_bangou_tuple()
            d.dprint(kou_bangou_tuple)
            kou_name = kou.get_kou_bangou()
            d.dprint(kou_name)
            kou_file_name = \
                    TransNum.create_link_name(
                    zeihou_mei, kubun_mei,
                    (kou_bangou_tuple, kou_name, None),
                    jou_jou.soku)
            kou_zenkaku = TransNum.i2z(kou_name)
            kou_list_full.append(
                    '[第' + kou_zenkaku + '項(全)](' \
                    + kou_file_name + '_.md)  ')
            kou_list_part.append(
                    '[第' + kou_zenkaku + '項 　 ](' \
                    + kou_file_name + '.md)  ')
        list_bun.extend(kou_list_full)
        list_bun.append('\n\n')
        list_bun.extend(kou_list_part)
        list_bun.append('\n\n')

#         list_bun.append(str_tag)
        str_index_guid = cls.create_index_guid(
                zeihou_mei, kubun)
        list_bun.append(str_index_guid)
#         d.dprint(list_bun)
        file_bun = ''.join(list_bun)
        del list_bun

#         d.dprint_method_end()
        return (file_name, file_bun)

    def sakusei_file_full_kou(self, folder,
            kou, gou_list):
        '''
        ファイルの内容(file_name,file_bun)を
        返す。
        file_bunは、条なら全部の項、号
        項なら全部の号を含む。
        file_nameは、最後は「_.md」とする
        '''
#         d.dprint_method_start()
        (file_name, str_title, kubun_mei, jou_list) = \
                self.sakusei_title(folder,
                self.zeihou_mei, self.kubun, self.soku,
                self.joubun_bangou, self.midashi, '_')
        self.file_name = file_name
        list_bun = [str_title]
        list_bun.append('\n\n')
        list_bun.append(self.honbun)
#         list_bun.append(self.get_honbun())
        for gou in gou_list:
            title = gou.get_item_title()
            list_bun.append('\n\n')
            list_bun.append(title)
            list_bun.append('　')
            honbun = gou.get_honbun()
            list_bun.append(honbun)
        list_bun.append('\n\n')
#         str_tag = self.sakusei_tag(
#                 self.zeihou_mei, kubun_mei,
#                 self.soku, self.part, self.midashi,
#                 jou_list)
        del jou_list

        list_bun.append('---\n\n')
        list_guid = self.create_kou_guid(kou, gou_list,
                True)
        list_bun.extend(list_guid)
        str_index_guid = self.create_index_guid(
                self.zeihou_mei, self.kubun)
        list_bun.append(str_index_guid)
#         list_bun.append(str_tag)
        file_bun = ''.join(list_bun)
        del list_bun
#         d.dprint_method_end()
        return (self.file_name, file_bun)

    @classmethod
    def create_index_guid(cls, zeihou_mei, kubun):
        '''indexファイルへのハイパーリンク'''
        list_index = ['[目次](index', zeihou_mei]
        if kubun == Md.kubunHou:
            kubun_mei = '法＿＿＿＿'
        elif kubun == Md.kubunRei:
            kubun_mei = '法施行＿令'
        else:
            assert(kubun == Md.kubunKi)
            kubun_mei = '法施行規則'
        list_index.append(kubun_mei)
        list_index.append('.md)\n\n')
        str_index = ''.join(list_index)
        del list_index
        return str_index


    def create_kou_guid(self, kou, gou_list,
            full):
        list_bun = []
        if self.kubun == Md.kubunHou:
            kubun_mei = '法＿＿＿＿'
        elif self.kubun == Md.kubunRei:
            kubun_mei = '法施行＿令'
        else:
            assert(self.kubun == Md.kubunKi)
            kubun_mei = '法施行規則'
        jou_name = \
                TransNum.create_link_name(
                self.zeihou_mei, kubun_mei,
                (self.joubun_bangou[0], None, None),
                self.soku)
        list_bun.append('[条(全)](' \
                + jou_name + '_.md)  ')
        kou_name = \
                TransNum.create_link_name(
                self.zeihou_mei, kubun_mei,
                (self.joubun_bangou[0],
                        self.joubun_bangou[1], None),
                self.soku)
        if full:
            list_bun.append('[項](' \
                    + kou_name + '.md)\n\n')
        else:
            list_bun.append('[項(全)](' \
                    + kou_name + '_.md)\n\n')
        list_full = []
        list_part = []
        zenkou = kou.get_zenkou()
        if zenkou != None:
            zenkou_name = \
                    TransNum.create_link_name(
                    self.zeihou_mei, kubun_mei,
                    zenkou,
                    kou.soku)
            list_full.append('[前項(全)←](' \
                    + zenkou_name + '_.md)  ')
            list_part.append('[前項 　 ←](' \
                    + zenkou_name + '.md)  ')
        else:
            list_full.append('~~前項(全)←~~　')
            list_part.append('~~前項 　 ←~~　')
        jikou = kou.get_jikou()
        if jikou != None:
#             print(jikou)
            jikou_name = \
                    TransNum.create_link_name(
                    self.zeihou_mei, kubun_mei,
                    jikou,
                    kou.soku)
            list_full.append('  [→次項(全)](' \
                    + jikou_name + '_.md)')
            list_part.append('  [→次項 　 ](' \
                    + jikou_name + '.md)')
        else:
            list_full.append('~~→次項(全)~~')
            list_part.append('~~→次項~~')
        list_full.append('\n\n')
        list_part.append('\n\n')
        list_bun.extend(list_full)
        list_bun.extend(list_part)

        for gou in gou_list:
            joubun_tuple = \
                    (gou.get_jou_bangou_tuple(),
                    gou.get_kou_bangou(),
                    gou.get_gou_bangou_tuple())
            gou_file_name = \
                    TransNum.create_link_name(
                    self.zeihou_mei, kubun_mei,
                    joubun_tuple,
                    gou.soku)
            str_tuple = TransNum.bangou_tuple2str(
                    joubun_tuple)
            list_bun.append(
                    '[' + str_tuple[2] + '](' \
                    + gou_file_name + '.md)  ')
        list_bun.append('\n\n')
        return list_bun

    def create_gou_guid(self, gou):
        list_bun = []
        if self.kubun == Md.kubunHou:
            kubun_mei = '法＿＿＿＿'
        elif self.kubun == Md.kubunRei:
            kubun_mei = '法施行＿令'
        else:
            assert(self.kubun == Md.kubunKi)
            kubun_mei = '法施行規則'

        jou_name = \
                TransNum.create_link_name(
                self.zeihou_mei, kubun_mei,
                (self.joubun_bangou[0], None, None),
                self.soku)
        list_bun.append('[条(全)](' \
                + jou_name + '_.md)    ')
        kou_name = \
                TransNum.create_link_name(
                self.zeihou_mei, kubun_mei,
                (self.joubun_bangou[0],
                    self.joubun_bangou[1], None),
                self.soku)
        list_bun.append('[項(全)](' \
                + kou_name + '_.md)    ')
        list_bun.append('[項](' \
                + kou_name + '.md)\n\n')

        zengou = gou.get_zengou()
#         print(kou_name)
#         print(self.joubun_bangou)
#         print(zengou)
        if zengou != None:
            zengou_name = \
                    TransNum.create_link_name(
                    self.zeihou_mei, kubun_mei,
                    zengou,
                    gou.soku)
            list_bun.append('[前号←](' \
                    + zengou_name + '.md)  ')
        else:
#             print("None")
            list_bun.append('~~前号←~~　')
#             print(list_bun)
        jigou = gou.get_jigou()
        if jigou != None:
            jigou_name = \
                    TransNum.create_link_name(
                    self.zeihou_mei, kubun_mei,
                    jigou,
                    gou.soku)
            list_bun.append('  [→次号](' \
                    + jigou_name + '.md)')
        else:
            list_bun.append('~~→次号~~')
        list_bun.append('\n\n')
#         print(list_bun)
        return list_bun


    @classmethod
    def sakusei_title(cls, folder,
            zeihou_mei, kubun, soku, joubun_bangou,
            midashi, full=''):
        '''
        ファイル名とファイル内のタイトルなどを
        作成する
        '''
#         d.dprint_method_start()
#         d.dprint(kubun)
#         d.dprint(soku)
#         d.dprint(joubun_bangou)
        if kubun == cls.kubunHou:
            kubun_mei = '法'
            kubun_file_mei = '法＿＿＿＿'
        elif kubun == cls.kubunRei:
            kubun_mei = '法施行令'
            kubun_file_mei = '法施行＿令'
        else:
            assert(kubun == cls.kubunKi)
            kubun_mei = '法施行規則'
            kubun_file_mei = '法施行規則'
        # list_name はファイル名の生成用
        list_name = [zeihou_mei, kubun_file_mei]
        if (soku == None) or \
                (soku == "本則") or (soku == "＿"):
            list_name.append("＿")
        else:
            list_name.append(soku)
        jou_list = TransNum.bangou_tuple2str(
                joubun_bangou)
        list_name.extend(jou_list)
        # jou_bangouが項か号の前提イロハは想定していない
        # 前提として項、号以下であり、条のことはない
#         assert(jou_list[0] != '')
#         assert(jou_list[1] != '')
        # list_bun はファイル内容の生成用
        if midashi != None:
            list_bun = [midashi, '\n']
        else:
            list_bun = []
        if jou_list[2] == '':
            # 項
            list_bun.append(zeihou_mei)
            list_bun.append(kubun_mei)
            if (soku != None) and \
                    (soku != '本則') and (soku != '＿'):
                list_bun.append(soku)
            list_bun.extend(jou_list)
            # [消費税法第三十条](消費税法第三十条)第一項
            # とは、しない。
        else:
            # 号の場合
            # [消費税法第三十条第二項]
            # (消費税法＿＿＿＿＿第三十条第二項)第三号
            list_bun.append('[')
            list_bun.append(zeihou_mei)
            list_bun.append(kubun_mei)
            if (soku != None) and \
                    (soku != '本則') and (soku != '＿'):
                list_bun.append(soku)
            list_bun.append(jou_list[0])
            list_bun.append(jou_list[1])
            list_bun.append('](')
            list_bun.append(zeihou_mei)
            list_bun.append(kubun_file_mei)
            if (soku != None) and \
                    (soku != '本則'):
                list_bun.append(soku)
            list_bun.append(jou_list[0])
            list_bun.append(jou_list[1])
            list_bun.append(')')
            list_bun.append(jou_list[2])
        list_name.append(full)
        list_name.append('.md')
        file_name = ''.join(list_name)
        file_name = os.path.join(folder, file_name)
        del list_name
        str_title = ''.join(list_bun)
        del list_bun
#         d.dprint_method_end()
        return (file_name, str_title,
                kubun_mei, jou_list)

    @classmethod
    def sakusei_file_name(cls,
            zeihou_mei, kubun, soku, joubun_bangou,
            midashi, full=''):
        '''
        ファイル名を作成する
        '''
#         d.dprint_method_start()
#         d.dprint(kubun)
#         d.dprint(soku)
#         d.dprint(joubun_bangou)
        if kubun == cls.kubunHou:
            kubun_mei = '法'
            kubun_file_mei = '法＿＿＿＿'
        elif kubun == cls.kubunRei:
            kubun_mei = '法施行令'
            kubun_file_mei = '法施行＿令'
        else:
            assert(kubun == cls.kubunKi)
            kubun_mei = '法施行規則'
            kubun_file_mei = '法施行規則'
        # list_name はファイル名の生成用
        list_name = [zeihou_mei, kubun_file_mei]
        if (soku == None) or \
                (soku == "本則") or (soku == "＿"):
            list_name.append("＿")
        else:
            list_name.append(soku)
        jou_list = TransNum.bangou_tuple2str(
                joubun_bangou)
        list_name.extend(jou_list)
        list_name.append(full)
        list_name.append('.md')
        file_name = ''.join(list_name)
#         d.dprint_method_end()
        return file_name


    @classmethod
    def sakusei_tag(cls, zeihou_mei, kubun_mei,
            soku, part, midashi, jou_list):
        # obsidianでの利用を想定したタグの設定
        list_tag = ['#', zeihou_mei, kubun_mei]
        list_bun = list_tag.copy()
        list_bun.append('\n\n')

        if (soku != None) and \
                    (soku != '本則') and (soku != '＿'):
            list_tag.append("/")
            list_tag.append(soku)
            list_bun.extend(list_tag)
            list_bun.append('\n\n')

        if part != None:
            # #相続税法/_第１章総則/_第１節通則
            # の編や章などを設定する
            list_tag_kubun = list_tag.copy()
            list_tag_kubun.append('/')
            if part[0] != None:
                # 表示の順番を考慮して
                list_tag_kubun.append('_')
                list_tag_kubun.append(part[0])
                list_bun.extend(list_tag_kubun)
                list_bun.append('\n\n')
                list_tag_kubun.append('/')
            if part[1] != None:
                # 表示の順番を考慮して
                list_tag_kubun.append('_')
                list_tag_kubun.append(part[1])
                list_bun.extend(list_tag_kubun)
                list_bun.append('\n\n')
                list_tag_kubun.append('/')
            if part[2] != None:
                # 表示の順番を考慮して
                list_tag_kubun.append('_')
                list_tag_kubun.append(part[2])
                list_bun.extend(list_tag_kubun)
                list_bun.append('\n\n')
                list_tag_kubun.append('/')
            if part[3] != None:
                # 表示の順番を考慮して
                list_tag_kubun.append('_')
                list_tag_kubun.append(part[3])
                list_bun.extend(list_tag_kubun)
                list_bun.append('\n\n')
                list_tag_kubun.append('/')
            if part[4] != None:
                # 表示の順番を考慮して
                list_tag_kubun.append('_')
                list_tag_kubun.append(part[4])
                list_bun.extend(list_tag_kubun)
                list_bun.append('\n\n')
                list_tag_kubun.append('/')
        else:
            list_tag_kubun = list_tag.copy()
            list_tag_kubun.append('/')
        # #Ｘ税法/_第一章通則/第１条（見出し）
        # タグペインに便利
        list_tag_kubun.append(jou_list[0])
        if midashi != None:
            list_tag_kubun.append(midashi)
        list_bun.extend(list_tag_kubun)
        del list_tag_kubun
        list_bun.append('\n\n')

        # #消費税法/第Ｘ条（見出し）
        list_tag.append('/')
        list_tag.append(jou_list[0])
        if midashi != None:
            list_tag.append(midashi)
        list_bun.extend(list_tag)
        list_bun.append('\n\n')
        # #消費税法/第Ｘ条（見出し）/第２項
        if jou_list[1] != '':
            list_tag.append('/')
            list_tag.append(jou_list[1])
            list_bun.extend(list_tag)
            list_bun.append('\n\n')
        # #消費税法/第Ｘ条（見出し）/第２項/第３号
        if jou_list[2] != '':
            list_tag.append('/')
            list_tag.append(jou_list[2])
            list_bun.extend(list_tag)
            list_bun.append('\n\n')
        del list_tag
        str_tag = ''.join(list_bun)
        del list_bun
        return str_tag

    def save(self):
        # d.dprint_method_start()
        # d.dprint(self.file_name)
        with open(self.file_name,
            mode='w',
            encoding='UTF-8') as f:
            f.write(self.file_bun)
        # d.dprint_method_end()
        return


    @classmethod
    def load(cls, folder_name, file_name):
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
#         d.dprint(file_name)
        m = Md.matchFileName.match(file_name)
# ('消費税', '法施行令',
# '第４条の５', '４', 'の５', '５', None, None,
#  '第２項第９４号の３の２１', '２',
# '第９４号の３の２１', '第９４号の３の２１',
# '９４', 'の３の２１', '３', 'の２１', '２１')
        if m == None:
            d.dprint("m==None")
            d.dprint_method_end()
            return None
        d.dprint(m.group(0))
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
        d.dprint(m.group(2))
        if m.group(2) == '法＿＿＿＿':
            kubun = Md.kubunHou
        elif m.group(2) == '法施行＿令':
            kubun = Md.kubunRei
        else:
            assert(m.group(2) == '法施行規則')
            kubun = Md.kubunKi
        d.dprint(m.group(5))
        d.dprint(m.group(7))
        d.dprint(m.group(9))
        if m.group(7) == None:
            jou_tuple = (int(m.group(5)),)
        elif m.group(9) == None:
            jou_tuple = (int(m.group(5)), int(m.group(7)))
        else:
            # 第１条の２の３の４ は、ない前提
            jou_tuple = (int(m.group(5)), int(m.group(7)),
                    int(m.group(9)))
        if m.group(11) == None:
            kou = None
        else:
            kou = int(m.group(11))
        if m.group(14) == None:
            gou_tuple = None
        elif m.group(16) == None:
            gou_tuple = (int(m.group(14)),)
        elif m.group(18) == None:
            gou_tuple = (int(m.group(14)),
                    int(m.group(16)))
        else:
            d.dprint(m.group(18))
            gou_tuple = (int(m.group(14)),
                    int(m.group(16)), int(m.group(18)))
        read_text = ''.join(read_list)
        del read_list
        md = Md(m.group(1), kubun,
                (jou_tuple, kou, gou_tuple),
                read_text)
        if m.group(3) == '＿':
            md.set_soku('本則')
        else:
            md.set_soku(m.group(3))

        md.file_name = full_name
        md.file_bun = read_text
        d.dprint(md)
        d.dprint_method_end()
        return md


if __name__ == '__main__':
    file_name = '地方法人税法施行＿令附則平成２８年３月３１日第２条第７項.md'
#     file_name = '法人税法施行＿令附則平成２８年３月３１日第２条第７項.md'
    m = Md.matchFileName.match(file_name)
    print(m)
    print(m.groups(0))
    exit()
    md = Md.load(
            r'C:\Users\sue-t\Documents\000_保管庫\インボイス登録',
            '消費税法施行規則第２６条の３第１項第２号.md')
    exit(0)
