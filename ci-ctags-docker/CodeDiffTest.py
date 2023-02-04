#coding=utf-8
from CodeDiff import *
import unittest
import json
import time
from urllib import request,error
import requests
class CodeDiffTest(unittest.TestCase):
    def test_iosched_diff(self):
        cd = code_diff("/root/workspace/diff.txt")
        all_diffs = cd.analysis()
        print(all_diffs)
        self.send_message_to_database(all_diffs)
        # with open("/root/files/temp1.json" ,"w") as fd:
        #     json.dump(all_diffs,fd)
        #     fd.close()

    # def test_githawk_diff(self):
    #     cd = code_diff("/root/workspace/tx/t2_whosbug/ci-ctags-docker/TestingFiles/githawk.diff")
    #     all_diffs = cd.analysis() #分析
    #     print(all_diffs)
    #     self.send_message_to_database(all_diffs)
    #     with open("/root/workspace/tx/t2_whosbug/ci-ctags-docker/temp1.json" ,"w") as fd:
    #         json.dump(all_diffs,fd)
    #         fd.close()

    # def test_swiftTest0_diff(self):
    #     cd = code_diff("/root/workspace/tx/t2_whosbug/ci-ctags-docker/TestingFiles/swiftTest0.diff")
    #     all_diffs = cd.analysis() #分析
    #     print(all_diffs)
    #     self.send_message_to_database(all_diffs)
    #     with open("/root/workspace/tx/t2_whosbug/ci-ctags-docker/files/swift1.json" ,"w") as fd:
    #         json.dump(all_diffs,fd)
            

    # def test_iosched_diff(self):
    #     cd = code_diff("/root/workspace/tx/t2_whosbug/ci-ctags-docker/TestingFiles/iosched.diff")
    #     all_diffs = cd.analysis()
    #     print(all_diffs)
    #     # self.send_message_to_database(all_diffs)
    #     with open("/root/workspace/tx/t2_whosbug/ci-ctags-docker/files/temp2.json" ,"w") as fd:
    #         json.dump(all_diffs,fd)

    def send_message_to_database(self,data,url='http://39.101.192.144:8000/api/commits/'):
        try:
            head = {"Content-Type": "application/json; charset=UTF-8"} #the request headers
            body_data=json.dumps(data)
            r = requests.post(url,data=body_data,headers=head)
            response_data=r.text
            print(response_data)
            return response_data
        except error.HTTPError as err:
            error_body = err.file.read().decode()
            return  json.loads(result)

if __name__ == '__main__':
    unittest.main()