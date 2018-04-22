#!/usr/bin/env python

import os

os.system('make html')

from livereload import Server, shell

server = Server()
server.watch('source/**/*.rst', shell('make html'))
server.watch('source/**/*.md', shell('make html'))
server.serve(
        open_url=False,
        root='build/html',
        port=8080,
        host='0.0.0.0'
        )
