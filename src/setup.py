from setuptools import setup, find_packages

setup(
    name="rc_search",
    version="0.0.1",
    description="RC Search",
    entry_points='''
    [console_scripts]
    rc_search=rc_search_rest_api:web
    ''',
    py_modules=['api', 'lib'],
    scripts=["rc_search_rest_api.py"]
)