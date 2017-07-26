# SupExt
SupExt is a supervision system designed to be run outside your infrastructure, and does test "as if" it is a external client. the system is modular so you can write your own tests to fulfill your needs.

## Configuration
The whole system is configured using a simple yaml file in /etc/supext/config.yml. there's an example configuration file in example.yml and an example mail template in mail.tpl

## Modules
Right now, SupExt is capable of sending alert emails if a test fails two times in a row, sending logs in Elasticsearch and updating the status of CachetHQ components. it is planned that modules can be set dynamically too
