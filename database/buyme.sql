use c9; 

Drop table if exists user;
Drop table if exists items;
Drop table if exists posts;
Drop table if exists userpass;

create table user(
    uid int auto_increment,
    username varchar(50) not null,
    name varchar(50) not null,
    gradYear int not null,
    dorm varchar(20) not null,
    email varchar(50) not null,
    primary key(uid)
) Engine = InnoDB;

create table items (
    iid int auto_increment,
    description varchar(100),
    price float not null,
    availability enum('yes','no') not null,
    urgency int,
    check (urgency >=1 and urgency <= 10),
    category set('food','clothing','shoes','services','utility',
    'makeup','bath/body','event','other') not null,
	other varchar(30),
	photo blob,
    role enum('buyer', 'seller') not null,
    primary key(iid)
) Engine = InnoDB;

create table posts (
     uid int,
     iid int,
     primary key (uid,iid),
     foreign key (uid) references user (uid),
     foreign key (iid) references items (iid)
) Engine = InnoDB;

create table userpass(
       username varchar(50) not null,
       hashed char(60),
       primary key (username),
       foreign key (username) references user (username)
) Engine = InnoDB;
