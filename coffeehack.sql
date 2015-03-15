
CREATE TABLE coffeedata (
    id bigserial NOT NULL PRIMARY KEY,
    temperature numeric,
    measurement_timestamp timestamp
);

ALTER TABLE coffeedata OWNER TO postgres;


