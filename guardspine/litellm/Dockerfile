# Pinned to v1.82.3-stable.patch.2 (2026-03-24) -- post-TeamPCP supply chain fix.
# DO NOT use main-latest. See: https://docs.litellm.ai/blog/security-update-march-2026
# Safe versions: <= 1.82.6. Compromised: 1.82.7, 1.82.8.
FROM ghcr.io/berriai/litellm:main-v1.82.3-stable.patch.2
COPY config.yaml /app/config.yaml
CMD ["--config", "/app/config.yaml", "--port", "4000"]
