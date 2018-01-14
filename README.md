# SupExt

SupExt is an external monitoring system designed to run tests from outside your infrastructure "as if" it is a client. the system is also modular so you can write your own modules if needed.

## Configuration
SupExt is configured using a yaml file at /etc/supext/config.yml. there's an example config file in conf, also, there's an example mail template for the mail module.

## Modules
Supext is designed with 3 kinds of modules: tests, alerts and logging.
* Tests are the modules that execute the different checks defined in your config file
* Logging are the modules that log the results, for example in ElasticSearch or in CachetHQ
* Alerts are the modules that are trigged if a check fails 2 times in a row, for example to send an email

## Current list of modules
Here is a current list of modules, along with some important information about them

### Test modules

* cert_fingerprint: get a csv of certificates and check the certificate fingerprint from URL against a known fingerprint
* crl: read a csv that contains a list of CRLs and check if they aren't out of date
* dns: tries to resolv a dns (optionally check if it resolves to a known IP)
* http: tries to get a HTTP page, and check if it did successfuly (have a 200 return code)
* mail: send a mail using SMTP then check if it got an answer (or the same email) using IMAP
* ocsp: send an OCSP request and check the answer
* packets: does a ping and check the packet loss
* shell: a generic shell script runner, runs a bash script and check the exit code
* ssh: tries to connect using SSH (with a pasword or a certificate), this module requires paramiko to be installed
* ssl: get a SSL certificate and check it's expiration date
* tcp: tries to connect to a specific TCP host and port
* traceroute: does a traceroute to a given host
* tsa: does a RFC3161 (timestamping) request and check the token

### Alerting modules:

* mail: send an email to a group specified in each check (or defaults to 'default'), you can specify multiple groups per check.

### Connector modules:

* elasticsearch: send each check result to an elasticsearch cluster, it requires the elasticsearch python module
* cachet: send each check result to a cachetHQ server
