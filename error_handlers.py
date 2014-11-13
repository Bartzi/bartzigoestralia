# -*- coding: utf-8 -*-


import jinja2
import os


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


def handle_404(request, response, exception):
    template = JINJA_ENVIRONMENT.get_template('default_error.html')
    error_code = {"code": "404"}
    response.write(template.render(error_code))


def handle_500(request, response, exception):
    template = JINJA_ENVIRONMENT.get_template('default_error.html')
    error_code = {"code": "500"}
    response.write(template.render(error_code))
