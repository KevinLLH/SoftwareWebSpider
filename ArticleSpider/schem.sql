CREATE TABLE jobble_article
(
    title VARCHAR(200) NOT NULL,
    create_date DATE,
    url VARCHAR(300) NOT NULL,
    url_object_id INT(50) PRIMARY KEY NOT NULL,
    front_image_url VARCHAR(300),
    front_image_path VARCHAR(200),
    comment_nums INT(11) DEFAULT 0,
    fav_nums INT(11) DEFAULT 0,
    praise_nums INT(11) DEFAULT 0,
    tag VARCHAR(200),
    content LONGTEXT
);
ALTER TABLE jobble_article COMMENT = '伯乐在线表';

CREATE TABLE report_of_6080
(
    id INT(200) NOT NULL,
    name VARCHAR(100),
    sltj VARCHAR(50) ,
    mzt VARCHAR(50) ,
    zrbzf VARCHAR(50) ,
    rjgcgl VARCHAR(50) ,
    rjtxjg VARCHAR(50) ,
    yyxz VARCHAR(50) ,
    bxjs VARCHAR(50) ,
    ydyjsfwd VARCHAR(50) ,
    fbsjs VARCHAR(50) ,
    sjwj VARCHAR(50) ,
    mddxffjc VARCHAR(50) ,
    dsjjs VARCHAR(50) ,
    sjkxt VARCHAR(50) ,
    ydyjsdl VARCHAR(50) ,
    qyydyyykf VARCHAR(50) ,
    xnhyyjs VARCHAR(50) ,
    qyjg VARCHAR(50) ,
    ydkfjs VARCHAR(50)

);
ALTER TABLE report_of_6080 COMMENT = '6080成绩表';


CREATE TABLE lcsoft_article
(
    title VARCHAR(200) NOT NULL,
    url VARCHAR(300) NOT NULL,
    url_object_id INT(50) PRIMARY KEY NOT NULL,
    front_image_url VARCHAR(300),
    front_image_path VARCHAR(200),
    type VARCHAR(50),
    size VARCHAR(50),
    update_time DATE,
    content LONGTEXT,
    tag VARCHAR(200),
    fav_nums INT(11) DEFAULT 0,
    download_urls INT(11) DEFAULT 0

);
ALTER TABLE lcsoft_article COMMENT = '绿茶软件园表';