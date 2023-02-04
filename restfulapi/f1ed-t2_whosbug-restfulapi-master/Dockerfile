FROM centos:7.8.2003
MAINTAINER HuShenwei<1223929119@qq.com>
COPY ./Python-3.7.0.tgz /root
COPY ./requirements.txt /root
COPY ./whosbug /workspace
COPY ./operations.py /workspace
WORKDIR /root
RUN yum -y install wget
# RUN rpm -ivh https://repo.mysql.com//mysql57-community-release-el7-11.noarch.rpm
# RUN rpm -ivh http://repo.mysql.com/mysql80-community-release-el6-1.noarch.rpm
# RUN yum -y install mysql57-community-release-el7-10.noarch.rpm
# RUN yum -y install mysql-community-server
# RUN yum -y install mysql-community-libs.x86_64
# RUN yum -y install mysql-community-client.x86_64
# RUN yum install https://download.postgresql.org/pub/repos/yum/9.4/redhat/rhel-7-x86_64/pgdg-redhat94-9.4-3.noarch.rpm
# RUN yum install postgresql12
RUN yum  -y install postgresql-devel* 
RUN yum -y install https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
RUN yum -y install postgresql12.x86_64
RUN tar -zxvf Python-3.7.0.tgz
RUN yum install -y zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel xz xz-devel libffi-devel gcc libffi-devel make
RUN mkdir /usr/local/python3
WORKDIR /root/Python-3.7.0
RUN ./configure --prefix=/usr/local/python3
RUN make && make install
RUN ln -s /usr/local/python3/bin/python3 /usr/local/bin/python3
RUN ln -s /usr/local/python3/bin/pip3 /usr/local/bin/pip3
RUN python3 -V
RUN pip3 -V
WORKDIR /root
# RUN mysql -V
RUN pip3 install -r requirements.txt
WORKDIR /workspace
RUN yes | mv operations.py /usr/local/python3/lib/python3.7/site-packages/django/db/backends/mysql/operations.py
CMD python3 manage.py makemigrations
CMD python3 manage.py migrate
CMD python3 manage.py runserver 0.0.0.0:8000