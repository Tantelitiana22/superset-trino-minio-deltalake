# DATA LAKEHOUSE WITH TRINO, MINIO AND DELTA LAKE

This project is a docker configuration how allow to create locally
a data lakehouse environnement for development.

## requirements:
You must have docker and docker-compose installed on your computer.

## How to start:

Just run the next command:
```
docker-compose up -d
```

## Minio for test:
### requirements:
To have spark on you local env.
install pipenv on your computer.
Inside processing, run the next command:
```
pipenv install --dev
```
Use pipenv virtualenv after.

### How to?

When you are in the minio interface, create a bucket named `first-bucket`
and ones it 's create, you can put the data inside data/social inside the bucket
to get the next path:
`s3a://first-bucket/raw/social/bilan-social-tranche-dage-detaillees-pour-15-corps.csv`

Ones it done, create a bucket named `prepared` and after run the script named `runner.py`

As result, you will get a delta lake table inside minio with the next path:
`s3a://prepared/delta/social_data`


## ACCESS:
To get access to minio interface, just launch in your browser localhost:9001
```
user_name: minio
password: minio123
```
For trino interface: localhost:8080

## trino first approach:
Run the next command get access to the treno terminal:
```
docker-compose exec -it trino-coordinator trino  
```

When you are in the terminal, check first the list of your catalogs
```
show CATALOGS;
``` 
If all is good, you will get the next result:
```
 Catalog 
---------
 delta   
 hive
 system
 tpcds
 tpch
(5 rows)
```

Let check if we have access to the informations inside of the table:
```
show SCHEMAS FROM delta;

    Schema       
--------------------
 default
 information_schema 
(2 rows)

```

Now, let's create our first table from minio data.

```
CREATE SCHEMA IF NOT EXISTS delta.social
WITH (location = 's3a://prepared/delta/social_data');
```  

Now let's create from existing delta table:
```
CALL delta.system.register_table(schema_name => 'social', table_name => 'social_paris_table', table_location => 's3a://prepared/delta/social_data');

```

Let's now request this table:
```
SELECT * FROM delta.social.social_paris_table LIMIT 20; 
```
