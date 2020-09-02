create table general_info (
	id INT PRIMARY KEY,
	name text,
	current_price INT,
	_30_day_change FLOAT,
	_90_day_change FLOAT,
	_180_day_change FLOAT,
	small_icon_url text,
	large_icon_url text
	
);
create table temp_holding (
	id INT PRIMARY KEY,
	name text,
	current_price INT,
	_30_day_change FLOAT,
	_90_day_change FLOAT,
	_180_day_change FLOAT,
	small_icon_url text,
	large_icon_url text
);

create table price_over_time (
	Date text,
	price INT
);

select * from price_over_time
