#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parse git logs.

These parsing functions expect output of the following command:

    git log --pretty=raw --numstat

commit be2adad9c8340ef7fd97db6bf9c5a3fef0fd8b74
tree 6cf84a593543ebffabe6e0d2f315bd020a67bfb7
parent 450baad1184bb7c0be2c2cf1ded9c54ada9aa582
author ”MMMMMMorty <465346562@qq.com> 1595133813 +0800
committer ”MMMMMMorty <465346562@qq.com> 1595133813 +0800

    2020-07-19 12：42
    第二次提交




"""

#git词法分析器

import re,os,sys
#re 正则表达式

__author__ = 'Tavish Armstrong'
__email__ = 'tavisharmstrong@gmail.com'
__version__ = '0.2.1'

NOTE=r'''\/\/(.*)\n'''

MULI_NOTE=r'''\/\*[\w\W]*?\*\/'''

FILE_MODE=r'''new file mode \d+\n'''

PAT_APP=r'''
(
appname\ (?P<appname>[^\n]+)\n
version\ (?P<version>[^\n]+)\n
)
'''

PAT_AUTHOR=r'''
author\ +(?P<email><(.*)>) (?P<time>\d+) (?P<time_zone>[+\-]\d\d\d\d)
'''

PAT_COMMITER=r'''
committer\ +(?P<email><(.*)>) (?P<time>\d+) (?P<time_zone>[+\-]\d\d\d\d)
'''

PAT_COMMIT = r'''
(
commit\ (?P<commit>[a-f0-9]+)\n
tree\ (?P<tree>[a-f0-9]+)\n
(?P<parents>(parent\ [a-f0-9]+\n)*)
(?P<author>author \s+(.+)\s+<(.*)>\s+(\d+)\s+([+\-]\d\d\d\d)\n)
(?P<committer>committer \s+(.+)\s+<(.*)>\s+(\d+)\s+([+\-]\d\d\d\d)\n)\n
(?P<message>
(\ \ \ \ [^\n]*)*
)
\n
)
'''    #r变成非转义的原始字符串
# diff --git a/Classes/Notifications/NotificationSectionController.swift b/Classes/Notifications/NotificationSectionController.swift
# index 2992a4e4..f4991413 100644
#--- a/Classes/Repository/RepositoryClient.swift 更改前的
#+++ b/Classes/Repository/RepositoryClient.swift 更改后的
#@@ -1,165 +1,164 @@  行数？
#第一个是-1,2，-表示修改前，1，2表示第一行开始的两行，那么后面的+1，2表示修改后文件的第一行开始的两行内容。
PAT_DIFF = r'''
(
diff\ \-\-git\ a(?P<diff_file>[^\n]+)\ b[^\n]+\n
index\ (?P<index>[a-z\.0-9\ ]+)\n
^\-\-\-\ [^\n]+\n
^\+\+\+\ b[^\n]+
)
'''

#@@ -1,165 +1,164 @@
PAT_DIFF_PART = r'''
(@@\ \-(?P<org_begin_line>\d+),(?P<org_end_line>\d+)\ \+(?P<chg_begin_line>\d+),(?P<chg_end_line>\d+)\ @@\n)'''

RE_APP = re.compile(PAT_APP, re.MULTILINE | re.VERBOSE)
#分支
RE_COMMIT = re.compile(PAT_COMMIT, re.MULTILINE | re.VERBOSE) #e.VERBOSE可以把正则表达式写成多行，并且自动忽略空格
#分支
RE_DIFF = re.compile(PAT_DIFF, re.MULTILINE | re.VERBOSE)# ^和$的规则就是针对边界进行判定的，所以这些规则根据对换行符进行不同的处理，就会有不同的结果。当一串字符串中包含有换行符，如果设置MULTILINE标示，就当作换符处理，如果不设置就当作一行文本处理。
#总树
RE_DIFF_PART = re.compile(PAT_DIFF_PART, re.MULTILINE | re.VERBOSE)  #compile变成编译对象  Compile a regular expression pattern, returning a pattern object.

RE_MULI_NOTE=re.compile(MULI_NOTE,re.MULTILINE | re.VERBOSE)
# -------------------------------------------------------------------
# Main parsing functions


def parse_commits(data):
    '''Accept a string and parse it into many commits.
    Parse and yield each commit-dictionary.
    This function is a generator.
    '''
    raw_commits = RE_COMMIT.finditer(data) #分支一，第一部分 COMMIT 返回string中所有与pattern相匹配的全部字串，返回形式为迭代器
    for rc in raw_commits:#一个commit
        full_commit = rc.groups()[0] #一整个的commit
        parts = RE_COMMIT.match(full_commit).groupdict()#它返回一个字典，包含所有经命名的匹配子群，键值是子群名  (?P<user>\w+)： {'user': 'myname'}，其中一个commit
        parsed_commit = parse_commit(parts)#分析一个子群
        yield parsed_commit #利用yield关键字关起函数，给调用者返回一个值，同时保留了当前的足够多的状态，可以使函数继续执行

def parse_diff(data): #
    #print(data)
    raw_diffs = RE_DIFF.finditer(data) #返回内容的迭代器
    for rc in raw_diffs:
        full_commit = rc.groups()[0]
        parts = RE_DIFF.match(full_commit).groupdict()#只留下了有键值对的 #diff_file  index
        """
        --- a/Classes/Repository/RepositoryClient.swift
        +++ b/Classes/Repository/RepositoryClient.swift
        @@ -1,165 +1,164 @@
        
        find_str = parts["diff_file"] + "\n" + \
                       "@@ -" + parts["org_begin_line"] + "," + parts["org_end_line"] + \
                         " +" + parts["chg_begin_line"] + "," + parts["chg_end_line"] + " @@"""
        begin_index = data.index("+++ b" + parts["diff_file"]) #+++ b/Classes/Notifications/NotificationSectionController.swift的开始索引位置 
        end_index = data.find("diff --git a", begin_index)#下一个commit的diff --git a开始前
        if end_index == -1:#后面没有diff --git
            end_index = len(data) #data长度
        diff_parts_content = data[(begin_index+len("+++ b" + parts["diff_file"])):end_index] #截取包括diff_parts及后面的内容
        raw_diff_parts = RE_DIFF_PART.finditer(diff_parts_content)#Diff part   ？？？？？？
        content_diff_parts = []
        i=0
        for dp in raw_diff_parts:
            full_diff = dp.groups()[0]#'@@ -1,290 +1,292 @@\n'
            ###获取diff文件内容
            #print(full_diff)
            begin_index_fc = diff_parts_content.index(full_diff) + len(full_diff)
            end_index_fc = diff_parts_content.find("@@ -", begin_index_fc)
            if end_index_fc == -1:
                end_index_fc = len(diff_parts_content)
            tempfile_content = diff_parts_content[begin_index_fc:end_index_fc] #diff 文件内容
            file_names = parts["diff_file"].split('/')#选取diff 文件的文件名字
            if not file_names[-2]=='':
                file_name=file_names[-2]+"_"+file_names[-1]
            else:
                file_name=file_names[-1]
            print(file_name)
            with open(file_name,"w") as ffd:
                ##TODO: Save and remove + and -
                ffd.write(tempfile_content) #打开这个diff 文件，将diff内容写进去（swift文件时生成的）
            content_diff_parts.append(file_name)#这个列表就装着diff内容的文件名
            #content_diff_parts.append({"diff_line":full_diff,"file_name":file_name})
            #print({full_diff:file_name})

        parts["diff_file"] = content_diff_parts
        yield parts

