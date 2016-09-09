use cabmate;
insert into person(Name) values('TEST');
SET last_file_id = LAST_INSERT_ID();
insert into driver(Driver, DriverNumber) values(last_file_id, 9008);

