use c9;

insert into items (description, price, availability, category, role) values 
('Ugg boots',50,'yes','shoes','seller');

insert into items (description, price, availability, category, role) values 
('Zara dress',35,'yes','clothes','seller');

insert into items (description, price, availability, category, other, role) values 
('Muji stationery',5,'yes','other','stationery','seller');

insert into items (description, price, availability, category, role) values 
('Peach palette',29,'yes','makeup','seller');

insert into user (name,username,gradYear,dorm,email) values ('Wendy Wellesley','wwellesley',2020,'McAfee Hall','wwelles@wellesley.edu');
insert into user (name,username,gradYear,dorm,email) values ('Sally Stone','sstone',2021,'Freeman Hall','sstone@wellesley.edu');
insert into user (name,username,gradYear,dorm,email) values ('Hill Clinton','hclint',2020,'Stone-Davis Hall','hclint@wellesley.edu');

insert into posts (uid,iid) values (1,1);
insert into posts (uid,iid) values (2,2);
insert into posts (uid,iid) values (3,3);
insert into posts (uid,iid) values (1,4);

insert into userpass(username, hashed) values ('wwellesley','scooby');
insert into userpass(username, hashed) values ('sstone','doo');
insert into userpass(username, hashed) values ('hclint','abc');