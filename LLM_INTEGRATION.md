# Mailcow LLM Email Processing Integration

This integration adds local LLM-powered email analysis capabilities to Mailcow, providing intelligent email processing without sending data to external services.

## Features

- **Email Summarization**: Automatically generate concise summaries of email content
- **Smart Categorization**: AI-powered email categorization and tagging
- **Enhanced Phishing Detection**: Advanced phishing detection using LLM analysis
- **Priority Scoring**: Intelligent priority scoring based on content analysis
- **Sensitive Data Detection**: Identify emails containing sensitive information
- **Auto-Reply Suggestions**: Generate contextual auto-reply suggestions (experimental)

## Architecture

The LLM integration consists of three main components:

1. **Ollama Service** (`ollama-mailcow`): Hosts the local LLM models
2. **Email Processor** (`llm-processor-mailcow`): Python service that analyzes emails
3. **API & Database**: Extended mailcow API and database schema for LLM features

## Installation & Setup

### Prerequisites

- Docker and Docker Compose
- At least 8GB RAM (16GB recommended for larger models)
- GPU support (optional but recommended for better performance)

### Configuration

1. **Environment Variables**

Add these to your `mailcow.conf` or `.env` file:

```bash
# LLM Configuration
OLLAMA_MODEL=llama3.2:3b
LLM_PROCESSING_INTERVAL=60
LLM_BATCH_SIZE=10

# Optional: Use external Ollama instance (see "Using External Ollama" section below)
# OLLAMA_HOST=192.168.1.100:11434
```

2. **Pull the LLM Model**

After starting the services, pull your desired model:

```bash
docker-compose exec ollama-mailcow ollama pull llama3.2:3b
```

Available models:
- `llama3.2:3b` - Good balance of speed and accuracy (default)
- `mistral:7b` - Better accuracy, slower
- `phi3:mini` - Faster, lower resource usage
- `llama2:13b` - Best accuracy, requires more resources

3. **Start the Services**

For local Ollama deployment:
```bash
docker-compose --profile llm up -d
```

Or start services individually:
```bash
docker-compose up -d ollama-mailcow llm-processor-mailcow
```

4. **Verify Health**

Check the LLM processor status:

```bash
curl http://localhost/api/v1/get/llm/health
```

### Using External Ollama Instance

You can configure the LLM processor to use an Ollama instance running on a different server or network location. This is useful for:
- Load distribution across multiple servers
- Network traffic monitoring and analysis
- Running Ollama on a dedicated GPU server
- Privacy auditing with tools like Wireshark

#### Setup Steps:

1. **On the remote Ollama server:**

```bash
# Install and run Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Configure Ollama to listen on all interfaces
export OLLAMA_HOST=0.0.0.0:11434
ollama serve

# Pull your desired model
ollama pull llama3.2:3b
```

2. **On the Mailcow server:**

Add the external Ollama host to your `mailcow.conf`:

```bash
# External Ollama configuration
OLLAMA_HOST=192.168.1.100:11434  # Replace with your Ollama server IP/hostname
OLLAMA_MODEL=llama3.2:3b
```

3. **Start services with or without local Ollama:**

For local Ollama (default):
```bash
# Start with local Ollama instance
docker-compose --profile llm up -d
```

For external Ollama only:
```bash
# Start only the processor, not the local Ollama
docker-compose up -d llm-processor-mailcow
```

4. **Network monitoring (optional):**

To monitor network traffic between Mailcow and the external Ollama instance:

```bash
# On the Mailcow server
sudo tcpdump -i any host 192.168.1.100 and port 11434 -w ollama-traffic.pcap

# Or use Wireshark to capture and analyze traffic
```

#### Security Considerations:

- **Firewall**: Ensure port 11434 is only accessible from trusted networks
- **TLS**: Consider using a reverse proxy with TLS for encrypted communication
- **Network isolation**: Place Ollama on a separate VLAN if possible
- **Monitoring**: Use network monitoring tools to verify no data leaves your infrastructure

#### Troubleshooting:

If the health check fails with an external Ollama instance:

```bash
# Test connectivity from the processor container
docker-compose exec llm-processor-mailcow curl -v http://YOUR_OLLAMA_HOST:11434/api/tags

# Check Ollama server logs
# On the Ollama server
journalctl -u ollama -f
```

## API Usage

### Get Email Analysis

```bash
# Get analysis for specific email
curl -X GET "https://your-mailcow/api/v1/get/llm/analysis?mailbox=user@domain.com&email_id=12345" \
  -H "X-API-Key: your-api-key"

# Get all analyses for a mailbox
curl -X GET "https://your-mailcow/api/v1/get/llm/analysis?mailbox=user@domain.com" \
  -H "X-API-Key: your-api-key"
```

