from mitmproxy.test import tflow
import re

import mitmproxy.test.tutils
from mitmproxy.net.http import Headers
from mitmproxy import export  # heh
from . import tutils


def clean_blanks(s):
    return re.sub(r"^(\s+)$", "", s, flags=re.MULTILINE)


def python_equals(testdata, text):
    """
        Compare two bits of Python code, disregarding non-significant differences
        like whitespace on blank lines and trailing space.
    """
    d = open(tutils.test_data.path(testdata)).read()
    assert clean_blanks(text).rstrip() == clean_blanks(d).rstrip()


def req_get():
    return mitmproxy.test.tutils.treq(method=b'GET', content=b'', path=b"/path?a=foo&a=bar&b=baz")


def req_post():
    return mitmproxy.test.tutils.treq(method=b'POST', headers=())


def req_patch():
    return mitmproxy.test.tutils.treq(method=b'PATCH', path=b"/path?query=param")


class TestExportCurlCommand:
    def test_get(self):
        flow = tflow.tflow(req=req_get())
        result = """curl -H 'header:qvalue' -H 'content-length:7' 'http://address:22/path?a=foo&a=bar&b=baz'"""
        assert export.curl_command(flow) == result

    def test_post(self):
        flow = tflow.tflow(req=req_post())
        result = """curl -X POST 'http://address:22/path' --data-binary 'content'"""
        assert export.curl_command(flow) == result

    def test_patch(self):
        flow = tflow.tflow(req=req_patch())
        result = """curl -H 'header:qvalue' -H 'content-length:7' -X PATCH 'http://address:22/path?query=param' --data-binary 'content'"""
        assert export.curl_command(flow) == result


class TestExportPythonCode:
    def test_get(self):
        flow = tflow.tflow(req=req_get())
        python_equals("data/test_flow_export/python_get.py", export.python_code(flow))

    def test_post(self):
        flow = tflow.tflow(req=req_post())
        python_equals("data/test_flow_export/python_post.py", export.python_code(flow))

    def test_post_json(self):
        p = req_post()
        p.content = b'{"name": "example", "email": "example@example.com"}'
        p.headers = Headers(content_type="application/json")
        flow = tflow.tflow(req=p)
        python_equals("data/test_flow_export/python_post_json.py", export.python_code(flow))

    def test_patch(self):
        flow = tflow.tflow(req=req_patch())
        python_equals("data/test_flow_export/python_patch.py", export.python_code(flow))


class TestExportLocustCode:
    def test_get(self):
        flow = tflow.tflow(req=req_get())
        python_equals("data/test_flow_export/locust_get.py", export.locust_code(flow))

    def test_post(self):
        p = req_post()
        p.content = b'content'
        p.headers = ''
        flow = tflow.tflow(req=p)
        python_equals("data/test_flow_export/locust_post.py", export.locust_code(flow))

    def test_patch(self):
        flow = tflow.tflow(req=req_patch())
        python_equals("data/test_flow_export/locust_patch.py", export.locust_code(flow))


class TestExportLocustTask:
    def test_get(self):
        flow = tflow.tflow(req=req_get())
        python_equals("data/test_flow_export/locust_task_get.py", export.locust_task(flow))

    def test_post(self):
        flow = tflow.tflow(req=req_post())
        python_equals("data/test_flow_export/locust_task_post.py", export.locust_task(flow))

    def test_patch(self):
        flow = tflow.tflow(req=req_patch())
        python_equals("data/test_flow_export/locust_task_patch.py", export.locust_task(flow))


class TestURL:
    def test_url(self):
        flow = tflow.tflow()
        assert export.url(flow) == "http://address:22/path"
