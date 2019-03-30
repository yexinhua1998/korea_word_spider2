CREATE INDEX unget_index ON UNGET USING HASH (docid);
CREATE INDEX rawcontent_docid_index ON RAWCONTENT USING HASH(docid);
CREATE INDEX content_docid_index ON CONTENT USING HASH(docid);
CREATE INDEX category_doc_categoryid_index ON category_doc USING HASH(categoryid);
CREATE INDEX category_doc_docid_index ON category_doc USING HASH(docid);
