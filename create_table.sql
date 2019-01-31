--记录还没有爬取的数据的docID的表
CREATE TABLE UNGET(
    docid int UNIQUE
);

--记录每个档案页面的content的表
CREATE TABLE RAWCONTENT(
    docid int UNIQUE,
    cid int,
    categoryid int,
    content text
);

--记录已经解析的数据的表
CREATE TABLE CONTENT(
    docid int,
    cid int,
    categoryid int,
    word text,
    cite text,
    desc_ text,
    commment_chinese text,
    comment_japan text,
    comment_korea text,
    comment_english text,
    att text,
    txt text,
    dic text,
    quote text,
    box_ text,
    naml text,
    directory text,
    summary text,
    other text
);
