# -*- coding: utf-8 -*-
"""
    blogger
    -------
    
    A personal blog framework with flask and sqlite3

    :copyright: (c) 2017 by cjhang.
    :license: MIT, see LICENSE for details.
"""

import os
import sqlite3
import codecs
from datetime import datetime
import markdown
from flask import Flask, request, g, redirect, url_for, render_template,\
    flash

# create the application
app = Flask(__name__)

# configuration
DATABASE = os.path.join(app.root_path, 'blogger.db')
BLOGS = os.path.join(app.root_path, 'blogs')
DEBUG = True
SECRET_KEY='23gtj7992de#dk$df@df2d4fs'
PER_PAGE = 10

app.config.from_object(__name__)
app.config.from_envvar('BLOGGER_SETTINGS', silent=True)
extensions = ['markdown.extensions.meta', 
    'markdown.extensions.toc', 'pymdownx.githubemoji', 'pymdownx.tasklist',
    'markdown.extensions.extra', 'markdown.extensions.codehilite']
md = markdown.Markdown(extensions = extensions);


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def query_db(query, args=(), method='r'):
    """Queries the database and returns a list of dictionaries."""
    db = get_db()
    cur = db.execute(query, args)
    if method == 'w':
        db.commit()
        return 0
    elif method == 'r':
        rv = cur.fetchall()
        return rv

def readMarkdown(filename):
    with codecs.open(filename, encoding='utf-8') as htmlSource:
        body = md.convert(htmlSource.read())
    toc = md.toc
    meta = md.Meta
    name = meta['name'][0]
    title_zh = meta['title_zh'][0]
    author = meta['author'][0] # TODO multi author surpport
    # try:
        # release = str(datetime.strftime(datetime.strptime(meta['release'][0], 
            # '%Y-%m-%d'),'%Y年%m月%d日'))
    # except:
        # release = ""
    # try:
        # revise = str(datetime.strftime(datetime.strptime(meta['revise'][0],
            # '%Y-%m-%d'),'%Y年%m月%d日'))
    # except:
        # revise = ""
    release = meta['release'][0]
    revise = meta['revise'][0]
    tags = meta['tags'][0] # TODO: multi tag surpport, should modify database
    abstract = meta['abstract'][0]
    return name, title_zh, author, release, revise, tags, abstract, toc, body

# def num2date(num):
    # if num > 90000000 and num < 19000000:
        # return 'Invalid Date'
    # year = num // 1000
    # month = (num - year*1000) // 100
    # day = num - year*1000 - month*100
    # return str(year)+'年'+str(month)+'月'+str(day)+'日'

@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Initialized the database')

@app.cli.command('updateblog')
def updatedb_command():
    blogs_fs = os.listdir(BLOGS)
    blogs_db = query_db('select name, revise from blogs')
    blogs_name_db = []
    for item in blogs_db:
      blogs_name_db.append(item['name'])
    for item in blogs_fs:
        print(os.path.join(BLOGS, item, item+'.blog'))
        name, title_zh, author, release, revise, tags, abstract, toc,content \
        = readMarkdown(os.path.join(BLOGS, item, item+'.blog'))
        if name in blogs_name_db:
            query_db('''update blogs set revise = ?, abstract = ?, toc = ?,
                        content = ? where name = ? and revise < ?''',
                        [revise, abstract, toc, content, name, revise], 
                        method='w')
        else:
            # create in blogs table
            query_db('''insert into blogs (name, title_zh, author, release, 
                     revise, tags, abstract, toc, content) 
                     values (?, ?, ?, ?, ?, ?, ?, ?, ?)''',[name, title_zh, 
                     author, release, revise, tags, abstract, toc, content], 
                     method='w')

@app.route('/')
def show_updates():
    blogs=query_db('''
        select name, title_zh, revise, abstract from blogs 
        where release != "" order by revise desc limit 30''')
    return render_template('update.html', blogs=blogs)

@app.route('/blogs/<blogname>')
def show_article(blogname):
    return render_template('article.html', article=query_db('''
        select title_zh, release, revise, toc, content from blogs
        where name = ?''', [blogname]))

@app.route('/add', methods=['GET', 'POST'])
# Currently, the add post only used for test
def add_blog():
    if request.method == 'POST':
        content = md.convert(request.form['content'])
        toc = md.toc
        query_db('''insert into blogs (name, title_zh, author, release, 
                revise, tags, abstract, toc, content) 
                values (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                [request.form['name'], request.form['title_zh'], 
                 request.form['author'], request.form['release'], 
                 request.form['revise'], request.form['tags'],
                 request.form['abstract'], toc, content], 
                method='w')
        flash('Blog was successfully posted')
        return redirect(url_for('show_updates'))
    return render_template('add.html')

    
if __name__ == '__main__':
    app.run()
