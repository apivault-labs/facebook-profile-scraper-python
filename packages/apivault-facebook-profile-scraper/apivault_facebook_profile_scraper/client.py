"""Thin client for the hosted facebook-profile-scraper Apify Actor."""
from __future__ import annotations
from dataclasses import dataclass
import json, os, re, time, urllib.error, urllib.parse, urllib.request
from typing import Any, Mapping

ACTOR_ID = "NZ2v1fqLfaN2UBYIx"
API = "https://api.apify.com/v2"

class ActorError(RuntimeError):
    """The API rejected a request or the run did not succeed."""

class WaitTimeout(ActorError):
    """Waiting ended; resume this run instead of starting a duplicate."""
    def __init__(self, run_id: str):
        self.run_id = run_id
        super().__init__(f"Waiting timed out; resume run {run_id}")

@dataclass
class RunResult:
    run_id: str
    dataset_id: str
    status: str
    rows: list[dict[str, Any]]
    summary: Any
    errors: Any
    truncated: bool

class Client:
    """Start one hosted run, wait safely, and read rows plus diagnostics."""
    def __init__(self, token: str | None = None):
        self._token = (token or os.environ.get("APIFY_TOKEN") or os.environ.get("APIFY_API_TOKEN") or "").strip()
        if not self._token:
            raise ValueError("Provide an Apify token or set APIFY_TOKEN")

    @staticmethod
    def _id(value: str) -> str:
        if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", value):
            raise ValueError("Invalid Apify identifier")
        return value

    def _request(self, method: str, path: str, body: Any = None, params: dict | None = None, optional: bool = False) -> Any:
        url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
        request = urllib.request.Request(url, method=method,
            data=json.dumps(body).encode("utf-8") if body is not None else None,
            headers={"Authorization": "Bearer " + self._token, "Content-Type": "application/json", "User-Agent": "apivault-facebook-profile-scraper/0.1.0"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as error:
            if optional and error.code == 404:
                return None
            raise ActorError(f"Apify request failed with HTTP {error.code}") from None
        except (urllib.error.URLError, TimeoutError):
            raise ActorError("Apify request could not complete; check an existing run before retrying") from None

    def start(self, actor_input: Mapping[str, Any], *, max_total_charge_usd: float = 0.05, actor_timeout_secs: int = 300) -> dict[str, Any]:
        if not isinstance(actor_input, Mapping):
            raise TypeError("actor_input must be a mapping")
        if not 0 < max_total_charge_usd <= 1000 or not 1 <= actor_timeout_secs <= 3600:
            raise ValueError("Use a positive charge cap and timeout of 1–3600 seconds")
        # POST is never automatically retried: a retry could start a paid duplicate.
        response = self._request("POST", f"/acts/{ACTOR_ID}/runs", dict(actor_input),
            {"maxTotalChargeUsd": max_total_charge_usd, "timeout": actor_timeout_secs, "build": "latest"})
        run = response.get("data", {}) if isinstance(response, dict) else {}
        if not run.get("id"):
            raise ActorError("Apify did not return a run ID; check Console before retrying")
        return run

    def wait(self, run_id: str, *, wait_secs: float = 600, poll_interval: float = 3) -> dict[str, Any]:
        run_id = self._id(run_id)
        if wait_secs <= 0 or poll_interval <= 0:
            raise ValueError("wait_secs and poll_interval must be positive")
        deadline = time.monotonic() + wait_secs
        while time.monotonic() < deadline:
            run = self._request("GET", f"/actor-runs/{run_id}")["data"]
            if run["status"] == "SUCCEEDED":
                return run
            if run["status"] in {"FAILED", "ABORTED", "TIMED-OUT"}:
                raise ActorError(f"Run {run_id} ended with status {run['status']}")
            time.sleep(min(poll_interval, max(0, deadline-time.monotonic())))
        raise WaitTimeout(run_id)

    def result(self, run_id: str, *, max_rows: int = 1000) -> RunResult:
        run_id = self._id(run_id)
        if not isinstance(max_rows, int) or not 1 <= max_rows <= 100000:
            raise ValueError("max_rows must be an integer from 1 to 100000")
        run = self._request("GET", f"/actor-runs/{run_id}")["data"]
        if run["status"] != "SUCCEEDED":
            raise ActorError(f"Run {run_id} is {run['status']}; wait before reading results")
        dataset = self._id(run["defaultDatasetId"])
        metadata = self._request("GET", f"/datasets/{dataset}")["data"]
        rows: list[dict[str, Any]] = []
        while len(rows) < max_rows:
            limit = min(1000, max_rows-len(rows))
            page = self._request("GET", f"/datasets/{dataset}/items", params={"clean": "true", "limit": limit, "offset": len(rows)})
            if not isinstance(page, list):
                raise ActorError("Apify returned an unexpected Dataset response")
            if len(page) > limit:
                raise ActorError("Dataset response exceeded the requested page limit")
            rows.extend(page)
            if len(page) < limit:
                break
        store = self._id(run["defaultKeyValueStoreId"])
        summary = self._request("GET", f"/key-value-stores/{store}/records/SUMMARY", optional=True)
        errors = self._request("GET", f"/key-value-stores/{store}/records/ERRORS", optional=True)
        return RunResult(run_id, dataset, run["status"], rows, summary, errors, metadata.get("itemCount", len(rows)) > len(rows))

    def run(self, actor_input: Mapping[str, Any], *, max_total_charge_usd: float = 0.05, actor_timeout_secs: int = 300, wait_secs: float = 600, max_rows: int = 1000) -> RunResult:
        run = self.start(actor_input, max_total_charge_usd=max_total_charge_usd, actor_timeout_secs=actor_timeout_secs)
        self.wait(run["id"], wait_secs=wait_secs)
        return self.result(run["id"], max_rows=max_rows)
