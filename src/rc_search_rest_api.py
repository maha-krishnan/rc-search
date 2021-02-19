import click
import logging, os, yaml
import pkg_resources
import time

@click.group()
def web():
    """Group all commands here"""
    pass

@click.command()
def version():
    """Displays the current build version"""
    version = pkg_resources.require("devan")[0].version
    click.echo(version)

@click.command()
@click.option('--port', type=int, default=5629, help="Port to run the application")
def start_server(port):
    """Starts the web server"""    
    
    import socket
    import datetime
    import os
    import logging

    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine.base.Engine').setLevel(logging.ERROR)

    from waitress import serve
    from configs.flask_config import APP
    serve(APP, listen='*:{0}'.format(port))
    
web.add_command(version)
web.add_command(start_server)
