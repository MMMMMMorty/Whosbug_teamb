import GitParser
import re
import os
from threading import Thread,RLock

kinds={
    'c':{
        "kt":['c','o','d'],
        "kts":['c','o','d'],
        "swift":['p','c'],
        "java":['c'],
        "c++":['c','m','g','n','s','t'],
        "go":[' '],
        "cpp":['c','m','g','n','s','t'],
        "cc":['c','m','g','n','s','t']

    },
    'f':{
        "kt":['m','i'],
        "kts":['m','i'],
        "swift":['f','i'],
        "java":['m','i'],
        "c++":['f'],
        "go":['f'],
        "cpp":['f'],
        "cc":['f'],

    },
    'v':{
        "kt":['C','v'],
        "kts":['C','v'],
        "swift":['v'],
        "java":['e','f'],
        "c++":['e','v'],#枚举数
        "go":['v','c'],
        "cpp":['e','v'],
        "cc":['e','v'],

    }
}

def find_change_commit(commit,diffs,all_diffs):
    threads=[]
    for diff in diffs:
        thread_diff=thread_find_diff(diff,commit)
        thread_diff.start()
        commit=thread_diff.get_commit()
        threads.append(thread_diff)

    for thread_diff in threads:
        thread_diff.join()
    all_diffs.append(commit)
    return all_diffs

def find_all_change_line_numbers( file_name, re_change_mark="^\+"): #找到所有更改的行号，+号是更改了的行
    change_line_numbers = []
    find_all_change_line_numbers={}
    with open(file_name,"r") as fd:
        lines = fd.readlines() #读行
        line_number = 0
        minus_number=0
        for line in lines:
            line_number = line_number+1 
            if re.search("^\-", line):
                minus_number=minus_number+1
            if re.search(re_change_mark, line): #扫描字符串，找到这个 RE 匹配的位置，匹配则说明找到行号,开头是+号且后面带空格
                # if re_change_mark=="^\-" and (re.search("{", line) or re.search("}", line)):#当是”-“号时只检索有”{“和”}“的
                #     change_line_numbers.append(line_number)
                #     continue
                change_line_numbers.append(line_number)  #统计更改了的
                find_all_change_line_numbers[line_number]=line_number-minus_number
        fd.close()
    return change_line_numbers, find_all_change_line_numbers#返回diff里面更改了的行号

def add_to_method(method_name,methods,ctags_line_method,scale):
    if method_name not in methods.keys():#init函数同名问题
        methods[method_name]={
            'lines':[ctags_line_method,],
            'method_scale':str(scale)
        }
    elif method_name in methods.keys() and str(scale) not in methods[method_name].values():#如果重名就带上范围
        method_name=method_name+"_"+str(scale)
        methods[method_name]={
            'lines':[ctags_line_method,],
            'method_scale':str(scale)
        }
    else:
        methods[method_name]["lines"].append(ctags_line_method)

def find_change( change_line_number, ctags_lines,function_scale,ctags_type):#ctags里面寻找更改, 会找到这改变的行对应的class 和改变行数  以及追踪的函数的行数
    """Find all the change with ctags type
        Find the fuction and its scale

    Args:
        ctags_type: None means find the neareast function , 'v' means variable
        change_line_number: change line number
        ctags_lines: read from the ctags file  

    Returns:
        class_name
        ctags line(eg: "['InboxFilterControllerClient', 'InboxFilterController.swift','/^ protocol InboxFilterControllerClient {$/;"', 'p', 'line:12\n']"
    """
    for scale in function_scale:
        left_bracket_line_number=scale[0]
        right_bracket_line_number=scale[1]
        if (change_line_number>=left_bracket_line_number and change_line_number<=right_bracket_line_number ) :#'+'在括号内，在函数体内，在class体内，定义新的函数->class
            for line in reversed(ctags_lines):
                args = line.split('\t')#分隔变量们
                type= (re.findall("\t.\t",line)[0].split('\t')[1])
                line_number =int(re.findall("\tline:\d+",line)[0].split(':')[1])
                if (left_bracket_line_number==line_number or left_bracket_line_number==change_line_number==line_number) and type in ctags_type :#swift
                    # print("change_line_number:",change_line_number,"cur_line_number:",line_number,"scale:",scale,"ctags_type:",type)
                    args.append(scale)
                    args.append(line_number)#记录行号
                    return  args
                if change_line_number==line_number  and type in ctags_type:#括号内的变量,'+'号的行数对应上ctags，
                    # print("change_line_number:",change_line_number,"cur_variable_line_number:",line_number,"ctags_type:",type)
                    args.append(scale)
                    args.append(line_number)
                    return  args
        else:#括号外面的变量
            first = 0
            last = len(ctags_lines) -1
            n=0
            while first < last:
                mid = (first+last) // 2
                line=ctags_lines[mid]
                line_number =int(re.findall("\tline:\d+",line)[0].split(':')[1])
                type= (re.findall("\t.\t",line)[0].split('\t')[1])
                n=n+1
                if change_line_number==line_number:
                    args = line.split('\t')
                    if type in kinds['v'][args[1].split('.')[-1]]:
                        args.append(None)
                        args.append(line_number)#记录行号
                        return   args
                    else:
                        return None
                elif change_line_number < line_number:
                    last = mid - 1
                else:
                    first = mid + 1

            # for line in reversed(ctags_lines):
            #     args = line.split('\t')#分隔变量们
            #     type= (re.findall("\t.\t",line)[0].split('\t')[1])
            #     # line_number = int(re.findall("\d+", args[-1])[0])#line的行数
            #     line_number =int(re.findall("\tline:\d+",line)[0].split(":")[1])
            #     if change_line_number==line_number and type in kinds['v'][args[1].split('.')[-1]]:#括号内的变量,'+'号的行数对应上ctags，
            #         # print("change_line_number:",change_line_number,"cur_variable_line_number:",line_number,"ctags_type:",type)
            #         args.append(None)
            #         args.append(line_number)
            #         return class_name, args
    return  None



