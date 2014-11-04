from setuptools import setup
import sys

#v = sys.version_info
#if v[0] == 2 and v[1] == 7:
setup(name='nuodbawsquickstart',
      version='0.1.0',
      description='Script to deploy a multi-region and multi-instance AWS cluster',
      url='http://github.com/nuodb/nuodb-aws-quickstart',
      author='NuoDB Inc.',
      author_email='info@nuodb.com',
      data_files=[('nuodbawsquickstart/templates', ['nuodbawsquickstart/templates/init.py'])],
      install_requires=["boto", "requests"], 
      license='BSD licence, see LICENSE',
      packages=['nuodbawsquickstart'],
      scripts=["nuodb_aws_quickstart.py"],
      zip_safe=False)
#else:
#  print "This module and some of its dependencies only work on Python version 2.7. Detected %s. Cannot continue." % ".".join(str(e) for e in v[0:2])
#  exit(2)
