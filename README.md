# SupExt

SupExt is an external monitoring system designed to run tests from outside your infrastructure "as if" it is a client. the system is also modular so you can write your own modules if needed.

## Configuration
SupExt is configured using a yaml file at /etc/supext/config.yml. there's an example config file in conf, also, there's an example mail template for the mail module.

## Modules
Supext is designed with 3 kinds of modules: tests, alerts and logging.
* Tests are the modules that execute the different checks defined in your config file
* Logging are the modules that log the results, for example in ElasticSearch or in CachetHQ
* Alerts are the modules that are trigged if a check fails 2 times in a row, for example to send an email

