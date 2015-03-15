
CREATE TABLE coffeedata (
    id bigserial NOT NULL PRIMARY KEY,
    temperature numeric,
    measurement_timestamp timestamp
);

ALTER TABLE coffeedata OWNER TO postgres;


CREATE TABLE coffeestate (
    id bigserial NOT NULL PRIMARY KEY,
    power text,
    brew text
);
ALTER TABLE coffeestate OWNER TO postgres;

INSERT INTO coffeestate (id, power, brew) values (1, 'Off', 'Strong');