def find_all_fuction_scale( file_name,diff): #字典存范围
    brackets=list() #声明数组
    final_branckets={}
    stack = list()
    change_line_numbers=[]
    final_change_line_numbers={}
    with open(file_name,"r") as fd:
        lines = fd.readlines() #读行
        line_number = 0
        minus_number=0
        for line in lines:
            if re.search(r'''\".*\"''', line):
                line=re.sub(r'''\".*\"''',' ',line)
            if re.search(r'''\'.*\'''', line):
                line=re.sub(r'''\'.*\'''',' ',line)
            line_number = line_number+1
            if re.match("^\-",line) :#不算上减号的因为为了与最终文件对应
                minus_number=minus_number+1
                continue 
            if re.search("^\+",line):
                change_line_numbers.append(line_number)
                final_change_line_numbers[line_number]=line_number-minus_number
            while re.search('{', line) or re.search('}', line):
                left_index=line.find('{')
                right_index=line.find('}')
                if 0<=left_index<right_index:
                    stack.append((line_number,"{",minus_number))
                    line=line[left_index+1:]
                elif 0<=right_index<left_index:
                    try:
                        left_line_number=stack.pop()
                        left_bracket_line_number=left_line_number[0]
                        left_minus_number=left_line_number[2]
                    except IndexError:
                        print(line)
                        print(line_number)
                        print(brackets)
                        print(file_name)
                    brackets.append((left_bracket_line_number,line_number))
                    final_branckets[(left_bracket_line_number,line_number)]=(left_bracket_line_number-left_minus_number,line_number-minus_number)
                    line=line[right_index+1:]
                elif right_index>=0 and left_index==-1:
                    
                    try:
                        left_line_number=stack.pop()
                        left_bracket_line_number=left_line_number[0]
                        left_minus_number=left_line_number[2]
                    except IndexError:
                        print(line)
                        print(line_number)
                        print(brackets)
                        print(file_name)       
                    brackets.append((left_bracket_line_number,line_number))
                    final_branckets[(left_bracket_line_number,line_number)]=(left_bracket_line_number-left_minus_number,line_number-minus_number)
                    line=line[right_index+1:]
                elif left_index>=0 and right_index==-1:
                    stack.append((line_number,"{",minus_number))
                    line=line[left_index+1:]
                # if re.search('{', line) and re.search('}', line):  #{}
                #     left_index=line.find('{')
                #     right_index=line.find('}')
                #     if left_index< right_index:
                #         brackets.append((line_number,line_number))
                #         line=line[right_index+1:]
                #         continue
                #     else: #} {  
                #         pinrt(line)
                #         left_bracket_line_number=stack.pop()[0]#pop
                #         brackets.append((left_bracket_line_number,line_number))
                #         stack.append((line_number,"{"))
                #         line=line[left_index+1:]
                #         continue
                        
                # elif re.search('{', line) and not re.search('}', line): #扫描字符串，找到这个 RE 匹配的位置，匹配则说明找到行号,开头是+号且后面带空格
                #     left_index=line.find('{')
                #     stack.append((line_number,"{"))#push
                #     line=line[left_index+1:]
                #     continue
                # elif re.search('}', line) and not re.search('{', line):
                #     right_index=line.find('}')
                #     left_bracket_line_number=stack.pop()[0]#pop
                #     brackets.append((left_bracket_line_number,line_number))#匹配到的第一个一定是最小范围的
                #     line=line[right_index]
                #     continue
        if(len(stack)>0):
            print(brackets)
            print(stack)
            print(line)
            print(line_number)
            diff["error_message"]="The number of brackets is wrong. Brackets are not paired"
            print("The number of brackets is wrong. Brackets are not paired")#该函数名也会遇到这情况
        fd.close()
    return brackets,change_line_numbers,final_branckets,final_change_line_numbers #返回diff里面更改了的行号


