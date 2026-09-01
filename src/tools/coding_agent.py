import asyncio
import os
import re
import shutil
import urllib.parse

import aiohttp

GITLAB_API = "https://gitlab.com/api/v4"
REPO_DIR = "/tmp/frontend-repo"

# Guardrails: the coding agent only ever touches this one pre-approved repo,
# always on a fresh branch off main, and only Read/Write/Edit/git/npm tools -
# no arbitrary shell access. It never merges - a human reviews the MR.
ALLOWED_TOOLS = "Read,Write,Edit,Glob,Grep,Bash(git:*),Bash(npm:*)"


class CodingAgentError(Exception):
    pass


def _project_path() -> str:
    return os.environ["GITLAB_PROJECT_PATH"]


def _repo_url() -> str:
    token = os.environ["GITLAB_TOKEN"]
    return f"https://oauth2:{token}@gitlab.com/{_project_path()}.git"


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:40] or "feature"


async def _run(*cmd: str, cwd: str | None = None) -> str:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    out, _ = await proc.communicate()
    text = out.decode(errors="replace")
    if proc.returncode != 0:
        raise CodingAgentError(f"`{' '.join(cmd)}` failed:\n{text}")
    return text


async def _open_merge_request(branch: str, title: str) -> str:
    project_id = urllib.parse.quote(_project_path(), safe="")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{GITLAB_API}/projects/{project_id}/merge_requests",
            headers={"PRIVATE-TOKEN": os.environ["GITLAB_TOKEN"]},
            json={
                "source_branch": branch,
                "target_branch": "main",
                "title": title,
                "remove_source_branch": True,
            },
        ) as resp:
            data = await resp.json()
            if resp.status >= 400:
                raise CodingAgentError(f"GitLab MR creation failed ({resp.status}): {data}")
            return data["web_url"]


async def implement_feature(feature_request: str) -> str:
    """Implement a requested feature in the frontend repo and open a GitLab merge request.

    Clones the frontend project fresh from `main`, creates a new branch dedicated
    to this feature request, has an AI coding agent make the change inside
    `frontend/`, verifies it with `npm run build`, then pushes the branch and
    opens a merge request for human review. Never commits directly to `main` and
    never merges on its own.
    """
    shutil.rmtree(REPO_DIR, ignore_errors=True)
    await _run("git", "clone", "--depth", "1", _repo_url(), REPO_DIR)
    await _run("git", "config", "user.email", "teams-agent-bot@christian.local", cwd=REPO_DIR)
    await _run("git", "config", "user.name", "Teams Agent Bot", cwd=REPO_DIR)

    branch = f"agent/{_slugify(feature_request)}"
    await _run("git", "checkout", "-b", branch, cwd=REPO_DIR)

    prompt = (
        "You are working inside a git repository. Only modify files under the "
        f"frontend/ directory - never touch anything outside it. Implement this "
        f"feature request as a small, correct, focused change: {feature_request}"
    )
    await _run(
        "claude",
        "-p",
        prompt,
        "--permission-mode",
        "acceptEdits",
        "--allowedTools",
        ALLOWED_TOOLS,
        cwd=REPO_DIR,
    )

    status = await _run("git", "status", "--porcelain", cwd=REPO_DIR)
    if not status.strip():
        return "No changes were made for that request - nothing to open a merge request for."

    # Guardrail: only push if the frontend still builds.
    frontend_dir = f"{REPO_DIR}/frontend"
    await _run("npm", "install", cwd=frontend_dir)
    await _run("npm", "run", "build", cwd=frontend_dir)

    await _run("git", "add", "-A", cwd=REPO_DIR)
    await _run("git", "commit", "-m", f"Agent: {feature_request}", cwd=REPO_DIR)
    await _run("git", "push", "origin", branch, cwd=REPO_DIR)

    mr_url = await _open_merge_request(branch, feature_request)
    return f"Done - opened a merge request for review: {mr_url}"