def parse_commit(parts):
    '''Accept a parsed single commit. Some of the named groups
    require further processing, so parse those groups.
    Return a dictionary representing the completely parsed
    commit.
    '''
    commit = {}
    #print(parts)
    # commit['appname'] = parts['appname']
    # commit['version'] = parts['version']
    commit['commit'] = parts['commit']
    commit['tree'] = parts['tree']
    parent_block = parts['parents']
    commit['parents'] = [
        parse_parent_line(parentline)
        for parentline in
        parent_block.splitlines()
    ]
    # commit['author'] = parse_author_line(parts['author'])
    # commit['committer'] = parse_committer_line(parts['committer'])
    commit = parse_author_line(parts['author'],commit)
    commit = parse_committer_line(parts['committer'],commit)
    message_lines = [
        parse_message_line(msgline)
        for msgline in
        parts['message'].split("\n")
    ]#多行的message
    commit['message'] = "\n".join(
        msgline
        for msgline in
        message_lines
        if msgline is not None
    )#其中一句分开来

    return commit


# -------------------------------------------------------------------
# Parsing helper functions


def parse_hash_line(line, name):
    RE_HASH_LINE = name + r' ([abcdef0-9]+)'
    result = re.match(RE_HASH_LINE, line) #	决定 RE 是否在line刚开始的位置匹配
    if result is None:
        return result
    else:
        return result.groups()[0]


