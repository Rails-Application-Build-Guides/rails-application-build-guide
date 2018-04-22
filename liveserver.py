#!/usr/bin/env python

from livereload import Server, shell

server = Server()
server.watch('src/**/*.rst', shell('make html'))
server.serve(open_url=False)
