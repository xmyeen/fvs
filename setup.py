#!/usr/bin/env python
#coding:utf-8

import os
from setuptools import setup, find_packages

'''
    打包fvs的代码
'''

if os.path.exists("README.md"):
    with open("README.md", "r", encoding = 'utf-8') as fh:
        long_description = fh.read()
else:
    long_description = ""

setup(
    name = "fvs",
    version = "1.0.0",
    description = "轻量级的文件服务",
    author = "chenyuzhi",
    author_email = "chenyuzhi@hikvision.com.cn",

    packages = find_packages('fvs'),

    data_files = [
        ("/etc/sysconfig/fvs", ['cfg'])
    ],

    entry_points = {
        'console_scripts': [
            'fvs = fvs.app:setup'
        ]
    },

    license = 'MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3'
    ],

    python_requires='>=3',

    install_requires = [
        "numpy",
        "qrcode",
        "pillow"
    ]
)