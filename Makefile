PYTHON := python3
PIP := $(PYTHON) -m pip
VENV := .venv
VENV_BIN := $(VENV)/bin
VENV_PYTHON := $(VENV_BIN)/python
VENV_PIP := $(VENV_PYTHON) -m pip
VENV_APP := $(VENV_BIN)/jkpy

.DEFAULT_GOAL := help

NC := \033[0m
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
MAGENTA := \033[35m
CYAN := \033[36m

email=""
token=""
path=""
members=""
teams=""
statuses=""
labels=""
start=""
end=""

.PHONY: help venv install

##@ >>> Installation Targets
help: ## Display information for each run target
	@awk 'BEGIN { FS = ":.*##"; printf "\nUsage:\n make $(CYAN)<target>$(NC)\n" } \
	/^[a-zA-Z_0-9-]+:.*?##/ { printf "$(CYAN)%-20s$(NC) %s\n", $$1, $$2 } \
	/^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
venv: ## Create virtual environment
	@printf "$(CYAN)>>> Creating virtual environment...$(NC)\n"
	@if [ -f "$(VENV)/pyvenv.cfg" ]; then \
		printf "$(GREEN)>>> Virtual environment already exists$(NC)\n"; \
	else \
		$(PYTHON) -m venv $(VENV); \
		printf "$(GREEN)>>> Virtual environment created at %s$(NC)\n" "$(VENV)"; \
	fi
pre-commit-install: ## Install pre-commit hooks
	@printf "$(CYAN)>>> Installing pre-commit hooks...$(NC)\n"
	$(VENV_PYTHON) -m pre_commit install
	@printf "$(GREEN)>>> pre-commit hook Installation complete$(NC)\n"
install: venv ## Run application/project install
	@printf "$(CYAN)>>> Installing dependencies...$(NC)\n"
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install  -e .
	$(MAKE) pre-commit-install
	@printf "$(GREEN)>>> Project installation complete$(NC)\n"

##@ >>> Development Targets
clean: ## Remove all artifacts, cache, virtual environment, etc...
	@printf "$(CYAN)>>> Cleaning application/project...$(NC)\n"
	rm -rf $(VENV)
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-information
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*.egg' -delete
	@printf "$(GREEN)>>> Cleanup complete$(NC)\n"
test: ## Run tests (all files with *_test.py)
	@printf "$(CYAN)>>> Running tests...$(NC)\n"
	$(VENV_PYTHON) -m pytest
	@printf "$(GREEN)>>> Tests complete$(NC)\n"
coverage: ## Run tests with coverage report (all files with *_test.py)
	@printf "$(CYAN)>>> Running tests with coverage...$(NC)\n"
	$(VENV_PYTHON) -m pytest --cov=jkpy --cov-report=term-missing --cov=report=html
	@printf "$(GREEN)>>> Tests complete$(NC)\n"
	@printf "$(GREEN)>>> Coverage report generated in %s$(NC)\n" "htmlcov/index.html"
lint: ## Run all linters (ruff)
	@printf "$(CYAN)>>> Running linters...$(NC)\n"
	$(VENV_PYTHON) -m ruff check .
	@printf "$(GREEN)>>> Linting complete$(NC)\n"
format: ## Format code with black and isort
	@printf "$(CYAN)>>> Formatting code...$(NC)\n"
	$(VENV_PYTHON) -m black .
	@printf "$(CYAN)>>> Sorting imports...$(NC)\n"
	$(VENV_PYTHON) -m isort .
	@printf "$(GREEN)>>> Code formatting complete$(NC)\n"
check-format: ## Check code formatting w/o makeing changes
	@printf "$(CYAN)>>> Checking code formatting...$(NC)\n"
	$(VENV_PYTHON) -m black --check .
	$(VENV_PYTHON) -m isort --check-only .
	@printf "$(GREEN)>>> Code format checking complete$(NC)\n"
type-check: ## Run type checking
	@printf "$(CYAN)>>> Running type checker...$(NC)\n"
	$(VENV_PYTHON) -m mypy .
	@printf "$(GREEN)>>> Type checking complete$(NC)\n"

##@ >>> Setup and Configurations Targets
config: ## Show Configurations
	@printf "$(CYAN)%60s$(NC)\n" | tr " " "="
	@printf "$(CYAN)>>> Configurations:$(NC)\n"
	@printf "$(CYAN)%60s$(NC)\n" | tr " " "="
	@printf "${YELLOW}"
	@$(VENV_APP) --config | $(VENV_PYTHON) -m json.tool
	@printf "${NC}"
email: ## Set Jira email config
### make email --email=john.doe@gmail.com
	@printf "$(CYAN)>>> Setting %s configuration: %s\n" "email" "$(email)"
	$(VENV_APP) --email $(email)
token: ## Set Jira token config
### make token --token=AAB1213DWELK...
	@printf "$(CYAN)>>> Setting %s configuration: %s\n" "token" "$(token)"
	$(VENV_APP) --token $(token)
path: ## Set output path
### make path --path=~/Documents/jkpy
	@printf "$(CYAN)>>> Setting %s configuration: %s\n" "path" "$(path)"
	$(VENV_APP) --path $(path)
members: ## Set members by member name (e.g. John Doe)
### make members --members="John Doe","Dohn Joe",etc...
	@printf "$(CYAN)>>> Setting %s configuration: %s\n" "members" "$(members)"
	$(VENV_APP) --members $(members)
teams: ## Set teams by team name (e.g. ABC-TEAM-ONE)
### make teams --teams=ABC-team-one,ABC-team-two
	@printf "$(CYAN)>>> Setting %s configuration: %s\n" "teams" "$(teams)"
	$(VENV_APP) --teams $(teams)
statuses: ## Set statuses by status type (e.g. "in development")
### make statuses --statuses="in development","in qa",done,...
	@printf "$(CYAN)>>> Setting %s configuration: %s\n" "statuses" "$(statuses)"
	$(VENV_APP) --statuses $(statuses)
labels: ## Set labels for targeted metrics (e.g. "a/b test")
### make labels --labels="a/b test","rollover",etc...
	@printf "$(CYAN)>>> Setting %s configuration: %s\n" "labels" "$(labels)"
	$(VENV_APP) --labels $(labels)
start: ## Set start date for target dataset
### make start --start=2026-01-01
	@printf "$(CYAN)>>> Setting %s configuration: %s\n" "target start date" "$(start)"
	$(VENV_APP) --start $(start)
end: ## Set end date for target dataset
### make end --end=2026-02-01
	@printf "$(CYAN)>>> Setting %s configuration: %s\n" "target end date" "$(end)"
	$(VENV_APP) --end $(end)
range: ## Set date range for target dataset
### make range --start=2026-01-01 --end=2026-02-01
	@printf "$(CYAN)>>> Setting %s configuration: %s - %s\n" "target date range" "$(start)" "$(end)"	
	$(VENV_APP) --start $(start) --end $(end)
remove-members: ## Remove member(s)
### make remove-members --members="john doe"
	@printf "$(CYAN)>>> Removing %s from %s configuration\n" "$(members)" "members"
	$(VENV_APP) --remove-members $(members)
remove-teams: ## Remove team(s)
### make remove-teams --members=ABC-team-one
	@printf "$(CYAN)>>> Removing %s from %s configuration\n" "$(teams)" "teams"
	$(VENV_APP) --remove-teams $(teams)
remove-statuses: ## Remove status(es)
### make remove-statuses --statuses=done
	@printf "$(CYAN)>>> Removing %s from %s configuration\n" "$(statuses)" "statuses"
	$(VENV_APP) --remove-statuses $(statuses)
remove-labels: ## Remove label(s)
### make remove-labels --labels="rollover"
	@printf "$(CYAN)>>> Removing %s from %s configuration\n" "$(labels)" "labels"
	$(VENV_APP) --remove-labels $(labels)

##@ >>> Run Targets
run: ## Run application
	@printf "$(CYAN)>>> Running Application$(NC)"
	$(VENV_APP)
