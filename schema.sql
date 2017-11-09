drop table if exists project;
create table project (
	id integer primary key autoincrement,
	riverbasin text not null,
	proj_name text not null
);

drop table if exists feature;
create table feature (
	id integer primary key autoincrement,
	bldg_type text,
	bldg_name text,
	feature_id integer not null,
	status integer not null,
	lat double not null,
	long double not null,
	proj_id integer not null,
	foreign key(proj_id) references project(id)
);