"""
Example of simple data processing
"""
from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
from pyspark.sql import types as ty

SOCIAL_DATA_PATH = "s3a://first-bucket/raw/social/bilan-social-tranche-dage-detaillees-pour-15-corps.csv"


def read_social_data(path: str, spark: SparkSession) -> DataFrame:
    schema = ty.StructType([
        ty.StructField("YEARS", ty.IntegerType(), True),
        ty.StructField("FUNCTION", ty.StringType(), True),
        ty.StructField("AGE_RANGE", ty.StringType(), True),
        ty.StructField("NUMBER_ET", ty.IntegerType(), True)
    ])
    return spark.read.csv(path, header=True, sep=";", schema=schema)


def main_iceberg():
    spark = SparkSession.builder \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.spark_catalog.type", "hadoop") \
        .config("spark.sql.catalog.spark_catalog.warehouse", "s3a://prepared/") \
        .enableHiveSupport() \
        .getOrCreate()
    # dbfs_utils = S3Utils(spark, "s3a://first-bucket")
    df_input = read_social_data(SOCIAL_DATA_PATH, spark)

    df_input.write.format("iceberg").mode("overwrite").saveAsTable("social_paris_table")


def main_delta():
    spark = SparkSession.builder.appName("MyApp") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

    df_input = read_social_data(SOCIAL_DATA_PATH, spark)

    df_input.write.format("delta") \
        .option("path", "s3a://prepared/delta/social_data") \
        .mode("overwrite").saveAsTable("social_paris_table")


if __name__ == '__main__':
    main_delta()
