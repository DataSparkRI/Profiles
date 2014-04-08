from django.test.simple import DjangoTestSuiteRunner

class DataTestRunner(DjangoTestSuiteRunner):
    def setup_databases(self, **kwargs):
        print "--Using DataTestRunner, skippind db setup--"""

    def teardown_databases(self, old_config, **kwargs):
        print "--skipping db teardown---"""
