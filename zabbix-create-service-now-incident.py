#!/usr/bin/python

## Create Service-Now incident from Zabbix
## Copyright (C) 2001-2015 Jan Garaj - www.jangaraj.com
## Doc: http://wiki.servicenow.com/index.php?title=Python_Web_Services_Client_Examples
## WSDL doc: https://<your_instance>.service-now.com/incident.do?WSDL
##

debug     = 0                 # 0/1 - enable/disable debug outputs
instance  = 'your_instance'   #
username  = 'login '          # Service-Now login
password  = 'password'        # base64 encrypted Service-Now password, don't use plaintext passwords
interface = 'incident.do'     #
agroup    = 'Group'           # Assignment group
category  = 'Category'        # Category of incident
scategory = 'Subcategory'     # Subcategory of incident

import sys
if len(sys.argv) < 3:
    print """
Incorrect usage of Create Service-Now incident from Zabbix script

Example:
   zabbix-create-service-now-incident.py <to> <subject> <message>
   zabbix-create-service-now-incident.py "Jan Garaj" "PROBLEM" "
Trigger: Zabbix Server is down
Trigger description: Zabbix Server is down, please check it immediately
Trigger severity: Hight
Trigger nseverity: 4
Trigger status: Problem
Trigger URL:
Host: zabserver01
Host description: Main Zabbix Server
Event age: 10s
Current Zabbix time: 2015.06.19 21:23:12

Item values:

1. {ITEM.NAME1} ({HOST.NAME1}:{ITEM.KEY1}): {ITEM.VALUE1}
2. {ITEM.NAME2} ({HOST.NAME2}:{ITEM.KEY2}): {ITEM.VALUE2}
3. {ITEM.NAME3} ({HOST.NAME3}:{ITEM.KEY3}): {ITEM.VALUE3}

Zabbix event ID: 12345
Zabbix web UI: https://zabbix.domain.com/zabbix
   "
    """
    sys.exit(1)

# command line arguments
# subject - {TRIGGER.STATUS} - PROBLEM or OK
subject = sys.argv[2]
# message - whatever message the Zabbix action sends, preferably something like "Zabbix server is unreachable for 5 minutes"
# recommended setting:
'''
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
'''
message = sys.argv[3]

# value mapping
zabbix2servicenow = {
    # parse from Zabbix message, remap value if map exists
    'dynamic': {
        'impact': '^Trigger nseverity: .*',
        'urgency': '^Trigger nseverity: .*',
        'priority': '^Trigger nseverity: .*',
        'configuration_item': '^Host: .*',
        'short_description': '^Trigger: .*',
        'zabbix_event_id': '^Zabbix event ID: .*',
    },
    # maps Zabbix value -> Service Now value
    'maps': {
        'impact': {
            # ServiceNow: 1 - High, 2 - Medium, 3 - Low
            # Zabbix:     0 - Not classified, 1 - Information, 2 - Warning, 3 - Average, 4 - High, 5  - Disaster
            '0': 'Low',
            '1': 'Low',
            '2': 'Medium',
            '3': 'Medium',
            '4': 'High',
            '5': 'High',
        },
        'urgency': {
            # ServiceNow: 1 - Immediate, 2 - Prompt, 3 - Non-urgent
            # Zabbix:     0 - Not classified, 1 - Information, 2 - Warning, 3 - Average, 4 - High, 5  - Disaster
            '0': 'Non-urgent',
            '1': 'Non-urgent',
            '2': 'Prompt',
            '3': 'Prompt',
            '4': 'Immediate',
            '5': 'Immediate',
        },
        'priority': {
            # ServiceNow: 1 - Critical, 2 - Error, 3 - Moderate, 4 - Low, 5 - Project
            # Zabbix:     0 - Not classified, 1 - Information, 2 - Warning, 3 - Average, 4 - High, 5  - Disaster
            '0': '4 - Low',
            '1': '4 - Low',
            '2': '3 - Moderate',
            '3': '2 - Error',
            '4': '1 - Critical',
            '5': '1 - Critical',
        }
    },
    # static
    'static': {
        'category': category,
        'subcategory': scategory,
        'caller': username,
        'assignment_group': agroup,
        'additional_comments': message,
    }
}

import re, sys, base64
incident = zabbix2servicenow['static']
for key in zabbix2servicenow['dynamic']:
    items=re.findall(zabbix2servicenow['dynamic'][key], message, re.MULTILINE)
    if len(items) != 1:
        if debug:
            print 'Problem with "%s" matching, found %i times' % (zabbix2servicenow['dynamic'][key], len(items))
        incident[key] = 'Problem with "%s" matching, found %i times' % (zabbix2servicenow['dynamic'][key], len(items))
        continue
    else:
        items[0] = items[0].split(':')[1].strip()
        if key in zabbix2servicenow['maps']:
            if items[0] not in zabbix2servicenow['maps'][key]:
                if debug:
                    print "Problem with mapping of value %s" % str(items[0])
                incident[key] = "Problem with mapping of value %s" % str(items[0])
            else:
                incident[key] = zabbix2servicenow['maps'][key][items[0]]
        else:
            incident[key] = items[0]

# add host name to short description
incident['short_description'] = incident['configuration_item'] + ": " + incident['short_description']

from SOAPpy import SOAPProxy
def createincident(incident):
        proxy = 'https://%s:%s@%s.service-now.com/%s?SOAP' % (username, base64.b64decode(password), instance, interface)
        namespace = 'http://www.service-now.com/'
        server = SOAPProxy(proxy, namespace)
        server.config.dumpHeadersIn = debug
        server.config.dumpHeadersOut = debug
        server.config.dumpSOAPOut = debug
        server.config.dumpSOAPIn = debug
        response = server.insert(
            impact              = incident['impact'],
            urgency             = incident['urgency'],
            priority            = incident['priority'],
            category            = incident['category'],
            subcategory         = incident['subcategory'],
            caller              = incident['caller'],
            assignment_group    = incident['assignment_group'],
            configuration_item  = incident['configuration_item'],
            short_description   = incident['short_description'],
            additional_comments = incident['additional_comments']
        )
        return response

if debug:
    print incident

# create incident
if subject == 'PROBLEM':
    response=createincident(incident)
    if debug:
        print "Server response: " + repr(response)
