.PHONY: docker-build deploy

docker-build:
	docker build -t 923eb773-kr1-registry.container.nhncloud.com/uragan-container-registry/horcrux -f ./Dockerfile .

docker-push: docker-build
	docker push 923eb773-kr1-registry.container.nhncloud.com/uragan-container-registry/horcrux

deploy:
	kubectl apply -f deploy/kubernetes/deployment.yaml

d-deploy:
	kubectl delete -f deploy/kubernetes/deployment.yaml