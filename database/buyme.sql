use c9; 

Drop table if exists posts;
Drop table if exists userpass;
Drop table if exists messages;
Drop table if exists items;
Drop table if exists user;

create table user(
    uid int auto_increment,
    username varchar(50) not null,
    name varchar(50) not null,
    gradYear int not null,
    dorm varchar(20) not null,
    email varchar(50) not null,
    key username (username),
    primary key(uid) 
) Engine = InnoDB;

create table items (
    iid int auto_increment,
    description varchar(100),
    price float not null,
    category set('food','clothing','shoes','services','utility',
    'makeup','textbooks','bath-body','event','other') not null,
	other varchar(30),
	photo blob,
    role enum('buyer', 'seller') not null,
    uploaded timestamp DEFAULT CURRENT_TIMESTAMP,
    primary key(iid)
) Engine = InnoDB;

create table posts (
     uid int not null,
     iid int not null,
     sold enum('false','true') not null,
     key uid (uid),
     key iid (iid),
     primary key (uid,iid),
     foreign key (uid) references user (uid) on delete cascade,
     foreign key (iid) references items (iid) on delete cascade
) Engine = InnoDB;

create table userpass (
      username varchar(50) not null,
      hashed char(60),
      primary key (username),
      foreign key (username) references user (username) on delete cascade
) Engine = InnoDB;

create table messages (
    messageId int auto_increment,
    sender int not null,
    receiver int not null,
    iid int not null,
    message varchar(200) not null,
    readMessage enum('false','true') not null,
    messageSent timestamp DEFAULT CURRENT_TIMESTAMP,
    primary key(messageId),
    foreign key (iid) references items (iid) on delete cascade,
    foreign key (sender) references user (uid) on delete cascade,
    foreign key (receiver) references user (uid) on delete cascade
)
Engine = InnoDB;



