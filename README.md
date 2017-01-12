Blogger
=======

Introduction
------------
My own simple blog system, based on flask, it is still under heavilly develop,
currently can only show, add and update blogs from markdown source file.

Dependents
----------
To use blogger, you should have flask(>=0.12), python-markdown(>=2.6) installed.

Usage
-----
Initialize the database run:
```shell
export FLASK_APP=blogger.py
flask initdb
```

Then make a new directory named 'blogs', put all your blogs in it, run:
```shell
flask updateblog
```
to add and update the blogs in database.

Finally, run:
```shell
flask run
```
make blogger run in localhost:5000.
