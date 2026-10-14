create table conductor (
    conductor_id integer primary key,
    name varchar(40) not null,
    email varchar(60)
);

create table ensemble (
    ensemble_id integer primary key,
    name varchar(40) not null,
    conductor_id integer not null,
    rehearsal_day varchar(9) not null,
    start_time char(5) not null,
    end_time char(5) not null,
    room varchar(30),
    foreign key (conductor_id) references conductor (conductor_id)
);

create table player (
    player_id integer primary key,
    first_name varchar(20) not null,
    last_name varchar(20) not null,
    birth_date date not null,
    school_grade integer
);

create table parent (
    parent_id integer primary key,
    name varchar(40) not null,
    phone varchar(12),
    email varchar(60)
);

create table player_parent (
    player_id integer not null,
    parent_id integer not null,
    primary key (player_id, parent_id),
    foreign key (player_id) references player (player_id),
    foreign key (parent_id) references parent (parent_id)
);

create table section (
    section_id integer primary key,
    name varchar(20) not null,
    instrument varchar(20) not null,
    family varchar(10) not null
);

create table membership (
    ensemble_id integer not null,
    player_id integer not null,
    section_id integer not null,
    chair_number integer not null,
    primary key (ensemble_id, player_id),
    unique (ensemble_id, section_id, chair_number),
    foreign key (ensemble_id) references ensemble (ensemble_id),
    foreign key (player_id) references player (player_id),
    foreign key (section_id) references section (section_id)
);