class thread_find_diff(Thread):
    def __init__(self, diff,commit):
        Thread.__init__(self)
        self._diff=diff
        self._commit=commit
        self.lock=RLock()

    def run(self):
        dc = self._diff["diff_file"][0]#获取文件名字list
        self._diff["diff_file"] = {}

        # for dc in dcs:
        tempfile = dc
        if(dc.split('.')[-1] in ["c++","go","cpp" ,"kt" ,"kts","swift","java","cc"]):
            read_tags = os.popen("uctags --fields=+n -o - --sort=no %s"%tempfile)#跑这个环境
            # change_line_numbers = find_all_change_line_numbers(tempfile)
            # minus_sign_change_line_numbers = find_all_change_line_numbers(tempfile,re_change_mark="^\- ")#防止减号的”{“和”}“影响
            function_scale,change_line_numbers,final_branckets,final_change_line_numbers=find_all_fuction_scale(tempfile,self._diff)
            # print(function_scale)
            # print("!!")
            methods = {}
            ctags_lines = read_tags.readlines()
            
            # print(ctags_lines)
            threads = []
            for change_line_number in change_line_numbers: #change_line_number改变的每一行，分别查找变化的方法和变化的变量，查找变化的变量时还要把变化变量所在的行数给找出来，并且把影响的函数也找出来，但是这里的变化的变量没找对，导致后面也没找对
                ##查找变更的类
                # self.find_function_or_class(change_line_number, ctags_lines,function_scale,methods,dc,'c')
                ##查找变更的方法
                ctags_function_type=self.find_function_or_class(change_line_number, ctags_lines,function_scale,methods,dc,'f',final_branckets,final_change_line_numbers)
            
                ##查找变更的变量
                ctags_variable_type=kinds['v'][dc.split('.')[-1]]
                self.find_variable_and_related_fuction(change_line_numbers,change_line_number, ctags_lines,function_scale,ctags_variable_type,tempfile,methods,ctags_function_type,final_branckets)
            
            self.lock.acquire()
            self._diff["diff_content"]=(methods)
            self._diff["diff_file"] = dc
            self.lock.release()
            self._commit["diffs"].append(self._diff)
            read_tags.close()
    
    def get_commit(self):
        return self._commit
        

    def find_function_or_class(self,change_line_number, ctags_lines,function_scale,methods,dc,ctags_type,final_branckets,final_change_line_numbers):
        ctags_function_type=kinds[ctags_type][dc.split('.')[-1]]
        ctags_line_method =find_change(change_line_number, ctags_lines,function_scale,ctags_function_type)
        if ctags_line_method:
            ##找到变更的"方法"就存方法
            method_name = "method:" + ctags_line_method[0]
            if not ctags_line_method[-2]==None:
                scale=final_branckets[ctags_line_method[-2]]
            else:
                scale=None
            change_line_number=final_change_line_numbers[change_line_number]
            self.lock.acquire()
            add_to_method(method_name,methods,change_line_number,scale)#与append有关了
            self.lock.release()
        return ctags_function_type

    def find_variable_and_related_fuction(self,change_line_numbers,change_line_number, ctags_lines,function_scale,ctags_variable_type,tempfile,methods,ctags_function_type,final_branckets):
        ctags_line_variable = find_change(change_line_number, ctags_lines,function_scale,ctags_variable_type)#匹配为变量
        if ctags_line_variable and re.search("(public|private|protect)",ctags_line_variable[2]):#如果是全局变量  print(ctags_line_variable[2].split('\t'))
            # variable_name = ctags_line_variable[0] #全局变量的名字没拿到对 ctags_line_variable[2].split('\t')！！
            variable_name = ctags_line_variable[0]
            variable_line_number = ctags_line_variable[-1]
            change_line_numbers_with_variable,final_change_line_numbers = find_all_change_line_numbers(tempfile, variable_name)#找到变化的变量所在行号，改变这个变量可能会影响到行数(没有的时候就不会输出looking)
            #在变量相关中移除变量默认行号
            change_line_numbers_with_variable.remove(variable_line_number)

            for change_line_number_with_variable in change_line_numbers_with_variable:#这里已经把除了变量本身的函数给筛选了
                if change_line_number_with_variable in change_line_numbers:
                    ##变化变量影响的行，本身也在变化的行里面，所以就不用额外处理了
                    continue
                # print("looking for the variable:",variable_name, "change line numbers:", change_line_number_with_variable," connected methods:" ) #查找到这个变量，并且按照变量再找相关的函数
                ctags_line_method = find_change(change_line_number_with_variable, ctags_lines,function_scale,ctags_function_type)
                if ctags_line_method==None:
                    print("This variable is changed the position from ",change_line_number_with_variable)#!!
                    continue
                method_name = variable_name+"_variable_method:" + ctags_line_method[0]
                if not ctags_line_method[-2]==None:
                    scale=final_branckets[ctags_line_method[-2]]
                else:
                    scale=None
                change_line_number=final_change_line_numbers[change_line_number_with_variable]
                self.lock.acquire()
                add_to_method(method_name,methods,change_line_number_with_variable,scale)
                self.lock.release()
            