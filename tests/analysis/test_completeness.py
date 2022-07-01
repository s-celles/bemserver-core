"""Completeness tests"""
import datetime as dt

import pandas as pd

import pytest
from tests.utils import create_timeseries_data

from bemserver_core.model import (
    TimeseriesDataState,
    TimeseriesProperty,
    TimeseriesPropertyData,
)
from bemserver_core.authorization import CurrentUser, OpenBar

from bemserver_core.process.completeness import compute_completeness


class TestCompleteness:
    @pytest.mark.parametrize("timeseries", (5,), indirect=True)
    def test_completeness(self, users, timeseries):
        admin_user = users[0]
        assert admin_user.is_admin
        # 10 min, full
        ts_0 = timeseries[0]
        # 10 min, gaps
        ts_1 = timeseries[1]
        # 20 min, ratio > 1
        ts_2 = timeseries[2]
        # None, variable int
        ts_3 = timeseries[3]
        # None, no data
        ts_4 = timeseries[4]

        with OpenBar():
            ds_1 = TimeseriesDataState.get(name="Raw").first()
            interval_prop = TimeseriesProperty.get(name="Interval").first()
            TimeseriesPropertyData.new(
                timeseries_id=ts_0.id,
                property_id=interval_prop.id,
                value=600,
            )
            TimeseriesPropertyData.new(
                timeseries_id=ts_1.id,
                property_id=interval_prop.id,
                value=600,
            )
            TimeseriesPropertyData.new(
                timeseries_id=ts_2.id,
                property_id=interval_prop.id,
                value=1200,
            )

        start_dt = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)
        start_dt_plus_1_day = dt.datetime(2020, 1, 2, tzinfo=dt.timezone.utc)
        intermediate_dt_1 = dt.datetime(2020, 1, 25, 10, 3, tzinfo=dt.timezone.utc)
        intermediate_dt_2 = dt.datetime(2020, 2, 1, tzinfo=dt.timezone.utc)
        end_dt = dt.datetime(2020, 3, 1, tzinfo=dt.timezone.utc)

        timestamps_1 = pd.date_range(start_dt, end_dt, inclusive="left", freq="600S")
        values_1 = range(len(timestamps_1))
        create_timeseries_data(ts_0, ds_1, timestamps_1, values_1)

        timestamps_2 = pd.date_range(
            start_dt, intermediate_dt_1, inclusive="left", freq="600S"
        ).union(pd.date_range(intermediate_dt_2, end_dt, inclusive="left", freq="600S"))
        values_2 = range(len(timestamps_2))
        create_timeseries_data(ts_1, ds_1, timestamps_2, values_2)

        # 430 is a manually randomized number chosen to get uneven buckets
        timestamps_3 = pd.date_range(start_dt, end_dt, inclusive="left", freq="430S")
        values_3 = range(len(timestamps_3))
        create_timeseries_data(ts_2, ds_1, timestamps_3, values_3)

        timestamps_4 = pd.date_range(
            start_dt, intermediate_dt_1, inclusive="left", freq="600S"
        ).union(pd.date_range(intermediate_dt_2, end_dt, inclusive="left", freq="430S"))
        values_4 = range(len(timestamps_4))
        create_timeseries_data(ts_3, ds_1, timestamps_4, values_4)

        with CurrentUser(admin_user):

            ts_l = (ts_0, ts_1, ts_2, ts_3, ts_4)

            # 2 months - monthly
            ret = compute_completeness(start_dt, end_dt, ts_l, ds_1, "1 month")
            assert ret == {
                "timestamps": [
                    dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
                    dt.datetime(2020, 2, 1, tzinfo=dt.timezone.utc),
                ],
                "timeseries": {
                    "Timeseries 0": {
                        "avg count": 4320.0,
                        "avg ratio": 1.0,
                        "count": [4464, 4176],
                        "expected count": [4464.0, 4176.0],
                        "interval": 600.0,
                        "ratio": [1.0, 1.0],
                        "total count": 8640,
                        "undefined interval": False,
                    },
                    "Timeseries 1": {
                        "avg count": 3846.5,
                        "avg ratio": 0.8939292114695341,
                        "count": [3517, 4176],
                        "expected count": [4464.0, 4176.0],
                        "interval": 600.0,
                        "ratio": [0.7878584229390682, 1.0],
                        "total count": 7693,
                        "undefined interval": False,
                    },
                    "Timeseries 2": {
                        "avg count": 6028.0,
                        "avg ratio": 2.790739710789766,
                        "count": [6229, 5827],
                        "expected count": [2232.0, 2088.0],
                        "interval": 1200.0,
                        "ratio": [2.7907706093189963, 2.790708812260536],
                        "total count": 12056,
                        "undefined interval": False,
                    },
                    "Timeseries 3": {
                        "avg count": 4672.0,
                        "avg ratio": 0.782314808151154,
                        "count": [3517, 5827],
                        "expected count": [6228.862068965516, 5826.999999999999],
                        "interval": 429.9982838510383,
                        "ratio": [0.564629616302308, 1.0],
                        "total count": 9344,
                        "undefined interval": True,
                    },
                    "Timeseries 4": {
                        "avg count": 0.0,
                        "avg ratio": None,
                        "count": [0, 0],
                        "expected count": [None, None],
                        "interval": None,
                        "ratio": [None, None],
                        "total count": 0,
                        "undefined interval": True,
                    },
                },
            }

            # 2 months - daily
            ret = compute_completeness(start_dt, end_dt, ts_l, ds_1, "1 day")
            assert ret["timestamps"][0] == dt.datetime(
                2020, 1, 1, tzinfo=dt.timezone.utc
            )
            assert ret["timestamps"][-1] == dt.datetime(
                2020, 2, 29, tzinfo=dt.timezone.utc
            )
            assert ret["timeseries"]["Timeseries 0"]["avg count"] == 144.0
            assert ret["timeseries"]["Timeseries 0"]["total count"] == 8640
            assert ret["timeseries"]["Timeseries 0"]["avg ratio"] == 1.0
            assert ret["timeseries"]["Timeseries 0"]["interval"] == 600.0
            assert ret["timeseries"]["Timeseries 0"]["undefined interval"] is False
            assert ret["timeseries"]["Timeseries 0"]["expected count"] == 60 * [144.0]
            assert ret["timeseries"]["Timeseries 1"]["avg count"] == 128.21666666666667
            assert ret["timeseries"]["Timeseries 1"]["total count"] == 7693
            assert ret["timeseries"]["Timeseries 1"]["avg ratio"] == 0.8903935185185186
            assert ret["timeseries"]["Timeseries 1"]["interval"] == 600.0
            assert ret["timeseries"]["Timeseries 1"]["undefined interval"] is False
            assert ret["timeseries"]["Timeseries 1"]["expected count"] == 60 * [144.0]
            assert ret["timeseries"]["Timeseries 2"]["avg count"] == 200.93333333333334
            assert ret["timeseries"]["Timeseries 2"]["total count"] == 12056
            assert ret["timeseries"]["Timeseries 2"]["avg ratio"] == 2.79074074074074
            assert ret["timeseries"]["Timeseries 2"]["interval"] == 1200.0
            assert ret["timeseries"]["Timeseries 2"]["undefined interval"] is False
            assert ret["timeseries"]["Timeseries 2"]["expected count"] == 60 * [72.0]
            assert ret["timeseries"]["Timeseries 3"]["avg count"] == 155.73333333333332
            assert ret["timeseries"]["Timeseries 3"]["total count"] == 9344
            assert ret["timeseries"]["Timeseries 3"]["avg ratio"] == 0.7747927031509121
            assert ret["timeseries"]["Timeseries 3"]["interval"] == 429.85074626865674
            assert ret["timeseries"]["Timeseries 3"]["undefined interval"] is True
            assert ret["timeseries"]["Timeseries 3"]["expected count"] == 60 * [201.0]
            assert ret["timeseries"]["Timeseries 4"]["avg count"] == 0.0
            assert ret["timeseries"]["Timeseries 4"]["total count"] == 0
            assert ret["timeseries"]["Timeseries 4"]["avg ratio"] is None
            assert ret["timeseries"]["Timeseries 4"]["interval"] is None
            assert ret["timeseries"]["Timeseries 4"]["undefined interval"] is True
            assert ret["timeseries"]["Timeseries 4"]["expected count"] == 60 * [None]

            # 2 months - weekly
            ret = compute_completeness(start_dt, end_dt, ts_l, ds_1, "1 week")
            assert ret["timestamps"][0] == dt.datetime(
                2019, 12, 30, tzinfo=dt.timezone.utc
            )
            assert ret["timestamps"][-1] == dt.datetime(
                2020, 2, 24, tzinfo=dt.timezone.utc
            )
            assert ret["timeseries"]["Timeseries 0"]["count"] == [
                720,
                1008,
                1008,
                1008,
                1008,
                1008,
                1008,
                1008,
                864,
            ]
            assert ret["timeseries"]["Timeseries 0"]["avg ratio"] == 1.0
            assert ret["timeseries"]["Timeseries 2"]["count"] == [
                1005,
                1407,
                1406,
                1407,
                1406,
                1407,
                1406,
                1407,
                1205,
            ]
            assert ret["timeseries"]["Timeseries 3"]["count"] == [
                720,
                1008,
                1008,
                781,
                402,
                1407,
                1406,
                1407,
                1205,
            ]

            # 1 day - minute step
            ret = compute_completeness(
                start_dt, start_dt_plus_1_day, ts_l, ds_1, "1 minute"
            )
            assert ret["timestamps"][0] == dt.datetime(
                2020, 1, 1, tzinfo=dt.timezone.utc
            )
            assert ret["timestamps"][-1] == dt.datetime(
                2020, 1, 1, 23, 59, tzinfo=dt.timezone.utc
            )
            assert ret["timeseries"]["Timeseries 0"]["avg count"] == 0.1
            assert ret["timeseries"]["Timeseries 0"]["total count"] == 6 * 24
            assert ret["timeseries"]["Timeseries 0"]["avg ratio"] == 1.0
            assert ret["timeseries"]["Timeseries 0"]["interval"] == 600.0
            assert ret["timeseries"]["Timeseries 0"]["undefined interval"] is False
            assert ret["timeseries"]["Timeseries 0"]["expected count"] == 60 * 24 * [
                0.1
            ]
            assert ret["timeseries"]["Timeseries 2"]["avg count"] == 0.13958333333333334
            assert ret["timeseries"]["Timeseries 2"]["total count"] == 201
            assert ret["timeseries"]["Timeseries 2"]["avg ratio"] == 2.7916666666666665
            assert ret["timeseries"]["Timeseries 2"]["interval"] == 1200.0
            assert ret["timeseries"]["Timeseries 2"]["undefined interval"] is False
            assert ret["timeseries"]["Timeseries 2"]["expected count"] == 24 * 60 * [
                0.05
            ]
            assert ret["timeseries"]["Timeseries 4"]["avg count"] == 0.0
            assert ret["timeseries"]["Timeseries 4"]["total count"] == 0
            assert ret["timeseries"]["Timeseries 4"]["avg ratio"] is None
            assert ret["timeseries"]["Timeseries 4"]["interval"] is None
            assert ret["timeseries"]["Timeseries 4"]["undefined interval"] is True
            assert ret["timeseries"]["Timeseries 4"]["expected count"] == 24 * 60 * [
                None
            ]