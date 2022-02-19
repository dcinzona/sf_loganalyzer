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
Not happy with how this is rendering out in the chart (not what I'm looking for). It's hard to follow.

1. See if this needs to be handled in order of execution on entry, rather than stack (so sort by line number and have the parent be the immediately preceding operation)