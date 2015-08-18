ServiceNow tickets from Zabbix
==============================

Python script for custom Zabbix script media. Script uses ServiceNow API.

[![Paypal donate button](http://jangaraj.com/img/github-donate-button02.png)]
(https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=8LB6J222WRUZ4)

Installation
============

Copy the `zabbix-create-service-now-incident.py` script into the `AlertScriptsPath` 
directory which is by default `/usr/lib/zabbix/alertscripts` and make it executable:

    $ cd /usr/lib/zabbix/alertscripts
    $ wget https://raw.github.com/monitoringartist/zabbix-script-servicenow/master/zabbix-create-service-now-incident.py 
    $ chmod 755 zabbix-create-service-now-incident.py

Configuration
=============

To forward Zabbix events to ServiceNow a new media script needs to be created 
and associated with a user. Follow the steps below as a Zabbix Admin user:

1.) Create a new media type [Admininstration > Media Types > Create Media Type]
```
Name: ServiceNow API
Type: Script
Script name: zabbix-create-service-now-incident.py
```

2.) Modify the Media for the Admin user [Administration > Users]
```
Type: ServiceNow API
Send to: string               <--- this string is not used
When active: 1-7,00:00-24:00
Use if severity: (all)
Status: Enabled
```

3.) Configure Action [Configuration > Actions > Create Action > Action]
Event source: Triggers
```
Name: Create ServiceNow ticket
Default Subject: {TRIGGER.STATUS}

Default Message:
Trigger: {TRIGGER.NAME}
Trigger description: {TRIGGER.DESCRIPTION} 
Trigger severity: {TRIGGER.SEVERITY}
Trigger nseverity: {TRIGGER.NSEVERITY}
Trigger status: {TRIGGER.STATUS}
Trigger URL: {TRIGGER.URL}
Host: {HOST.HOST}
Host description: {HOST.DESCRIPTION}
Event age: {EVENT.AGE}
Current Zabbix time: {DATE} {TIME} 

Item values:

1. {ITEM.NAME1} ({HOST.NAME1}:{ITEM.KEY1}): {ITEM.VALUE1}
2. {ITEM.NAME2} ({HOST.NAME2}:{ITEM.KEY2}): {ITEM.VALUE2}
3. {ITEM.NAME3} ({HOST.NAME3}:{ITEM.KEY3}): {ITEM.VALUE3}

Zabbix event ID: {EVENT.ID}
Zabbix web UI: https://zabbix.domain.com/zabbix
```

For a full list of trigger macros see https://www.zabbix.com/documentation/2.4/manual/appendix/macros/supported_by_location

At the Conditions tab, to only forward PROBLEM events:

```
(A)	Maintenance status not in "maintenance" 
(B)	Trigger value = "PROBLEM" 
```

Finally, add an operation:
```
Send to Users: Admin
Send only to: ServiceNow API
```

Troubleshooting
===============

Set debug to 1 in the script for debug output:
``` 
debug = 1
```
And test script in commandline manually. It is very likely, that your ServiceNow 
instance has different settings (mandatory fields, lists, ...). You should to see 
in server response, what is a problem.

Author
======

[Devops Monitoring zExpert](http://www.jangaraj.com), who loves monitoring 
systems, which start with letter Z. Those are Zabbix and Zenoss.

Professional monitoring services:

[![Monitoring Artist](http://monitoringartist.com/img/github-monitoring-artist-logo.jpg)]
(http://www.monitoringartist.com)
