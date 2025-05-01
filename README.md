# Self-hosted Automation & Integration Stack

This repository provides a Docker Compose template that quickly bootstraps a self-hosted automation and integration environment including n8n for workflow automation, Supabase for database, Redis for caching, and Evolution API for WhatsApp integration, all secured behind Caddy as a reverse proxy.

## What's Included

✅ [**n8n**](https://n8n.io/) - Low-code workflow automation platform with 400+ integrations

✅ [**Supabase**](https://supabase.com/) - Open source PostgreSQL database with authentication and vector capabilities

✅ [**Redis**](https://valkey.io/) - Via Valkey, an open-source, high-performance in-memory data store

✅ [**Evolution API**](https://github.com/EvolutionAPI/evolution-api) - WhatsApp integration API for business communication

✅ [**Caddy**](https://caddyserver.com/) - Automatic HTTPS with zero configuration reverse proxy

## Prerequisites

Before you begin, make sure you have the following software installed:

- [Python](https://www.python.org/downloads/) - Required to run the setup script
- [Git/GitHub Desktop](https://desktop.github.com/) - For easy repository management
- [Docker/Docker Desktop](https://www.docker.com/products/docker-desktop/) - Required to run all services

## Installation

Clone the repository and navigate to the project directory:
```bash
git clone https://github.com/your-username/self-hosted-automation-stack.git
cd self-hosted-automation-stack
```

Before running the services, you need to set up your environment variables:

1. Make a copy of `.env.example` and rename it to `.env` in the root directory
2. Set the following required environment variables:
   ```bash
   ############
   # N8N Configuration
   ############
   N8N_ENCRYPTION_KEY=your-encryption-key
   N8N_USER_MANAGEMENT_JWT_SECRET=your-jwt-secret

   ############
   # Supabase Secrets
   ############
   POSTGRES_PASSWORD=your-postgres-password
   JWT_SECRET=your-jwt-secret
   ANON_KEY=your-anon-key
   SERVICE_ROLE_KEY=your-service-role-key
   DASHBOARD_USERNAME=your-dashboard-username
   DASHBOARD_PASSWORD=your-dashboard-password
   POOLER_TENANT_ID=your-pooler-tenant-id

   ############
   # Evolution API Configuration
   ############
   EVOLUTION_API_KEY=your-evolution-api-key
   WEBHOOK_GLOBAL_URL=your-webhook-url
   
   # WhatsApp display configuration
   CONFIG_SESSION_PHONE_CLIENT=EvolutionAPI
   CONFIG_SESSION_PHONE_NAME=Chrome
   
   # Optional Redis authentication
   REDIS_USERNAME=
   REDIS_PASSWORD=
   ```

For production deployments, uncomment and configure these additional variables:
```bash
############
# Caddy Config
############
N8N_HOSTNAME=n8n.yourdomain.com
SUPABASE_HOSTNAME=supabase.yourdomain.com
EVOLUTION_API_HOSTNAME=evolution-api.yourdomain.com
LETSENCRYPT_EMAIL=your-email-address
```

## Starting the Services

The project includes a `start_services.py` script that handles starting both the Supabase and core services:

```bash
python start_services.py
```

This will:
1. Clone/update the Supabase repository
2. Configure the environment
3. Start Supabase
4. Wait for initialization
5. Start n8n, Redis, Evolution API, and Caddy

## Accessing the Services

Once the services are running, you can access them at:

- **n8n**: http://localhost:5678
- **Supabase**: http://localhost:3000
- **Evolution API**: http://localhost:8080

For production deployments with custom domains, configure the Caddy environment variables in your `.env` file.

## Using n8n with Evolution API

To create a WhatsApp integration workflow in n8n:

1. Create a new workflow in n8n
2. Add an HTTP Request node to connect to Evolution API:
   - Method: POST
   - URL: `{{$env.EVOLUTION_API_HOST}}/api/[[endpoint]]`
   - Headers: `{"apikey": "{{$env.EVOLUTION_API_KEY}}"}`
   - Authentication: None
   - JSON Body: Your WhatsApp message payload

3. Test your workflow with Evolution API

### WhatsApp Client Display Name Configuration

Evolution API allows you to configure how the WhatsApp connection appears on your smartphone:

- `CONFIG_SESSION_PHONE_CLIENT`: The client name shown in WhatsApp connection info (default: "EvolutionAPI")
- `CONFIG_SESSION_PHONE_NAME`: The browser name shown in WhatsApp connection info (default: "Chrome")

This helps identify your automation connection in the WhatsApp connected devices list.

## Upgrading

To update all containers to their latest versions, run:

```bash
# Stop all services
docker compose -p localai -f docker-compose.yml -f supabase/docker/docker-compose.yml down

# Pull latest versions
docker compose -p localai -f docker-compose.yml -f supabase/docker/docker-compose.yml pull

# Start services again
python start_services.py
```

## Troubleshooting

Here are solutions to common issues:

### Supabase Issues

- **Supabase Pooler Restarting**: If the supabase-pooler container keeps restarting, follow the instructions in [this GitHub issue](https://github.com/supabase/supabase/issues/30210#issuecomment-2456955578).

- **Supabase Analytics Startup Failure**: If the supabase-analytics container fails to start after changing your Postgres password, delete the folder `supabase/docker/volumes/db/data`.

- **If using Docker Desktop**: Go into the Docker settings and make sure "Expose daemon on tcp://localhost:2375 without TLS" is turned on.

### WhatsApp Connection Issues

- **Evolution API Connection**: Ensure your Evolution API key is correctly set in the .env file.
- **QR Code Scanning**: Follow the Evolution API documentation to properly connect WhatsApp devices.

### Redis Connection Issues

- **n8n Redis Credentials**: When setting up Redis credentials in n8n, use the values from your .env file:
  - Host: `redis`
  - Port: `6379`
  - Username: Value of `REDIS_USERNAME` (leave empty if not using authentication)
  - Password: Value of `REDIS_PASSWORD` (leave empty if not using authentication)

## Testing Service Connections

To verify that all services are properly connected and accessible from n8n:

1. Import the `Test_Service_Connections.json` workflow from the `n8n-tool-workflows` directory
2. Set up the required credentials:
   - **Postgres**: Host: `db`, Port: `5432`, Database: `postgres`, User: `postgres`, Password: your `POSTGRES_PASSWORD`
   - **Redis**: Host: `redis`, Port: `6379`, Optional Username/Password from your .env file
3. Run the workflow to test connections to:
   - PostgreSQL database
   - Redis
   - Qdrant vector store
   - Ollama model server
   - Evolution API
   - Supabase API (via Kong)
4. The workflow will aggregate results and show which services are accessible

### Individual Service Connection Details

| Service | Access From n8n | Credentials |
|---------|----------------|-------------|
| PostgreSQL | `db:5432` | User: postgres, Password: POSTGRES_PASSWORD |
| Supabase API | `http://kong:8000/rest/v1/` | apikey: ANON_KEY, Authorization: Bearer ANON_KEY |
| Redis | `redis:6379` | Username: REDIS_USERNAME, Password: REDIS_PASSWORD |
| Qdrant | `http://qdrant:6333` | None by default |
| Ollama | `http://ollama:11434` | None by default |
| Evolution API | `http://evolution-api:8080` | apikey: EVOLUTION_API_KEY<br>Display Names: CONFIG_SESSION_PHONE_CLIENT, CONFIG_SESSION_PHONE_NAME |

## 📜 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.