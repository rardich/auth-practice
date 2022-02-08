### Starting the Application
`docker-compose up -d --build`

### FastAPI Built-in Documentation
Describes request bodies at http://127.0.0.1:8000/docs

### Assumptions
- No need for logout API-side
  - JWT-based Authentication
  - State is stored client-side with JWT, when user logs out, token is deleted from client storage
  - Signing occurs server-side, decoding occurs client-side, verification happens on accessed resources
- The use of HS256 signing for JWT would be sufficient if I am also writing the client-side application

### Design Decisions
- FastAPI
	- Faster than Flask, comparable to Node and Go
	- Open source, robust, yet readable and easy to write
- PostgreSQL
	- Server-based, SQLite files do not support concurrent operations
	- Usage familiarity vs other SQL databases
- bcrypt
  - Wanted to salt and hash passwords, a package does it better than I can
- Separated environmental variables like passwords onto .env files to separate them from code
- Compose network
  - Specified custom bridge network to allow containers to talk to each other
  - Eliminates need to identify and reassign dynamic container IPs

### Known Issues
- JWT refreshing not implemented
  - No current time limit on valid tokens, if exposed, can be exploited
- API service restart on failure
  - API service attempts to connect to db before postgres starts up and connection is refused
  - Current workaround is by restarting 
  - Need to implement a health check for startup attempting to connect to db before it's running
- SQL initialization script not working, removed
  - Postgres not properly executing SQL commands to create tables
  - Directly initializing tables in API on execution
    - Introduces persistence issues when rebuilding (no persistence)
    - Forces some non-ideal hard-coding in API code