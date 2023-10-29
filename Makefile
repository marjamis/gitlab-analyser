.DEFAULT_GOAL := helper
GIT_COMMIT ?= $(shell git rev-parse --short=12 HEAD || echo "NoGit")
BUILD_TIME ?= $(shell date -u '+%Y-%m-%d_%H:%M:%S')
TEXT_RED = \033[0;31m
TEXT_BLUE = \033[0;34;1m
TEXT_GREEN = \033[0;32;1m
TEXT_NOCOLOR = \033[0m

GITLAB_HOME = ./data/gitlab_home

helper: # Adapted from: https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@echo "Available targets..." # @ will not output shell command part to stdout that Makefiles normally do but will execute and display the output.
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

command:
ifeq ($(origin GITLAB_TOKEN), undefined)
		echo "Required GILAB_TOKEN environment variable missing"
		exit 1
endif

ifeq ($(origin GITLAB_GRAPHQL_ENDPOINT), undefined)
		echo "Required GITLAB_GRAPHQL_ENDPOINT environment variable missing"
		exit 1
endif

	echo "Application run: $(OPTIONS)"
	python main.py $(OPTIONS)

test: ## Builds and then runs tests against the application
	pytest -vrP ./tests 

prod: ## Runs the prod version of the application
	$(MAKE) command

dev: ## Runs a dev version of the application
	GITLAB_GRAPHQL_ENDPOINT="http://localhost:8080/api/graphql" $(MAKE) command OPTIONS="--output-directory='./data/'"

generate-report: ## Runs the jupyter notebook and generates the resultant repot
	jupyter nbconvert --to html --no-input --output ./data/analysis.html ./analysis.ipynb

gitlab: ## Start the sample gitlab to be used for development work
	docker start gitlab || mkdir -p $(GITLAB_HOME) && \
	docker run --detach \
	--hostname gitlab \
	--publish 8443:443 \
	--publish 8080:80 \
	--publish 8022:22  \
	--name gitlab \
	--shm-size 256m \
	--volume $(shell pwd)/$(GITLAB_HOME)/config:/etc/gitlab \
	--volume $(shell pwd)/$(GITLAB_HOME)/logs:/var/log/gitlab \
	--volume $(shell pwd)/$(GITLAB_HOME)/data:/var/opt/gitlab \
	gitlab/gitlab-ce:16.1.5-ce.0 && \
	echo "To get the root password run: docker exec -it gitlab grep 'Password:' /etc/gitlab/initial_root_password"

clean: ## Cleans up any old/unneeded items
