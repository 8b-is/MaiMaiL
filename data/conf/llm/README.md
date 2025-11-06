# LLM Configuration Directory

This directory contains configuration files for the Mailcow LLM email processing integration.

## Files

- **config.yml**: Main configuration file for LLM processing

## Configuration

Edit `config.yml` to customize:

- Ollama model selection
- Processing intervals and batch sizes
- Feature toggles
- Performance settings
- Alert thresholds

Changes to this file require restarting the llm-processor-mailcow container:

```bash
docker-compose restart llm-processor-mailcow
```

## Models

To change the LLM model:

1. Update `config.yml` with desired model
2. Pull the model:
   ```bash
   docker-compose exec ollama-mailcow ollama pull <model-name>
   ```
3. Restart the processor:
   ```bash
   docker-compose restart llm-processor-mailcow
   ```

## See Also

- Main documentation: `/LLM_INTEGRATION.md`
- Docker compose: `/docker-compose.yml`
