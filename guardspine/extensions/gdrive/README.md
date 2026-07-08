# Google Drive Connector for GuardSpine

Watch Google Drive folders for document changes and generate verifiable evidence bundles.

## Features

- **Real-time monitoring**: Poll-based watching of Drive folders
- **Multi-format support**: PDF, XLSX, DOCX, PPTX
- **Board Packet workflow**: Coherence gate with `.ready-for-review` marker
- **Risk tier mapping**: Automatic classification by folder path
- **Diff generation**: Version-aware content comparison

## Quick Start

### 1. Install dependencies

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Set up Google Cloud credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Drive API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json` to connector directory

### 3. Configure connector

Edit `config.yaml`:

```yaml
source:
  folders:
    - "YOUR_FOLDER_ID" # Get from Drive URL
  credentials_path: "credentials.json"
  token_path: "token.json"
```

### 4. Run connector

```python
import asyncio
from gdrive_connector import GoogleDriveConnector, BoardPacketWatcher
import yaml

# Load config
with open("config.yaml") as f:
    config = yaml.safe_load(f)

# Create connector
connector = BoardPacketWatcher(config)

async def main():
    await connector.start()

    async for event in connector.watch_changes():
        print(f"Change detected: {event.artifact_id}")

        # Get diff
        diff = await connector.get_diff(event)
        if diff:
            print(f"  Diff: {diff.algorithm}, {diff.stats}")

        # Create bundle
        bundle = connector.emitter.create_bundle(event, diff)
        print(f"  Bundle: {bundle['bundle_id']}")

asyncio.run(main())
```

## Board Packet Workflow

The `BoardPacketWatcher` subclass implements the full Board Packet governance workflow:

1. **Draft Stage**: Watch for file uploads to `Draft/` subfolder
2. **Review Stage**: Generate diffs and AI summaries for each change
3. **Coherence Gate**: Triggered when `.ready-for-review` marker is added
4. **Approval Stage**: Route to executive approvers via GuardSpine UI
5. **Lock Stage**: Move to `Final/` and generate master evidence bundle

### Folder Structure

```
Board Packets/
+-- Q1-2024/
|   +-- Draft/
|   |   +-- Q1-2024-Board-Deck-v3.pptx
|   |   +-- Q1-2024-Financials-rev12.xlsx
|   |   +-- .ready-for-review  <- Trigger coherence gate
|   +-- Final/
|       +-- Q1-2024-Board-Deck-FINAL.pdf
|       +-- evidence-bundle.zip
```

### Coherence Rules

Create `coherence-rules.yaml`:

```yaml
coherence_rules:
  - rule: revenue_match
    source: "Financial Summary!Revenue!Q4"
    targets:
      - "Board Deck!Slide 5!Revenue Figure"
      - "CEO Letter!Para 2!Revenue Mention"
    tolerance: 0.01 # 1% variance allowed

  - rule: date_consistency
    pattern: "Q[1-4] 20[0-9]{2}"
    must_match_across: all_documents
```

## Risk Mapping

Files are automatically classified by path:

| Path Pattern          | Risk Tier |
| --------------------- | --------- |
| `**/Board Packets/**` | L4        |
| `**/Contracts/**`     | L4        |
| `**/Financials/**`    | L3        |
| `**/HR/**`            | L3        |
| `**/Marketing/**`     | L2        |
| Default               | L1        |

## API Reference

### GoogleDriveConnector

```python
class GoogleDriveConnector(BaseConnector):
    async def watch_changes() -> AsyncIterator[ChangeEvent]
    async def get_diff(event: ChangeEvent) -> Optional[DiffResult]
    async def get_artifact_metadata(artifact_id: str) -> dict
    async def healthcheck() -> dict
```

### BoardPacketWatcher

```python
class BoardPacketWatcher(GoogleDriveConnector):
    # Adds coherence gate detection
    marker_file: str = ".ready-for-review"
    coherence_enabled: bool = True
```

## Environment Variables

| Variable            | Description            |
| ------------------- | ---------------------- |
| `SLACK_WEBHOOK_URL` | Slack notifications    |
| `SMTP_HOST`         | Email notifications    |
| `GUARDSPINE_URL`    | GuardSpine backend URL |

## License

Apache 2.0 - See [guardspine-connector-template](https://github.com/DNYoussef/guardspine-connector-template)
