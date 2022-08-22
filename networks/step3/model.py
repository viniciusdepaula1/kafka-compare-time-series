from turtle import Turtle
from typing import List
from marshmallow import Schema, fields

class TimeSeries():
    def __init__(self, user_code: str, time_series: List[List[float]], work_order: List[List[float]], converter_alg: int, comparator_alg: int) -> None:
        self.user_code = user_code
        self.time_series = time_series
        self.work_order = work_order
        self.converter_alg = converter_alg
        self.comparator_alg = comparator_alg

class TimeSeriesSchema(Schema):
    user_code = fields.Str(required=True)
    converter_alg = fields.Int(required=True)
    comparator_alg = fields.Int(required=True)
    time_series = fields.List(fields.List(fields.Float, required=True), required=True)
    work_order = fields.List(fields.List(fields.Float, required=True), required=True)
    len_time_series = fields.Int(required=True)
    position = fields.Int(required=True) 

class monitorSchema(Schema):
    line = fields.Int(required=True)
    column = fields.Int(required=True)
    value = fields.Float(required=True)

class send_receive_network_Schema(Schema):
    time_series_number = fields.Int(required=True)
    network = fields.List(fields.List(fields.Int(required=True), required=True))

class networkSchema(Schema):
    user_code = fields.Str(required=True)
    comparator_alg = fields.Int(required=True)
    work_order = fields.List(fields.List(fields.Float, required=True), required=True)
    results = fields.List(fields.Nested(send_receive_network_Schema))
