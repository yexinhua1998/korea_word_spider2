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
