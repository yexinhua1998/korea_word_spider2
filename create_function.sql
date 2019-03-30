CREATE FUNCTION INITUNGET(amount int) RETURNS boolean
AS $$
BEGIN
    FOR i IN 1..amount LOOP
        INSERT INTO UNGET VALUES(i);
    END LOOP;
    RETURN TRUE;
END;
$$
LANGUAGE PLPGSQL;

CREATE FUNCTION UNINIT() RETURNS boolean
AS $$
BEGIN
    DROP TABLE UNGET CASCADE;
    DROP TABLE RAWCONTENT CASCADE;
    DROP TABLE CONTENT CASCADE;
    DROP FUNCTION INITUNGET(amount int);
    DROP FUNCTION UNINIT();
    DROP FUNCTION SAVERAWCONTENT
    (_docid int,_cid int,_categoryid int,_content text);
    RETURN TRUE;
END;
$$
LANGUAGE PLPGSQL;

CREATE FUNCTION SAVERAWCONTENT
(_docid int,_cid int,_categoryid int,_content text)
RETURNS boolean
--保存一个RAWCONTENT
AS $$
BEGIN
    INSERT INTO RAWCONTENT VALUES(_docid,_cid,_categoryid,_content);
    DELETE FROM UNGET WHERE docid=_docid;
    RETURN TRUE;
END;
$$
LANGUAGE PLPGSQL;

CREATE FUNCTION SAVECONTENT
(_docid int,_cid int ,_categoryid int,_word text,_cite text,_desc text,
_cw text,_jw text,_kw text,_ew text,_att text,_txt text,_dic text,_quote text,
_box text,_naml text,_directory text,_summary text,_other text)
RETURNS boolean
--保存一个content
AS $$
BEGIN
    INSERT INTO CONTENT
    VALUES(_docid,_cid,_categoryid,_word,_cite,_desc,_cw,_jw,
    _kw,_ew,_att,_txt,_dic,_quote,_box,_naml,
    _directory,_summary,_other);
    DELETE FROM RAWCONTENT WHERE docid=_docid;
    RETURN TRUE;
END;
$$
LANGUAGE PLPGSQL;

CREATE FUNCTION SAVE_CATEGORY_DOC(_categoryid int,_docid int)
RETURNS boolean
AS $$
DECLARE
    _num int;
BEGIN
    SELECT COUNT(*) FROM category_doc WHERE categoryid=_categoryid AND docid=_docid
    INTO _num;
    IF _num=0 THEN
        INSERT INTO category_doc (categoryid,docid) VALUES(_categoryid,_docid);
    END IF;
    RETURN TRUE;
END;
$$
LANGUAGE PLPGSQL;
