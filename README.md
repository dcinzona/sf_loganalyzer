## SOQL Query counter ##
Processes a log and counts the number of SOQL queries from Flows and Apex.  

Outputs to CSV.

command: `py readlog.py [logfile] [optional:outputFile]`

## Log vizualizer ##
**Under development**


Goal is to visualize / enumerate all of the automated processes that fire in the context of the transaction.
Requires the [graphviz](https://graphviz.readthedocs.io/en/stable/manual.html) python module 
### Setup ###
Install dependencies: `pip install --upgrade -r requirements.txt`

Base command: `py logviz.py [logfile]`

Options:
`py logviz.py --help`


_TODO_
1. Support other event types (DML, SOQL, Callouts, etc)
2. Count SOQL Queries and limits effectively _per node collected_


_Additional Resources_
- [Debug Log Levels](https://help.salesforce.com/s/articleView?id=sf.code_setting_debug_log_levels.htm&type=5)