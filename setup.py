#!/usr/bin/env python
#coding:utf-8

import os
from setuptools import setup, find_packages
from setuptools.command.install import install
import warnings

'''
    打包fvs的代码
'''

# class install_data_files(install):
#     # user_options = install.user_options + [
#     #     # ('fix=', None, 'whether to install fx'),
#     #     # ('service', None, 'whether to install as service')
#     # ]
#     @staticmethod
#     def files():
#         return [
#             ("/etc/sysconfig/fvs/env", ["config/env/fvs"]),
#             ("/usr/bin", ["bin/fvsctl"])
#         ]

#     # def initialize_options(self):
#     #     """初始化参数"""
#     #     install.initialize_options(self)
#     #     self.fix = None
#     #     self.service = None

#     # def finalize_options(self):
#     #     install.finalize_options(self)

#     def run(self):
#         """
#         移动特殊文件，防止安装wheel的时候，只能安装在site-package目录
#         """
#         # service = self.service #Will be 1 or None

#         #先安装其他
#         install.run(self)

#         try:
#             from pkg_resources import Requirement, resource_filename
#             import os
#             import shutil
#             for p,f in self.files():
#                 if not p.startswith('/'):
#                     continue

#                 resource_filename(Requirement.parse())
#             pass
#         except:
#             warnings.warn("WARNING: An isssue occured while installing the special files")

if os.path.exists("README.md"):
    with open("README.md", "r", encoding = 'utf-8') as fh:
        long_description = fh.read()
else:
    long_description = ""

install_requires = []
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'requirements.txt'), mode='r', encoding='utf-8') as f:
    install_requires.extend([ l.strip() for l in f.readlines() ])

setup(
    name = "fvs",
    version = "1.0.0",
    keywords = ["file server", "http.server"],
    description = "轻量级的文件服务",
    long_description = long_description,
    author = "xmyeen",
    author_email = "xmyeen@sina.com.cn",
    url = "https://github.com/xmyeen/fvs",

    packages = find_packages(),
    # package_dir = {"fvs": "fvs"},
    # package_data = {
    #     'bin' :  [ 'bin/*' ],
    #     'config': ['config/*.cfg' ]
    # },
    # include_package_data = True,

    data_files = [
        ( 'config', [ 'config/app.cfg' ] )
    ],

    entry_points = {
        'console_scripts': [
            'fvs = fvs.__main__:main'
        ]
    },

    scripts = [ 'bin/fvsctl' ],

    license = 'MIT',
    platforms = 'Posix',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Internet',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8'
    ],

    python_requires='>=3',

    install_requires = install_requires

    # cmdclass = { 'install': install_data_files }
)

