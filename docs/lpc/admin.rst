Administration
==============

Configuration Management
------------------------

I use `Ansible <https://www.ansible.com/>`_ as a configuration management system, tracked using version control and available at this `internal LIPS repository <https://github.com/PrincetonLIPS/lpc_admin/tree/master>`_. Traditionally one would only use a configuration management system when administrating a fairly large number of hosts (say 16 or 32 minimum). In this case, my primary motivation to utilize configuration management is automating documentation and administrative policies. The beauty of a configuration management system is it formalizes administration policies as code, which a new administrator can then simply read to understand how I’ve been administrating the hosts. 

Of course, ad-hoc and one-time administration tasks come up all the time, but for most of the major system components I’ve implemented idempotent Ansible playbooks to automate and codify (literally) my administration policies: 

- Installation of administration and core development tools
- Automated backups and filesystem management
- Container engine configuration and setup
- OpenLDAP client configuration
- NFS server and client configuration
- Nvidia GPU driver, runtime, and tooling software
- System service management

In this way a new administrator has an on-ramp to managing these systems even if they’re not familiar with them at the outset. Eventually something goes wrong, and in that case you need to understand the layers below this (the actual systems above), but these playbooks communicate precisely what I consider to be a “satisfactory” administrative state of the hosts. 

I maintain our configuration management under version control within our GitHub organization, see `that repository <https://github.com/PrincetonLIPS/lpc_admin>`_ for additional information. 

