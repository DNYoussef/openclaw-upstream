"""
Google Drive Connector for GuardSpine.

Watches Google Drive folders for changes and generates evidence bundles.
Supports the Board Packet workflow pattern.
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator, Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Import from connector template
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "open-source" / "guardspine-connector-template"))
from connector.base import BaseConnector
from connector.events import ChangeEvent, DiffResult, FileMetadata
from connector.bundle_emitter import BundleEmitter

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
]


class GoogleDriveConnector(BaseConnector):
    """
    Connector for Google Drive.

    Watches specified folders for document changes and generates
    evidence bundles for governance workflows.

    Supports:
    - PDF documents (contracts, legal)
    - XLSX spreadsheets (financials, forecasts)
    - DOCX documents (policies, procedures)
    - PPTX presentations (board decks)
    """

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.service = None
        self.credentials = None
        self.emitter = BundleEmitter(config)

        # Configuration
        self.watch_folders = config.get("source", {}).get("folders", [])
        self.poll_interval = config.get("source", {}).get("poll_interval", 60)
        self.token_path = config.get("source", {}).get("token_path", "token.json")
        self.credentials_path = config.get("source", {}).get("credentials_path", "credentials.json")

        # State tracking
        self._known_revisions: dict[str, str] = {}
        self._running = False

    async def start(self) -> None:
        """Initialize Google Drive API connection."""
        self.credentials = self._get_credentials()
        self.service = build("drive", "v3", credentials=self.credentials)
        self._running = True
        logger.info(f"GoogleDriveConnector started, watching {len(self.watch_folders)} folders")

    async def stop(self) -> None:
        """Stop the connector."""
        self._running = False
        logger.info("GoogleDriveConnector stopped")

    def _get_credentials(self) -> Credentials:
        """Get or refresh OAuth credentials."""
        creds = None

        if Path(self.token_path).exists():
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(self.token_path, "w") as token:
                token.write(creds.to_json())

        return creds

    async def watch_changes(self) -> AsyncIterator[ChangeEvent]:
        """
        Watch for file changes in configured folders.

        Yields ChangeEvent when:
        - New file added
        - Existing file modified (new revision)
        - .ready-for-review marker file detected (Board Packet workflow)
        """
        while self._running:
            for folder_id in self.watch_folders:
                async for event in self._scan_folder(folder_id):
                    if self.should_process(event.artifact_id):
                        yield event

            await asyncio.sleep(self.poll_interval)

    async def _scan_folder(self, folder_id: str) -> AsyncIterator[ChangeEvent]:
        """Scan a folder for changed files."""
        try:
            # Get files in folder
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed = false",
                fields="files(id, name, mimeType, modifiedTime, version, md5Checksum, size)",
                orderBy="modifiedTime desc",
            ).execute()

            files = results.get("files", [])

            for file_info in files:
                file_id = file_info["id"]
                current_version = file_info.get("version", file_info.get("modifiedTime"))

                # Check if file changed
                previous_version = self._known_revisions.get(file_id)
                if previous_version != current_version:
                    event = await self._create_change_event(file_info, folder_id, previous_version)
                    self._known_revisions[file_id] = current_version
                    yield event

        except Exception as e:
            logger.error(f"Error scanning folder {folder_id}: {e}")

    async def _create_change_event(
        self,
        file_info: dict,
        folder_id: str,
        previous_version: Optional[str]
    ) -> ChangeEvent:
        """Create a ChangeEvent from Drive file info."""
        file_id = file_info["id"]

        # Determine artifact kind
        mime_type = file_info.get("mimeType", "")
        kind = self._mime_to_kind(mime_type)

        # Build artifact ID
        artifact_id = f"gdrive:{folder_id}/{file_info['name']}"

        return ChangeEvent(
            event_id=f"gdrive-{file_id}-{datetime.utcnow().isoformat()}",
            artifact_id=artifact_id,
            artifact_kind=kind,
            from_version=previous_version,
            to_version=file_info.get("version", file_info.get("modifiedTime")),
            timestamp=datetime.fromisoformat(
                file_info["modifiedTime"].replace("Z", "+00:00")
            ),
            source="google-drive",
            metadata=FileMetadata(
                path=file_info["name"],
                size=int(file_info.get("size", 0)),
                mime_type=mime_type,
                checksum=file_info.get("md5Checksum"),
                extra={
                    "file_id": file_id,
                    "folder_id": folder_id,
                }
            ),
            risk_tier=self.map_risk_tier(artifact_id),
        )

    def _mime_to_kind(self, mime_type: str) -> str:
        """Map MIME type to artifact kind."""
        mapping = {
            "application/pdf": "pdf",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
            "application/vnd.google-apps.spreadsheet": "xlsx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
            "application/vnd.google-apps.document": "docx",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
            "application/vnd.google-apps.presentation": "pptx",
        }
        return mapping.get(mime_type, "unknown")

    async def get_diff(self, event: ChangeEvent) -> Optional[DiffResult]:
        """
        Get diff between file versions.

        For binary files (PDF, XLSX), downloads both versions
        and delegates to appropriate guard (PDFGuard, SheetGuard).
        """
        file_id = event.metadata.extra.get("file_id")
        if not file_id:
            return None

        try:
            # Get current content
            current_content = await self._download_file(file_id)
            current_hash = hashlib.sha256(current_content).hexdigest()

            # Get previous revision if available
            previous_content = None
            previous_hash = None

            if event.from_version:
                revisions = self.service.revisions().list(fileId=file_id).execute()
                for rev in revisions.get("revisions", []):
                    if rev.get("id") == event.from_version:
                        previous_content = await self._download_revision(file_id, rev["id"])
                        previous_hash = hashlib.sha256(previous_content).hexdigest()
                        break

            return DiffResult(
                diff_id=f"diff-{event.from_version or 'new'}-{event.to_version}",
                algorithm=self._get_diff_algorithm(event.artifact_kind),
                from_hash=previous_hash,
                to_hash=current_hash,
                from_content=previous_content,
                to_content=current_content,
                stats={
                    "has_previous": previous_content is not None,
                    "current_size": len(current_content),
                    "previous_size": len(previous_content) if previous_content else 0,
                },
            )

        except Exception as e:
            logger.error(f"Error getting diff for {file_id}: {e}")
            return None

    def _get_diff_algorithm(self, kind: str) -> str:
        """Get appropriate diff algorithm for artifact kind."""
        algorithms = {
            "pdf": "pdf-text-extract",
            "xlsx": "cell-comparison",
            "docx": "paragraph-diff",
            "pptx": "slide-diff",
        }
        return algorithms.get(kind, "binary-hash")

    async def _download_file(self, file_id: str) -> bytes:
        """Download current file content."""
        request = self.service.files().get_media(fileId=file_id)
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        return buffer.getvalue()

    async def _download_revision(self, file_id: str, revision_id: str) -> bytes:
        """Download specific revision content."""
        request = self.service.revisions().get_media(
            fileId=file_id, revisionId=revision_id
        )
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        return buffer.getvalue()

    async def get_artifact_metadata(self, artifact_id: str) -> dict[str, Any]:
        """Get metadata for a Drive file."""
        # Parse artifact_id: gdrive:{folder_id}/{filename}
        parts = artifact_id.replace("gdrive:", "").split("/", 1)
        if len(parts) != 2:
            return {}

        folder_id, filename = parts

        try:
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and name = '{filename}'",
                fields="files(id, name, mimeType, modifiedTime, version, owners, permissions, size)",
            ).execute()

            files = results.get("files", [])
            if not files:
                return {}

            file_info = files[0]
            return {
                "id": file_info["id"],
                "name": file_info["name"],
                "mime_type": file_info.get("mimeType"),
                "modified_time": file_info.get("modifiedTime"),
                "version": file_info.get("version"),
                "size": file_info.get("size"),
                "owners": [o.get("emailAddress") for o in file_info.get("owners", [])],
            }

        except Exception as e:
            logger.error(f"Error getting metadata for {artifact_id}: {e}")
            return {}

    async def healthcheck(self) -> dict[str, Any]:
        """Check Google Drive API connectivity."""
        try:
            about = self.service.about().get(fields="user").execute()
            return {
                "healthy": True,
                "connector": self.name,
                "type": "google-drive",
                "user": about.get("user", {}).get("emailAddress"),
                "folders_watched": len(self.watch_folders),
            }
        except Exception as e:
            return {
                "healthy": False,
                "connector": self.name,
                "type": "google-drive",
                "error": str(e),
            }


class BoardPacketWatcher(GoogleDriveConnector):
    """
    Specialized connector for Board Packet workflow.

    Watches for .ready-for-review marker files and triggers
    coherence gate when all documents are ready.
    """

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.marker_file = config.get("workflow", {}).get("marker_file", ".ready-for-review")
        self.coherence_enabled = config.get("coherence", {}).get("enabled", True)

    async def _scan_folder(self, folder_id: str) -> AsyncIterator[ChangeEvent]:
        """Scan for board packet folders with ready marker."""
        async for event in super()._scan_folder(folder_id):
            yield event

        # Check for ready marker
        if await self._check_ready_marker(folder_id):
            yield await self._create_coherence_event(folder_id)

    async def _check_ready_marker(self, folder_id: str) -> bool:
        """Check if .ready-for-review marker exists."""
        try:
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and name = '{self.marker_file}'",
                fields="files(id)",
            ).execute()
            return len(results.get("files", [])) > 0
        except Exception:
            return False

    async def _create_coherence_event(self, folder_id: str) -> ChangeEvent:
        """Create coherence gate trigger event."""
        return ChangeEvent(
            event_id=f"coherence-{folder_id}-{datetime.utcnow().isoformat()}",
            artifact_id=f"gdrive:{folder_id}",
            artifact_kind="folder",
            from_version=None,
            to_version="coherence-check",
            timestamp=datetime.utcnow(),
            source="google-drive",
            metadata=FileMetadata(
                path=folder_id,
                size=0,
                mime_type="application/vnd.google-apps.folder",
                extra={"trigger": "coherence_gate", "marker": self.marker_file}
            ),
            risk_tier="L4",  # Board packets are always high risk
        )
