from pyspark.sql import SparkSession

from src.archetype_pkg.dbfsutils.abc_dbfsutils import ABCDbFsUtils


class S3Utils(ABCDbFsUtils):
    def __init__(self, spark: SparkSession, s3_bucket: str):
        """
        s3_bucket example path: s3a:// example
        :param spark:
        :param s3_bucket:
        """
        self.s3_bucket = s3_bucket
        super().__init__(spark)

    @property
    def file_system(self):
        jsc = self.spark.sparkContext._jsc  # type: ignore
        conf = jsc.hadoopConfiguration()
        return self.jvm.org.apache.hadoop.fs.Path(self.s3_bucket).getFileSystem(conf)  # type: ignore
