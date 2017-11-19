from distutils.core import setup

setup(
    name         = "SupExt",
    version      = "0.1.5",
    packages     = ['supext', 'supext.modules.tests', 'supext.modules.alerting', 'supext.modules.connectors'],
    description  = "External and modular monitoring tool",
    author       = "Lex Persona",
    author_email = "contact@lex-persona.com",
    url          = "https://github.com/Lex-Persona/SupExt",
    keywords     = [
        "monitoring", "testing", "tests"
    ],
    classifiers  = [
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3"
    ],
    install_requires = [
        # TODO: list required dependencies
    ],
    data_files = [
        ('/etc/supext', ['conf/config.yml', 'conf/mail.tpl']),
        ('/usr/bin', ['bin/supext'])
    ],
    long_description = """\
External and modular monitoring tool,
designed to test parts of your infra 'as if' it is an external client.
The system is also modular so you can write your own tests if needed.
There's also alerting capabilities and connectors for CachetHQ and ElasticSearch.
"""
)
