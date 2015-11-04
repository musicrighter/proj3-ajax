#! /usr/bin/env python3

""" For deployment on ix under CGI """

import site
site.addsitedir("/home/users/djg/public_html/proj3-ajax/env/lib/python3.4/site-packages")

from wsgiref.handlers import CGIHandler
from app import app

CGIHandler().run(app)
