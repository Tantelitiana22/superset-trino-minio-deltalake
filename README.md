# DATA LAKEHOUSE WITH TRINO, MINIO, AND DELTA LAKE

This project provides a Docker configuration to create a local data lakehouse environment for development.

## Requirements

You must have Docker and Docker Compose installed on your computer.

## How to Start

Just run the following command:
```sh
docker-compose up -d
```

## Minio for Testing

### Requirements

To have Spark in your local environment, install `pipenv` on your computer. Inside the `processing` directory, run the following command:
```sh
pipenv install --dev
```
Use the `pipenv` virtual environment afterward.

### How to Use

1. **Create a Bucket**: When you are in the Minio interface, create a bucket named `first-bucket`.
2. **Upload Data**: After creating the bucket, upload the data from the `data/social` directory into the bucket to get the following path:
   ```
   s3a://first-bucket/raw/social/bilan-social-tranche-dage-detaillees-pour-15-corps.csv
   ```
3. **Create Another Bucket**: Create a bucket named `prepared`.
4. **Run the Script**: Run the script named `runner.py`.

As a result, you will get a Delta Lake table inside Minio with the following path:
```
s3a://prepared/delta/social_data
```

## Access

To access the Minio interface, open your browser and go to `localhost:9001`.
```
Username: minio
Password: minio123
```
For the Trino interface, go to `localhost:8080`.

## Trino First Approach

Run the following command to access the Trino terminal:
```sh
docker-compose exec -it trino-coordinator trino
```

When you are in the terminal, check the list of your catalogs:
```sql
SHOW CATALOGS;
```
If everything is set up correctly, you should see the following result:
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

Next, check if you have access to the information inside the tables:
```sql
SHOW SCHEMAS FROM delta;
```
You should see:
```
    Schema
--------------------
 default
 information_schema
(2 rows)
```

Now, let's create our first table from Minio data:
```sql
CREATE SCHEMA IF NOT EXISTS delta.social
WITH (location = 's3a://prepared/delta/social_data');
```

Next, create a table from the existing Delta table:
```sql
CALL delta.system.register_table(schema_name => 'social', table_name => 'social_paris_table', table_location => 's3a://prepared/delta/social_data');
```

Finally, query this table:
```sql
SELECT * FROM delta.social.social_paris_table LIMIT 20;
```