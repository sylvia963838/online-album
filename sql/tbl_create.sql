drop database if exists albumDB;
create database albumDB;
use albumDB;


create table User
(
	username varchar(20) not null primary key,
	firstname varchar(20) not null,
	lastname varchar(20) not null,
	password varchar(256) not null,
	email varchar(40) not null
);

create table Album
(
	albumid int not null auto_increment primary key,
	title varchar(50) not null,
	created timestamp not null default current_timestamp,
	lastupdated timestamp not null default current_timestamp,
	username varchar(20) not null,
	access ENUM('public', 'private'),
	foreign key (username) references User(username)	
);

create table Photo
(
	picid varchar(40) not null primary key,
	format char(3) not null,
	date timestamp not null default current_timestamp
);

create table Contain
(
	sequencenum int not null primary key,
	albumid int not null,
	picid varchar(40) not null,
	caption varchar(255) not null,
	foreign key (albumid) references Album(albumid),
	foreign key (picid) references Photo(picid)

);

create table AlbumAccess
(
	albumid int not null,
	username varchar(20) not null,
	foreign key (albumid) references Album(albumid),
	foreign key (username) references User(username),
	primary key (albumid, username)
);

