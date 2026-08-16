"""Vercel serverless entrypoint for the Kenzory Flask app.

Vercel's @vercel/python runtime imports the WSGI callable named ``app`` from
this module and serves every request through it. ``application`` is exposed
as an alias for runtimes that look for the more conventional name.
"""

from app import app as application

app = application
