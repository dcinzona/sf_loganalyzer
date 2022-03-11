## SOQL Query counter

Processes a log and counts the number of SOQL queries from Flows and Apex.

Outputs to CSV.

_Until I get this as an installable module, execute the Query Counter this way_

- command: `py -m sfloganalyzer soql [logfile]` -> Saves to `[logfile].csv`

## Log vizualizer

**Under development**

Goal is to visualize / enumerate all of the automated processes that fire in the context of the transaction.
Requires the [graphviz](https://graphviz.readthedocs.io/en/stable/manual.html) python module

### Setup

Take a look at the **DEV Setup** section for, perhaps, an easier time getting this running.

- Install dependencies: `pip install --upgrade -r requirements.txt`
- Base command: `py -m sfloganalyzer render [logfile]`
- Redacted output command (helpful for sharing output without class/flow names):
  `py -m sfloganalyzer render -R [logfile]`

Options: `py -m sfloganalyzer render --help`

### DEV Setup

**Using Make**

Install dev dependencies: `make dev-install`

Run the script: `sfla render [options] [logfile]` or `sfla soql [logfile]`

_TODO_

1. Support other event types (DML, SOQL, Callouts, etc)
2. Count SOQL Queries and limits effectively _per node collected_
3. Cluster support (by code units?)
4. D3 or similar interactive html output
5. Convert to installable package
6. Test on Windows (currently tested on Mac OS)

_Additional Resources_

- [Debug Log Levels](https://help.salesforce.com/s/articleView?id=sf.code_setting_debug_log_levels.htm&type=5)

_Notable Mentions_
Some of this code includes modified code from [CumulusCI](https://github.com/SFDO-Tooling/CumulusCI)