### Trigger Email Analysis

```bash
curl -X POST "https://your-mailcow/api/v1/add/llm/analyze" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "mailbox": "user@domain.com",
    "email_id": "12345",
    "force": false
  }'
```

### Get Statistics

```bash
curl -X GET "https://your-mailcow/api/v1/get/llm/stats" \
  -H "X-API-Key: your-api-key"
```

### Configure User Preferences

```bash
curl -X POST "https://your-mailcow/api/v1/edit/llm/preferences" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@domain.com",
    "auto_analysis": true,
    "auto_categorize": true,
    "phishing_alerts": true,
    "summary_enabled": true
  }'
```

## Database Schema

The integration adds four new tables:

1. **`llm_email_analysis`**: Stores email analysis results
2. **`llm_config`**: System-wide LLM configuration
3. **`llm_processing_queue`**: Email processing queue
4. **`llm_user_preferences`**: Per-user LLM preferences

## Performance Tuning

### For Limited Resources

```yaml
# data/conf/llm/config.yml
ollama:
  model: "phi3:mini"  # Smaller, faster model

processing:
  batch_size: 5
  interval: 120

performance:
  max_email_size: 2000
  concurrent_jobs: 1
```

### For High Performance

```yaml
# data/conf/llm/config.yml
ollama:
  model: "llama2:13b"  # Larger, more accurate model

processing:
  batch_size: 20
  interval: 30

performance:
  concurrent_jobs: 3
```

### GPU Support

The docker-compose configuration includes GPU support for NVIDIA GPUs. Ensure you have:

1. NVIDIA drivers installed
2. NVIDIA Container Toolkit installed
3. Docker configured for GPU support

To disable GPU support, remove these lines from `docker-compose.yml`:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

## Monitoring

### Health Check

```bash
docker-compose exec llm-processor-mailcow curl http://localhost:8080/health
```

### View Logs

```bash
docker-compose logs -f llm-processor-mailcow
docker-compose logs -f ollama-mailcow
```

### Check Processing Stats

```bash
docker-compose exec llm-processor-mailcow cat /var/log/llm-processor/processor.log
```

## Troubleshooting

### LLM Processor Won't Start

1. Check if Ollama is running: `docker-compose ps ollama-mailcow`
2. Verify the model is pulled: `docker-compose exec ollama-mailcow ollama list`
3. Check logs: `docker-compose logs llm-processor-mailcow`

### Slow Processing

1. Reduce batch size: Set `LLM_BATCH_SIZE=5`
2. Increase processing interval: Set `LLM_PROCESSING_INTERVAL=120`
3. Use a smaller model: Set `OLLAMA_MODEL=phi3:mini`

### High Memory Usage

1. Use a smaller model (phi3:mini or llama3.2:3b)
2. Reduce concurrent jobs in config.yml
3. Limit max_email_size in config.yml

### Analysis Not Working

1. Verify API endpoint: `curl http://llm-processor-mailcow:8080/health`
2. Check database tables exist: `docker-compose exec mysql-mailcow mysql -u mailcow -p mailcow -e "SHOW TABLES LIKE 'llm_%'"`
3. Verify email permissions and paths

## Privacy & Security

- **100% Local**: All processing happens on your server - no data leaves your infrastructure
- **No External APIs**: No calls to OpenAI, Anthropic, or other external services
- **GDPR Compliant**: Email data stays within your control
- **Encrypted Storage**: Analysis results stored in encrypted MySQL database

## Resource Requirements

| Model | RAM | Storage | CPU | Performance |
|-------|-----|---------|-----|-------------|
| phi3:mini | 4GB | 2GB | 2 cores | Fast |
| llama3.2:3b | 8GB | 3GB | 4 cores | Balanced |
| mistral:7b | 16GB | 5GB | 4 cores | Accurate |
| llama2:13b | 32GB | 8GB | 8 cores | Best |

## Roadmap

- [ ] Web UI for LLM configuration and monitoring
- [ ] Real-time email processing (via Dovecot plugin)
- [ ] Custom model fine-tuning capabilities
- [ ] Multi-language support
- [ ] Integration with Rspamd for spam scoring
- [ ] Automated response generation
- [ ] Email thread analysis
- [ ] Attachment content analysis

## Support

For issues, questions, or contributions:
- GitHub Issues: [mailcow/mailcow-dockerized](https://github.com/mailcow/mailcow-dockerized)
- Documentation: [docs.mailcow.email](https://docs.mailcow.email)

## License

This integration is part of Mailcow and follows the same GPL-3.0 license.