def parse_commit_line(line):#可无
    return parse_hash_line(line, 'commit')#是否匹配commit


def parse_parent_line(line):
    return parse_hash_line(line, 'parent')#是否匹配parent


def parse_tree_line(line):#可无
    return parse_hash_line(line, 'tree')#是否匹配tree


def parse_person_line(line, commit,name):
    RE_PERSON = name + r' (.+) <(.*)> (\d+) ([+\-]\d\d\d\d)'
    result = re.match(RE_PERSON, line)
    if result is None:
        return commit
    else:
        groups = result.groups()  #如果匹配上了就将匹配的字符串转换为对应值得元组
        real_name = groups[0]
        email = groups[1]
        timestamp = int(groups[2])
        timezone = groups[3]
        if name=='author':
            return commit
        commit[name+'_name']=real_name
        commit[name+'_email']=email
        commit[name+'_time']=str(timestamp)
        commit[name+'_timezone']= timezone
        # d_result = {
        #     'name': name,
        #     'email': email,
        #     'date': timestamp,
        #     'timezone': timezone,
        # }
        # return d_result #最后输出字典
        return commit


def parse_committer_line(line,commit):
    return parse_person_line(line,commit, 'committer') #匹配committer


def parse_author_line(line,commit):
    return parse_person_line(line, commit,'author') #匹配author


def parse_message_line(line): 
    RE_MESSAGE = r'    (.*)' #匹配空格数 （剩余）
    result = re.match(RE_MESSAGE, line)
    if result is None:
        return result
    else:
        return result.groups()[0]


def parse_numstat_line(line):
    RE_NUMSTAT = r'(\d+|-)\s+(\d+|-)\s+(.*)' #读取一行 数字（空白）数字（空白）剩余
    result = re.match(RE_NUMSTAT, line)#分割
    if result is None:
        return result
    else:
        (sadd, sdel, fname) = result.groups()
        try:
            return (int(sadd), int(sdel), fname)
        except ValueError:
            return (sadd, sdel, fname)

def delete_note(data):
    data=re.sub(NOTE,r'''\n''',data)
    return data

def delete_mult_note(data):
    # data=re.sub(NOTE,r'''\/\*( )*?\*\/''',data)
    notes=RE_MULI_NOTE.findall(data)
    for note in notes:
        temp=note.replace("{"," ")
        Note=temp.replace("}"," ")
        data=data.replace(note,Note)
    return data

def delete_new_file_mode(data):
    data=re.sub(FILE_MODE,r'''''',data)
    return data

def get_appname_and_version(data):
    parts = RE_APP.match(data).groupdict() 
    return parts['appname'],parts['version']

def none_author_and_commit(data):
    data=re.sub(PAT_AUTHOR,r'''\nauthor undefined <\g<email>> \g<time> \g<time_zone>\n''',data)
    data=re.sub(PAT_COMMITER,r'''\ncommitter undefined <\g<email>> \g<time> \g<time_zone>\n''',data)
    return data