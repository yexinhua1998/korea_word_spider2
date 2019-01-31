CREATE INDEX unget_index ON UNGET USING HASH (docid);
CREATE INDEX rawcontent_docid_index ON RAWCONTENT USING HASH(docid);
CREATE INDEX content_docid_index ON CONTENT USING HASH(docid);
