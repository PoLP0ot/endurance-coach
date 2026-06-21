---
name: docker-first-execution
description: How to execute commands using Docker-first conventions in a Dockerized project.
---

> Claude Code adaptation: migrated from `skills/docker-first-execution/SKILL.md`. Use as a project skill under `.claude/skills/docker-first-execution/SKILL.md`.

# Docker-first Execution Playbook

## Execution Rules

- For lifecycle commands (start/stop/build):
  - Use `docker compose`

- For running scripts or one-off commands (npm, node, etc.):
  - Use `docker compose run --rm --service-ports`

## Failure Handling

- If a command fails due to ports already in use:
  1. Run `docker stop $(docker ps -a -q)` to stop all running containers
  2. Retry the original command

## Permissions

- Ensure permission is granted to access the Docker socket before execution
