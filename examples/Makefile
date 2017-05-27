.PHONY: help init

kubectl = $(shell which kubectl)
helm = $(shell which helm)
gcloud = $(shell which helm)

help:
	@echo 'Usage:'
	@echo '  make <target>'
	@echo 
	@echo 'Targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo

version:              ## Show Tolls Versions
	@echo Kubectl Version
	$(kubectl) version
	@echo
	@echo Helm Version
	$(helm) version
	@echo 
	@echo GCloud Version
	$(gcloud) version

get-svc:             ## Get K8s services
	@$(kubectl) get svc

jenkins-get:         ## Check stack changes
	@echo Credentials: admin/$(shell $(kubectl) get secret --namespace default hackathon-jenkins -o jsonpath="{.data.jenkins-admin-password}" | base64 --decode) 
	@echo URL: http://$(shell $(kubectl) get svc hackathon-jenkins --namespace default --template '{{ range (index .status.loadBalancer.ingress 0) }}{{.}}{{ end }}'):8080/login