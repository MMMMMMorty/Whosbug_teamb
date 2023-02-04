## git diff日志的分析器
- 详细介绍
利用ctags工具，解释出diff文件中的方法与变量，然后根据变更的行，推测变更的方法，并最终把一次commit变更的方法列表、所属的owner、日期、当前build的版本号（非必须）通过另外一个目录提供的restapi服务上传到数据库中。

- 当前目录内容介绍
这是之前开发到一半的项目，可以作为参考的基础。
. AddSupportLanguage是添加ctags自定义支持语言的定义文件
. ctags是依赖的语言解析器，在容器中编译
. TestingFile是给CodeDiffTest.py与TagsParserTest.py做测试用的，里面有一些基础的测试，用例与涉及的语言都有待添加
. Dockerfile 用于生成ctags对应的Image，通过docker build/docker push上传镜像到某地址，生成后需要更改uctags文件中的Image地址才能使用
. GitParser.py 负责git的读取和解释
. CodeDiff.py 负责git diff代码文件的解释
. 初次理解可以直接调试CodeDiffTest.py来快速理解项目

- TeamA尝试创建了持续集成：https://f1ed.coding.net/p/t1_whosbug/ci/job?id=267103 ， 构建的镜像会到https://f1ed.coding.net/p/t1_whosbug/artifacts ,要使用的化，要修改uctags的Image路径为构建的镜像的路径