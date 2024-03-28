#!/usr/bin/env python
# coding=utf-8
"""db manager 单元测试"""
import unittest

import pandas
import sqlalchemy as db
from common.db_manager import (DeclarMixin, pd_from_records, pd_read_sql,
                               pd_to_sql)
from qt_quant.model.base_model import BaseModel


class People(BaseModel):
    __abstract__ = True
    name = db.Column(db.String(50), primary_key=True, comment="姓名")
    age = db.Column(db.INTEGER(), comment="年龄")


class Student(People, DeclarMixin):
    __tablename__ = "tb_student"


class Teacher(People, DeclarMixin):
    __tablename__ = "tb_teacher"


def add_table():
    Student.create_table(session="default")
    Teacher.create_table(session="default")


def drop_table():
    ...


class TestTransformer(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        add_table()

    def test_read_to_sql(self):
        data = [['Google', 10], ['Runoob', 12], ['Wiki', 13]]
        df_data = pandas.DataFrame(data, columns=["name", "age"], dtype=float)
        pd_to_sql(df_data, tb=Student)
        result = pd_read_sql("select * from tb_student where name='Google'")
        self.assertIsInstance(result, pandas.DataFrame)

    def test_from_records(self):
        result = pd_from_records(Teacher, filters=[Teacher.age == 13])
        self.assertIsInstance(result, pandas.DataFrame)
