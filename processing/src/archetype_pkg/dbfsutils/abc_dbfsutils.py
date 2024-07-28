import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List

from pyspark.sql import SparkSession


@dataclass
class FileInfo:
    path: str
    name: str
    creation_date: datetime
    is_dir: bool


class ABCDbFsUtils(ABC):
    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.jvm = spark.sparkContext._jvm  # type: ignore

    @property
    @abstractmethod
    def file_system(self):
        raise NotImplementedError("will be implemented in child class")

    def get_spark_session(self):
        return self.spark

    def get_fs_path(self, path: str):
        return self.jvm.org.apache.hadoop.fs.Path(path) if isinstance(path, str) else path  # type: ignore

    def list_ls(self, path: str) -> List[FileInfo]:
        result = []
        fs_path = self.get_fs_path(path)
        for p in self.file_system.listStatus(fs_path):
            path = f"{p.getPath()}"
            name = path.split("/")[-1]
            result.append(FileInfo(path=path,
                                   name=name,
                                   is_dir=p.isDirectory(),
                                   creation_date=self.modification_datetime_file(path)))
        return result

    def path_is_dir(self, path: str) -> bool:
        return self.file_system.getFileStatus(self.get_fs_path(path))

    def delete_path(self, path: str):
        if self.path_exists(path):
            self.file_system.delete(self.get_fs_path(path), True)

    def remove_file(self, path: str) -> bool:
        fs_path = self.get_fs_path(path)
        return self.file_system.delete(fs_path)

    def path_exists(self, path: str) -> bool:
        return self.file_system.exists(self.get_fs_path(path))

    def mk_dirs(self, path: str) -> bool:
        fs_path = self.get_fs_path(path)
        return self.file_system.mkdirs(fs_path)

    def get_parent(self, path: str) -> str:
        return self.get_fs_path(path).getParent().toUri().toString()

    def touch_file(self, path: str, overwrite: bool = False):
        self.mk_dirs(self.get_parent(path))
        self.write_file(path, '', overwrite=overwrite)

    def move_file_or_dir(self, source_path: str, target_path: str) -> bool:
        src_fs_path = self.get_fs_path(source_path)
        target_fs_path = self.get_fs_path(target_path)
        self.mk_dirs(target_path)
        return self.file_system.rename(src_fs_path, target_fs_path)

    def write_file(self, path, file_content, overwrite=False):
        self.mk_dirs(self.get_parent(path))
        bw = self.jvm.java.io.BufferedWriter(
            self.jvm.java.io.OutputStreamWriter(self.file_system.create(self.get_fs_path(path), overwrite)))
        bw.write(file_content)
        bw.close()

    def get_fs_root(self) -> str:
        fs_root = self.file_system.getConf().get("fs.defaultFS")
        return " ".join(re.findall("[a-zA-Z]", fs_root))

    def get_list_leaf_dir(self, path):
        list_leaf_dir_scala = self.jvm.org.apache.spark.deploy.SparkHadoopUtil().listLeafDirStatuses(
            self.file_system,
            self.get_fs_path(path))
        return [
            list_leaf_dir_scala.apply(i)
            .getPath()
            .toString()
            .replace(self.get_fs_root().strip('/'), '')
            for i in range(list_leaf_dir_scala.size())
        ]

    def find_partitions_paths_with_pattern(self, path: str, pattern: List[str]) -> List[str]:
        pattern_joined = '/'.join([f'{k}=[^/]+' for k in pattern])
        path_leaf = self.get_list_leaf_dir(path)
        list_result = []
        for path_l in path_leaf:
            if find_path_group := re.search(pattern_joined, path_l):
                list_result.append(os.path.join(path, find_path_group[0]))
        return list_result

    def modification_datetime_file(self, path: str) -> datetime:
        status = self.file_system.getFileStatus(self.get_fs_path(path))
        last_modified = status.getModificationTime()
        return datetime.fromtimestamp(last_modified / 1000)
