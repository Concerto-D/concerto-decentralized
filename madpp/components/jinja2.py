import os

from jinja2 import Template

from madpp.component import Component
from madpp.dependency import DepType


def print_html_doc():
    # Create the jinja2 environment.
    # Notice the use of trim_blocks, which greatly helps control whitespace.
    print ()


class Jinja2(Component):
    
    def __init__(self, template_text, var_parameters_names, const_parameters_values={}):
        for p in var_parameters_names:
            if p is 'jinja2_result':
                raise Exception("Cannot have a parameter called 'jinja2_result' (used internally)")
        
        self.template = Template(template_text)
        self.var_parameters_names = var_parameters_names
        self.const_parameters_values = const_parameters_values
        Component.__init__(self)

    def create(self):
        self.places = [
            'init',
            'providing'
        ]

        self.transitions = {
            'generate': ('init', 'providing', 'generate', 0, self.generate)
        }

        self.dependencies = {
            'jinja2_result': (DepType.DATA_PROVIDE, ['providing'])
        }
        
        for p in self.var_parameters_names:
            if p not in self.const_parameters_values:
                self.dependencies[p] = (DepType.DATA_USE, ['generate'])
        
        
        self.initial_place = 'init'
    
    def generate(self):
        parameters = {}
        for p in self.var_parameters_names:
            parameters[p] = self.read(p)
        for p in self.const_parameters_values:
            parameters[p] = self.const_parameters_values[p]
        self.write('jinja2_result',self.template.render(parameters))
