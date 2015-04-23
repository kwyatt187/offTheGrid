create table users (
       id integer primary key autoincrement,
       username text not null,
       password text not null,
       email text not null
);

create table afterparties (
       id integer primary key autoincrement,
       location text not null,
       date text not null,
       description text not null,
       username text not null,
       foreign key(username) references users(username)
);

create table locations (
       id integer primary key autoincrement,
       location text not null,
       lat float null,
       lng float null
);
