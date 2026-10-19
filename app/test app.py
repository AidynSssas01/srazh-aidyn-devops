"""Unit tests for app.py — executed in the Jenkins "Test" stage:
    python3 -m unittest discover -s app -p "test_*.py" -v
"""
import json
import os
import sys
import threading
import unittest
import urllib.request
from http.server import HTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app  # noqa: E402


class ConfigTests(unittest.TestCase):
    def test_config_file_values_are_loaded(self):
        config, sources = app.load_config(environ={})
        self.assertEqual(config["STUDENT_SURNAME"], "Srazh")
        self.assertEqual(config["STUDENT_NAME"], "Aidyn")
        self.assertEqual(config["STUDENT_GROUP"], "IT2-2308")
        self.assertEqual(sources["STUDENT_NAME"], "config file")

    def test_environment_overrides_config(self):
        config, sources = app.load_config(environ={"STUDENT_GROUP": "TEST-0000"})
        self.assertEqual(config["STUDENT_GROUP"], "TEST-0000")
        self.assertEqual(sources["STUDENT_GROUP"], "environment")


class BannerTests(unittest.TestCase):
    def test_banner_contains_student_information(self):
        config, _ = app.load_config(environ={})
        banner = app.build_banner(config)
        for text in ("DevOps Student Application", "Name:", "Surname:", "Group:",
                     "Student ID:", "Application is running successfully!"):
            self.assertIn(text, banner)


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config, _ = app.load_config(environ={})
        cls.server = HTTPServer(("127.0.0.1", 0), app.make_handler(config))   # port 0 = any free port
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def get(self, path):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}", timeout=5) as resp:
            return resp.status, resp.read().decode()

    def test_health_endpoint(self):
        status, body = self.get("/health")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["status"], "ok")

    def test_info_endpoint(self):
        status, body = self.get("/info")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["surname"], "Srazh")

    def test_index_page(self):
        status, body = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn("Application is running successfully!", body)


if __name__ == "__main__":
    unittest.main(verbosity=2)
