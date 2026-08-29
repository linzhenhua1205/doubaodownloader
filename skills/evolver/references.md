# Evolver References

## GEP Protocol References
- [GEP Genome Evolution Protocol Specification](https://github.com/EvoMap/evolver)
- [EvoMap Documentation](https://evomap.io)

## Related Skills
- [skill-security-vetter](../skill-security-vetter/SKILL.md) - Security review before evolution
- [karpathy-guidelines](../karpathy-guidelines/SKILL.md) - Coding principles for evolution
- [open-source-skill-packer](../open-source-skill-packer/SKILL.md) - Open source skill packaging

## External Resources
- [ClawHub Evolver](https://clawhub.ai/skill/evolver)
- [OpenClaw Documentation](https://openclaw.dev)

## File References
- `assets/gep/genes.json` - Gene library
- `assets/gep/capsules.json` - Capsule definitions
- `assets/gep/events.jsonl` - Evolution audit trail
- `memory/narrative.log` - Narrative logs
- `memory/reflection.log` - Reflection logs
- `scripts/scan_logs.py` - Log scanning script
- `scripts/match_genes.py` - Gene matching script
- `scripts/apply_changes.py` - Change application script
- `scripts/validate.py` - Validation script
- `scripts/evolve.py` - Main evolution script

## Evolution Strategies
- **balanced**: Default strategy, balanced innovation and optimization
- **innovate**: Focus on new features and exploration
- **harden**: Focus on reliability and convergence
- **repair-only**: Emergency fix mode

## Safety Guidelines
1. Always run in review mode first (`--review`)
2. Regularly check events.jsonl for audit trail
3. Use git for version control of changes
4. Configure appropriate rollback mode
5. Monitor evolution results for effectiveness
