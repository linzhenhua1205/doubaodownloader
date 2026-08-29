# Discover Script Archive

This directory contains archived scripts from the `discover/` folder that are no longer actively maintained.

## Directory Structure

### `dead/`

Scripts with hardcoded paths to `h:\github\cowkb` (old machine) or other obsolete references. These scripts are **broken** and cannot be run without significant modifications:

- `newwiki/` - Legacy scripts for initial wiki processing
- `newwiki2/` - Intermediate scripts from the second wiki iteration
- `site/` - Site enhancement and quality scripts
- `root/` - Root-level discovery scripts

### `newwiki2/`

Archive of test/probe scripts and intermediate iterations:

- `ai-models/` - AI model scanning utilities
- `rename_tools/` - Probe scripts (`probe.py`, `probe2.py`, etc.) and `try_remove_lock.py`
- `batch_enhance_templates.py` - Template-based enhancement (deprecated)
- `batch_enhance_v3.py` - Batch enhancement v3 (deprecated)
- `fix_enhanced_files.py` - File fixing utilities
- `fix_titles_v2.py` - Title fixing utilities

### `site/`

Site maintenance scripts kept for historical reference:

- `fix_indexes.py` - Index fixing utilities
- `regenerate_indexes.py` - Index regeneration
- `scan_status.py` - Status scanning

## Migration Report

See `migration_report.json` for the complete migration details and mapping of old → new paths.

## Notes

- These scripts are kept for **reference purposes only**
- Production scripts have been moved to `scripts/discover/`
- Scripts in `dead/` contain hardcoded paths and should not be run directly
- If you need to reuse functionality from these scripts, check `scripts/discover/config.py` for the proper path configuration pattern
