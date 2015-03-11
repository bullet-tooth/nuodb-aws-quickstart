from setuptools import setup
import sys

setup(name='nuodbawsquickstart',
      version='1.0.1',
      description='Script to deploy a multi-region and multi-instance AWS cluster',
      url='http://github.com/nuodb/nuodb-aws-quickstart',
      author='NuoDB Inc.',
      author_email='info@nuodb.com',
      data_files=[('nuodbawsquickstart/templates', ['nuodbawsquickstart/templates/init.py'])],
      install_requires=["argparse", "boto", "requests"], 
      license='BSD licence, see LICENSE',
      packages=['nuodbawsquickstart'],
      scripts=["nuodb_aws_quickstart.py"],
      zip_safe=False)