
I want to make a short technical repport to summarize the architecture/infrastructure (I don't know what word to use) of this project. Could you help me out with that? write it in @repport/main.tex I was thinking of putting the following sections:

# Introduction

basically that this is an e-commerce social-media-like platform backend that handles logistics such as payments, delivery, and products/stock management. It is a microservice architecture with the service division being based on the business logic and division of responsiblity

# Architecutre/infrastructure (I don't know what word to use)

## 1. REST APIs

Basically say that the each microservice exposes a REST API

## 2. Authentication

Explain:

- JWT structure and claims and a basic explanation of how access and refresh tokens
- How each service locally verifies the signature usign RS256 keys without requesting anything from auth


## 3. State-consistency with RabbitMQ

- Start by an explanation of user roles
- start by giving an example workflow of a user creating a store in the store_service and then user_service having to promote the user's role from 'BUYER' to 'SELLER'
- Explain the exception of the payment validation process and how it needs to be a synchronized request
- note that each service will need at least an instance of the REST server as well has a `start_consumer` server

## 4. Discovery and registry

- Explain the code that registers itself in @services/delivery_service/delivery/consul_registry.py and how it passes
  it's port number and address passed in @services/delivery_service/run.sh

---


- do it in french
- keep it short and concise and use simple language
- draw a graph detailing the infra/architecture
