# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from setuptools import setup

classifiers = ['Operating System :: POSIX :: Linux',
               'License :: OSI Approved :: MIT License',
               'Intended Audience :: Developers',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3',
               'Topic :: Software Development',
               'Topic :: System :: Hardware']

setup(name                          = 'Jetson.GPIO',
      version                       = '2.0.15',
      author                        = 'NVIDIA',
      author_email                  = 'linux-tegra-bugs@nvidia.com',
      description                   = 'A module to control Jetson GPIO channels',
      long_description              = open('README.md').read(),
      long_description_content_type = 'text/markdown',
      license                       = 'MIT',
      keywords                      = 'Jetson GPIO',
      url                           = 'https://github.com/NVIDIA/jetson-gpio',
      classifiers                   = classifiers,
      package_dir                   = {'': 'lib/python/'},
      packages                      = ['Jetson', 'Jetson.GPIO', 'RPi', 'RPi.GPIO'],
      package_data                  = {'Jetson.GPIO': ['99-gpio.rules',]},
      include_package_data          = True,
)
