# Homelab Change Record Schema

Structured change records are stored in:

docs/changes/

## Required Fields

- date
- title
- change_type
- status
- summary
- verification

## Optional Fields

- hosts
- services_added
- services_changed
- services_removed
- domains
- ports
- files_created
- files_changed
- files_generated
- commands_run
- impact
- follow_up
- documentation

## Change Types

- service_deployment
- service_update
- configuration_change
- documentation
- automation
- backup_change
- monitoring_change
- network_change
- security_change
- experiment

## Status Values

- planned
- in_progress
- completed
- verified
- rolled_back