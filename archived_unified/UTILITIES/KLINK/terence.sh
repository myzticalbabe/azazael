#!/bin/bash
# ============================================================================
# AZAZAEL TERENCE COMMAND - Error Resolver
# Usage: ./terence.sh [command]
# ============================================================================

export AZAZAEL_ROOT="${AZAZAEL_ROOT:-$HOME/Desktop/Azazael}"

case "${1:-}" in
    --help|-h|"")
        echo "TERENCE - Error Resolution System"
        echo ""
        echo "Usage: terence.sh [command]"
        echo ""
        echo "Commands:"
        echo "  scan        - Scan for errors"
        echo "  fix         - Auto-fix errors"
        echo "  report      - Generate error report"
        echo "  --help      - Show this help"
        ;;
    scan|fix|report)
        python3 "$AZAZAEL_ROOT/TERENCE/TERENCE.py" --${1}
        ;;
    *)
        python3 "$AZAZAEL_ROOT/TERENCE/TERENCE.py" --scan
        ;;
esac
