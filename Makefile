HOSTTYPE=$(shell uname)
OPENSSL_LIB_EXTRA:=
ifeq ($(HOSTTYPE), Darwin)
MYSHELL=$(shell dscl . -read /Users/$$USER UserShell | awk '{print $$2}')
OPENSSL_LIB_EXTRA:=LDFLAGS="-L/usr/local/opt/openssl/lib"
else
# TODO figure out how to pick up user's config
MYSHELL=/usr/bin/bash
endif
SHELL_NAME=$(notdir $(MYSHELL))
ASDF_SCRIPT=asdf.sh
ifeq ($(SHELL_NAME), zsh)
  PROFILE_FILE=.zprofile
  FUNCTION_SUFFIX=is a shell function
else
  PROFILE_FILE=.bash_profile
  FUNCTION_SUFFIX=is a function
endif

update-deps:
	pip-compile --upgrade --allow-unsafe requirements/prod.in --resolver=backtracking
	pip-compile --upgrade --allow-unsafe requirements/dev.in --resolver=backtracking

dev-install: dev-env
	python -m pip install --upgrade pip pip-tools setuptools
	pip-sync requirements/*.txt
	python -m pip install -e .

dev-env: setup-dev
	@$(MYSHELL) -lc "pyenv versions | grep '3.10.4' -m 1 -o -q" || (echo 'Installing python 3.10.4' ; pyenv install 3.10.4)
	@$(MYSHELL) -lc "pyenv virtualenvs | grep '3.10.4/envs/sfla' -m 1 -o -q" || (echo 'Creating virtualenv for python 3.10.4' ; pyenv virtualenv 3.10.4 sfla)
	@$(MYSHELL) -lc 'test "$$(pyenv local)" = "sfla"' || (echo 'Setting up local environment' ; pyenv local sfla ; pyenv rehash ; pyenv activate sfla)

coverage:
	pytest --cov --cov-report=html
	open htmlcov/index.html

setup-dev:
	@# Platform specific dependencies for Mac OS
	@echo "checking for dependencies that require manual install:"
	@echo "Detected '$(SHELL_NAME)' as default shell."
	@echo "Using '~/$(PROFILE_FILE)' as shell profile location."
	@which -s brew > /dev/null || (echo "installing homebrew"; /usr/bin/ruby -e "$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)")
	@which -s pyenv > /dev/null || (echo "installing pyenv"; brew install pyenv)
	@which -s pyenv-virtualenv > /dev/null || (echo "installing pyenv-virtualenv"; brew install pyenv-virtualenv)
	@which -s sfdx || (echo "installing sfdx is required"; cd $(HOME)/Downloads; curl -O https://developer.salesforce.com/media/salesforce-cli/sfdx-osx.pkg && sudo installer -verboseR -pkg sfdx-osx.pkg -target / )
