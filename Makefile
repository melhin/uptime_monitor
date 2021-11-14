COMPOSE=docker-compose
SUPPORT= $(COMPOSE) -f docker-compose-support.yaml

start:
	$(COMPOSE) up -d

rebuild:
	$(COMPOSE) up --build -d --remove-orphans

logs:
	$(COMPOSE) logs --follow

stop:
	$(COMPOSE) down

clean:
	$(COMPOSE) down --remove-orphans --volumes

start-support:
	$(SUPPORT) up -d

logs-support:
	$(SUPPORT) logs --follow

stop-support:
	$(SUPPORT) down

clean-support:
	$(SUPPORT) down --remove-orphans --volumes