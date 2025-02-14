VENV=~/Downloads/venv/jkpy

email=""
token=""
folderPath=""
nameLabels=""
teamLabels=""
statusTypes=""
metricLabels=""
removeNameLabels=""
removeTeamLabels=""
removeStatusTypes=""
removeMetricLabels=""
startDate=""
endDate=""

# make install
install:
	@if [ ! -d "venv" ]; then \
		python3 -m venv $(VENV); \
	fi
	$(VENV)/bin/pip3 install -q build
	$(VENV)/bin/python3 -m build
	$(VENV)/bin/pip3 install dist/jkpy-1.0.0.tar.gz

# make help
help: 
	$(VENV)/bin/jkpy --help

# make setup email=john@gmail.com token=abc123 folderPath=$HOME/Desktop nameLabels=a,b,c teamLabels=a,b,c statusTypes=a,b,c removeNameLabels=a,b,c removeTeamLabels=a,b,c removeStatusTypes=a,b,c
setup:
	$(VENV)/bin/jkpy --isSetup -e $(email) -t $(token) -fp $(folderPath) -nl $(nameLabels) -tl $(teamLabels) -st $(statusTypes) -ml $(metricLabels) --remove-nameLabels $(removeNameLabels) --remove-teamLabels $(removeTeamLabels) --remove-statusTypes $(removeStatusTypes) --remove-metricLabels $(removeMetricLabels)

# make config
config:
	$(VENV)/bin/jkpy --showConfig

# make run startDate=2025-01-01 endDate=2025-02-01 (i.e. date is in year-month-day format)
run:
	$(VENV)/bin/jkpy --startDate ${startDate} --endDate ${endDate}
