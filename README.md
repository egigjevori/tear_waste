### Notes
- The project uses minimal dependencies, only the FastApi library and the cache/database connectors (bcrypt and load env also).
- The app supports a fine grained permission and role authorization system
  - routes require permissions
  - roles have multiple permissions
  - users are assigned roles


# Project Setup

Running this project requires **Docker** and **docker-compose** installed.

### To run the project:
1. Rename `.env.example` to `.env`
2. Run `docker-compose up --build`
3. Access [http://localhost:8000/docs](http://localhost:8000/docs)
---

### Deploy using Minikube (minikube already started):
1. Run `docker build -t tearwaste .`
2. Load local image to minikube `minikube image load tearwaste`
3. Run `kubectl apply -f deployments/`
4. Run `minikube service tearwaste --url`
---


## API Architecture - Layered Architecture

Layered architecture organizes code into horizontal layers, each with a specific responsibility, where higher layers depend on lower layers.

### How The Project Implements Layered Architecture:

1. **Presentation Layer**
   - Routes, controllers, request/response handling, input validation, exception handling.

2. **Service/Business Logic Layer**
   - Service modules containing domain logic (e.g., `authentication_service`, `authorization_service`)
   - Business rules and workflows
   - Domain-specific error types

3. **Data Access Layer**
   - Cache and database repositories

### Benefits

- **Testability**: Services can be tested in isolation without HTTP or database dependencies.
- **Flexibility**: You could replace FastAPI with another web framework with minimal changes to your core logic. Database technology could be swapped by implementing new repositories.
- **Maintainability**: Clear separation of concerns makes the codebase easier to understand. Changes to one layer have minimal impact on others.
- **Scalability**: Different layers can be scaled independently based on demand. Clear boundaries make it easier to refactor for performance.
- **Evolvability**: New features can be added by extending existing layers without disrupting the overall architecture. The system can evolve over time while maintaining structural integrity.

---

## Deployment Architecture

The application follows a modern microservices deployment pattern in Kubernetes with these key components:

1. **Load Balancer (External)**
   - Distributes incoming traffic across multiple API Gateway instances

2. **API Gateway**
   - Routing and rate limiting

3. **REST API Service (Multiple Replicas)**
   - Our FastAPI application, easily scalable.

4. **Redis Cache**
   - Cache frequently accessed data to reduce database load

5. **PostgreSQL Database**
   - Persistent data storage, easily scalable.

---

