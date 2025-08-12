# Start from the official Ollama base image
# Docker will automatically pull the correct ARM64 version for your system
FROM ollama/ollama:latest

# --- Pre-pull the models you need ---
# This command runs during the image build process.
# The model will be baked into your final image.
RUN ollama serve & sleep 10 && \
    ollama pull phi3:mini


# CMD ["sh", "-c", "ollama serve & sleep 5 && ollama pull phi3:mini && wait"]

# You can add more models if you want
# For example, to also include gemma:2b:
# RUN ollama pull gemma:2b