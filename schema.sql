drop table if exists blogs;
create table blogs (
  blog_id integer primary key autoincrement,
  name text not null,
  title_zh text,
  author text,
  release text,
  revise text,
  tags text,
  abstract text,
  toc text,
  content text
);

drop table if exists users;
create table users (
  user_id text not null,
  user_name text not null,
  user_email text
);


drop table if exists comments;
create table comments (
  comment_id integer primary key autoincrement,
  blog_name text not null,
  user_name text not null,
  comment_date text,
  comment_detail text not null
);
