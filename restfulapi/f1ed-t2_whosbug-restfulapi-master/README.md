# Django App
用于`commit`记录的插入与根据函数查询可能的Owner
## 启动
运行容器并进入容器， -e 后面为环境变量，按照实际情况配置

`docker run -it -e POSTGRES_DBNAME="whosbug" -e POSTGRES_USER="guest" -e POSTGRES_PASSWORD="guest" -e POSTGRES_HOST="39.101.192.144" -e POSTGRES_PORT="5432" -p 9000:8000 <IMAGE>:<TAG>`

`docker run` 时已自动执行`migrate`与`runserver 0.0.0.0:8000`	

进入容器后（可选）创建超级用户
```
python3 manage.py createsuperuser
```

```
退出容器并保持其后台运行
```
Ctrl + p + q
```


