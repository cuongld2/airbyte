#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import datetime
import random
# from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_google_analytics_data_api.source import GoogleAnalyticsDataApiGenericStream

json_credentials = '''
\"type\": \"service_account\",
\"project_id\": \"unittest-project-id\",
\"private_key_id\": \"9qf98e52oda52g5ne23al6evnf13649c2u077162c\",
\"private_key\": \"-----BEGIN PRIVATE KEY-----\\nONE\\nTWO\\nTREE\\nFOUR\\nFIVE\\nSIX...\\n-----END PRIVATE KEY-----\\n\",
\"client_email\": \"google-analytics-access@unittest-project-id.iam.gserviceaccount.com\",
\"client_id\": \"213243192021686092537\",
\"auth_uri\": \"https://accounts.google.com/o/oauth2/auth\",
\"token_uri\": \"https://oauth2.googleapis.com/token\",
\"auth_provider_x509_cert_url\": \"https://www.googleapis.com/oauth2/v1/certs\",
\"client_x509_cert_url\": \"https://www.googleapis.com/robot/v1/metadata/x509/google-analytics-access%40unittest-project-id.iam.gserviceaccount.com\" }",
'''


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(GoogleAnalyticsDataApiGenericStream, "path", f"{random.randint(100000000, 999999999)}:runReport")
    mocker.patch.object(GoogleAnalyticsDataApiGenericStream, "primary_key", "test_primary_key")
    mocker.patch.object(GoogleAnalyticsDataApiGenericStream, "__abstractmethods__", set())

    return {
        "config": {
            "property_id": "unittest-project-id",
            "json_credentials": json_credentials,
            "dimensions": [],
            "metrics": [],
            "date_ranges_start_date": datetime.datetime.strftime((datetime.datetime.now() - datetime.timedelta(days=1)), "%Y-%m-%d"),
        }
    }


# def test_request_params(patch_base_class):
#     assert GoogleAnalyticsDataApiGenericStream(config=patch_base_class["config"]).request_params(
#         stream_state=MagicMock(),
#         stream_slice=MagicMock(),
#         next_page_token=MagicMock()
#     ) == {"base": "USD", "symbols": ["USD", "EUR"]}


def test_next_page_token_equal_chunk(patch_base_class):
    stream = GoogleAnalyticsDataApiGenericStream(config=patch_base_class["config"])
    response = MagicMock()
    response.json.side_effect = [
        {
            "limit": 100000,
            "offset": 0,
            "rowCount": 200000
        },
        {
            "limit": 100000,
            "offset": 100000,
            "rowCount": 200000
        },
        {
            "limit": 100000,
            "offset": 200000,
            "rowCount": 200000
        }
    ]
    inputs = {"response": response}

    expected_tokens = [
        {
            "limit": 100000,
            "offset": 100000,
        },
        {
            "limit": 100000,
            "offset": 200000,
        },
        None
    ]

    for expected_token in expected_tokens:
        assert stream.next_page_token(**inputs) == expected_token


def test_next_page_token(patch_base_class):
    stream = GoogleAnalyticsDataApiGenericStream(config=patch_base_class["config"])
    response = MagicMock()
    response.json.side_effect = [
        {
            "limit": 100000,
            "offset": 0,
            "rowCount": 250000
        },
        {
            "limit": 100000,
            "offset": 100000,
            "rowCount": 250000
        },
        {
            "limit": 100000,
            "offset": 200000,
            "rowCount": 250000
        },
        {
            "limit": 100000,
            "offset": 300000,
            "rowCount": 250000
        }
    ]
    inputs = {"response": response}

    expected_tokens = [
        {
            "limit": 100000,
            "offset": 100000,
        },
        {
            "limit": 100000,
            "offset": 200000,
        },
        {
            "limit": 100000,
            "offset": 300000,
        },
        None
    ]

    for expected_token in expected_tokens:
        assert stream.next_page_token(**inputs) == expected_token



# def test_parse_response(patch_base_class):
#     stream = ExchangeRateApiStream(config=patch_base_class["config"])
#     response = MagicMock()
#     response.json.return_value = {"record": "expected record"}
#     inputs = {"response": response}
#     expected_parsed_object = {"record": "expected record"}
#     assert next(iter(stream.parse_response(**inputs))) == expected_parsed_object
#
#
# def test_request_headers(patch_base_class):
#     stream = ExchangeRateApiStream(config=patch_base_class["config"])
#     inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
#     expected_headers = {}
#     assert stream.request_headers(**inputs) == expected_headers
#
#
# def test_http_method(patch_base_class):
#     stream = ExchangeRateApiStream(config=patch_base_class["config"])
#     expected_method = "GET"
#     assert stream.http_method == expected_method
#
#
# @pytest.mark.parametrize(
#     ("http_status", "should_retry"),
#     [
#         (HTTPStatus.OK, False),
#         (HTTPStatus.BAD_REQUEST, False),
#         (HTTPStatus.TOO_MANY_REQUESTS, True),
#         (HTTPStatus.INTERNAL_SERVER_ERROR, True),
#     ],
# )
# def test_should_retry(patch_base_class, http_status, should_retry):
#     response_mock = MagicMock()
#     response_mock.status_code = http_status
#     stream = ExchangeRateApiStream(config=patch_base_class["config"])
#     assert stream.should_retry(response_mock) == should_retry
#
#
# def test_backoff_time(patch_base_class):
#     response_mock = MagicMock()
#     stream = ExchangeRateApiStream(config=patch_base_class["config"])
#     expected_backoff_time = None
#     assert stream.backoff_time(response_mock) == expected_backoff_time
