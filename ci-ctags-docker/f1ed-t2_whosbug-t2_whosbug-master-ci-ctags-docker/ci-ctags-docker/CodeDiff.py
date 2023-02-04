# -*- coding: utf-8 -*-

import GitParser
import re
import DiffChange

class code_diff:
    """def __init__(self, pre_version="97a8fbb0bb316f07dc2667d79082b93f9b6f00d2", next_version="6ae3f7d7888a01ba73f53a16885e2c56b270cffe"):
        git_diff_cmd = "git log --full-diff -p -U1000 %s..%s"%(pre_version, next_version)
        fd = os.popen(git_diff_cmd)
        self.diff_content = fd.readlines()
        fd.close()"""

    def __init__(self, git_diff_file="/root/workspace/diff"):
        with open(git_diff_file, 'r') as fd: #打开文件
            self.diff_content = fd.read()#读文件
            fd.close()

    def analysis(self):  #分析gitdiff,如果是改变函数名字，那么ctags也会识别出来
        self.diff_content=GitParser.delete_new_file_mode(self.diff_content)
        self.diff_content=GitParser.delete_note(self.diff_content)#删注释
        self.diff_content=GitParser.delete_mult_note(self.diff_content)#删多行注释
        self.diff_content=GitParser.none_author_and_commit(self.diff_content)
        appname,version=GitParser.get_appname_and_version(self.diff_content)
        commits = GitParser.parse_commits(self.diff_content)#根据gitdiff分析，生成commit-dictionary
        all_diffs = []

        for commit in commits:
            commit_id = commit["commit"]#按照键找对应的值
            begin_index = self.diff_content.index("commit %s"%commit_id) #跟find()方法一样，只不过如果str不在 string中会报一个异常.如果包含子字符串返回开始的索引值
            # end_index = self.diff_content.rfind("\ncommit ", begin_index+1)# rfind是从字符串右边开始查询,查询到的第一个子字符串的下标，从begin_index位置开始找，即从右到begin_index的位置
            pattern = re.compile(r'commit [a-f0-9]+\ntree [a-f0-9]+\nparent [a-f0-9]+\n')
            if pattern.search(self.diff_content,begin_index+1)==None:
                end_index =-1
            else:
                end_index=pattern.search(self.diff_content,begin_index+1).span()[0]
            if end_index == -1 or end_index == begin_index: #找不到或者 这一句话后面没有再多的commit，仅有一个commit
                end_index = len(self.diff_content) 
            diff_park = self.diff_content[begin_index:end_index] #截取diff的commit
            diffs = GitParser.parse_diff(diff_park)
            commit["diffs"] = []
            commit["appname"] = appname
            commit["version"]=version
            all_diffs=DiffChange.find_change_commit(commit,diffs,all_diffs)

            # for diff in diffs:
            #     dc = diff["diff_file"][0]#获取文件名字list
            #     diff["diff_file"] = {}

            #     # for dc in dcs:
            #     tempfile = dc
            #     if(dc.split('.')[-1] in ["md","xml","yml" ,"pbxproj" ,"podspec"]):
            #         continue
            #     read_tags = os.popen("/root/workspace/tx/t2_whosbug/ci-ctags-docker/uctags --fields=+ne -o - --sort=no %s"%tempfile)#跑这个环境
            #     change_line_numbers = self.find_all_change_line_numbers(tempfile)
            #     minus_sign_change_line_numbers = self.find_all_change_line_numbers(tempfile,re_change_mark="^\- ")#防止减号的”{“和”}“影响
            #     function_scale=self.find_all_fuction_scale(tempfile,diff,minus_sign_change_line_numbers)
            #     print(function_scale)
            #     print("!!")
            #     methods = {}
            #     ctags_lines = read_tags.readlines()
            #     print(ctags_lines)

            #     for change_line_number in change_line_numbers: #change_line_number改变的每一行，分别查找变化的方法和变化的变量，查找变化的变量时还要把变化变量所在的行数给找出来，并且把影响的函数也找出来，但是这里的变化的变量没找对，导致后面也没找对
            #         ##查找变更的类
            #         self.find_function_or_class(change_line_number, ctags_lines,function_scale,methods,dc,'c')
            #         ##查找变更的方法
            #         ctags_function_type=self.find_function_or_class(change_line_number, ctags_lines,function_scale,methods,dc,'f')
            #         ##查找变更的变量
            #         ctags_variable_type=kinds['v'][dc.split('.')[-1]]
            #         self.find_variable_and_related_fuction(change_line_numbers,change_line_number, ctags_lines,function_scale,ctags_variable_type,tempfile,methods,ctags_function_type)

            #     diff["diff_content"] = methods
            #     diff["diff_file"] = dc

            #     commit["diffs"].append(diff)


            # all_diffs.append(commit)
        commits.close()
        return all_diffs

   