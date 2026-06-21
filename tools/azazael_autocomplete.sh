#!/usr/bin/env bash
# Azazael Project — Shell Autocomplete
# Source this file:  source ~/Desktop/azazael_autocomplete.sh
# Or add to ~/.bashrc:  source ~/Desktop/azazael_autocomplete.sh

_azazael_completions() {
    local cur prev opts az_cmds hydra_cmds
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    az_cmds="hydra health import-test ner-benchmark system-scan"
    hydra_cmds="--discover --run --status --adapt --help --path"

    # Complete top-level commands
    if [[ ${COMP_CWORD} -eq 1 ]]; then
        COMPREPLY=($(compgen -W "${az_cmds}" -- ${cur}))
        return 0
    fi

    # Complete hydra subcommands
    if [[ ${COMP_WORDS[1]} == "hydra" ]] && [[ ${COMP_CWORD} -eq 2 ]]; then
        COMPREPLY=($(compgen -W "${hydra_cmds}" -- ${cur}))
        return 0
    fi
}

# Function shortcuts
az() {
    local cmd="$1"
    shift
    case "$cmd" in
        hydra)
            cd ~/Desktop/azazael-project-e && python3 HYDRA.py "$@"
            ;;
        health)
            KERAS_BACKEND=torch python3 ~/Desktop/health_check_azazael.py
            ;;
        import-test)
            KERAS_BACKEND=torch python3 ~/Desktop/test_azazael_imports.py "$@"
            ;;
        ner-benchmark)
            python3 ~/Desktop/benchmark_ner.py "$@"
            ;;
        system-scan)
            cd ~/Desktop/azazael-project-e && python3 SystemManager.py
            ;;
        *)
            echo "Usage: az {hydra|health|import-test|ner-benchmark|system-scan}"
            ;;
    esac
}

complete -F _azazael_completions az
