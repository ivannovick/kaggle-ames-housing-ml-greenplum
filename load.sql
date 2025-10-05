COPY public.training_bronze
FROM '/home/gpadmin/housing/train.csv'
WITH (
    FORMAT csv,
    HEADER true,
    DELIMITER ',',
    QUOTE '"',
    NULL 'NA',
    ENCODING 'UTF8'
);

