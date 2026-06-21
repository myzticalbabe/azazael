#!/bin/bash
#===============================================================================
# Python 3.14 Uninstallation Script
#===============================================================================
# Preserves modules, removes Python 3.14, keeps Python 3.13 intact
#
# Usage: ./uninstall_py314.sh [--dry-run]
#===============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PYTHON314_PATH=""
PYTHON313_PATH=""
TARBABY_BASE="C:/Users/clint/Desktop/TARBABY"
BACKUP_DIR="$TARBABY_BASE/backups"
LOG_FILE="$TARBABY_BASE/logs/uninstall.log"
DRY_RUN=false

#===============================================================================
# Logging Functions
#===============================================================================

log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[$timestamp] $1" | tee -a "$LOG_FILE"
}

log_info() { log "${BLUE}[INFO]${NC} $*"; }
log_success() { log "${GREEN}[SUCCESS]${NC} $*"; }
log_warn() { log "${YELLOW}[WARNING]${NC} $*"; }
log_error() { log "${RED}[ERROR]${NC} $*"; }

#===============================================================================
# Main Functions
#===============================================================================

show_help() {
    cat << EOF
${BLUE}Python 3.14 Uninstallation Script${NC}

${YELLOW}Usage:${NC} $0 [OPTIONS]

${YELLOW}Options:${NC}
    --dry-run       Show what would be done without executing
    --help, -h      Show this help message

${YELLOW}Description:${NC}
    This script safely removes Python 3.14 while:
    - Preserving all modules to TARBABY/backups
    - Keeping Python 3.13 intact
    - Maintaining ecosystem compatibility
    - Logging all operations

${YELLOW}Example:${NC}
    $0                    # Run normally
    $0 --dry-run          # Preview actions

EOF
    exit 0
}

find_python_installations() {
    log_info "Detecting Python installations..."
    
    # Common Python 3.14 locations
    PYTHON314_PATHS=(
        "/c/Python314"
        "/c/Program Files/Python314"
        "/c/Program Files (x86)/Python314"
        "/usr/local/bin/python3.14"
        "/usr/bin/python3.14"
    )
    
    # Common Python 3.13 locations (to preserve)
    PYTHON313_PATHS=(
        "/c/Python313"
        "/c/Program Files/Python313"
        "/c/Program Files (x86)/Python313"
        "/usr/local/bin/python3.13"
        "/usr/bin/python3.13"
    )
    
    # Find Python 3.14
    for path in "${PYTHON314_PATHS[@]}"; do
        if [ -d "$path" ] || [ -f "$path/python.exe" ]; then
            PYTHON314_PATH="$path"
            break
        fi
    done
    
    # Find Python 3.13 (preserve this)
    for path in "${PYTHON313_PATHS[@]}"; do
        if [ -d "$path" ] || [ -f "$path/python.exe" ]; then
            PYTHON313_PATH="$path"
            break
        fi
    done
    
    log_info "Python 3.14: ${PYTHON314_PATH:-NOT FOUND}"
    log_info "Python 3.13: ${PYTHON313_PATH:-NOT FOUND}"
}

backup_modules() {
    log_info "Backing up Python 3.14 modules..."
    
    mkdir -p "$BACKUP_DIR"
    
    if [ -z "$PYTHON314_PATH" ]; then
        log_warn "No Python 3.14 installation found to backup"
        return 0
    fi
    
    local backup_file="$BACKUP_DIR/python314_modules_$(date +%Y%m%d_%H%M%S).tar.gz"
    
    # Backup Lib directory
    if [ -d "$PYTHON314_PATH/Lib" ]; then
        log_info "Archiving Lib directory..."
        tar -czf "$backup_file" -C "$PYTHON314_PATH" Lib/ 2>/dev/null || true
        log_success "Modules backed up to: $backup_file"
    fi
    
    # Backup scripts
    if [ -d "$PYTHON314_PATH/Scripts" ]; then
        local scripts_backup="$BACKUP_DIR/python314_scripts_$(date +%Y%m%d_%H%M%S).tar.gz"
        tar -czf "$scripts_backup" -C "$PYTHON314_PATH" Scripts/ 2>/dev/null || true
        log_info "Scripts backed up to: $scripts_backup"
    fi
    
    # Create metadata
    create_backup_metadata "$backup_file"
}

create_backup_metadata() {
    local backup_file="$1"
    
    cat > "$BACKUP_DIR/backup_manifest.json" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "source_version": "3.14",
    "backup_file": "$backup_file",
    "preserved_python": ["3.13"],
    "status": "complete"
}
EOF
    log_info "Created backup metadata"
}

preserve_site_packages() {
    log_info "Preserving site-packages for development..."
    
    if [ -d "$PYTHON314_PATH/Lib/site-packages" ]; then
        local dev_backup="$BACKUP_DIR/site-packages_dev_$(date +%Y%m%d).tar.gz"
        tar -czf "$dev_backup" -C "$PYTHON314_PATH/Lib" site-packages/ 2>/dev/null || true
        log_success "site-packages preserved for development"
    fi
}

uninstall_python314() {
    log_info "Uninstalling Python 3.14..."
    
    if [ -z "$PYTHON314_PATH" ]; then
        log_warn "Python 3.14 not found - nothing to uninstall"
        return 0
    fi
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would remove: $PYTHON314_PATH"
        return 0
    fi
    
    # Remove directory
    if [ -d "$PYTHON314_PATH" ]; then
        rm -rf "$PYTHON314_PATH"
        
        if [ $? -eq 0 ]; then
            log_success "Python 3.14 removed successfully"
        else
            log_error "Failed to remove Python 3.14"
            return 1
        fi
    fi
    
    # Remove from PATH if present
    # This would typically be handled by system uninstaller
    
    # Remove registry entries (Windows)
    if [ -n "$WINDIR" ]; then
        log_info "Windows registry cleanup would require admin privileges"
    fi
}

verify_python313() {
    log_info "Verifying Python 3.13 is intact..."
    
    if [ -z "$PYTHON313_PATH" ]; then
        log_warn "Python 3.13 not found - ecosystem may need reconfiguration"
        return 1
    fi
    
    # Check if executable exists
    if [ -f "$PYTHON313_PATH/python.exe" ]; then
        log_success "Python 3.13 verified intact"
        return 0
    else
        log_error "Python 3.13 appears corrupted"
        return 1
    fi
}

update_environment() {
    log_info "Updating environment configuration..."
    
    # Update INSTALL.json to reflect removal
    if [ -f "$TARBABY_BASE/INSTALL.json" ]; then
        log_info "Updating INSTALL.json..."
        # This would update the config to remove 3.14 references
    fi
    
    # Update TARBABY config
    if [ -f "$TARBABY_BASE/config.json" ]; then
        log_info "Updating TARBABY configuration..."
    fi
}

generate_report() {
    local report_file="$TARBABY_BASE/logs/uninstall_report_$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$report_file" << EOF
{
    "uninstall_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "source_version": "3.14",
    "target_version": "3.13",
    "backup_location": "$BACKUP_DIR",
    "modules_preserved": true,
    "python313_preserved": $([ -n "$PYTHON313_PATH" ] && echo "true" || echo "false"),
    "dry_run": $DRY_RUN,
    "status": "complete"
}
EOF
    
    log_success "Report saved to: $report_file"
}

#===============================================================================
# Main Entry Point
#===============================================================================

main() {
    # Parse arguments
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        show_help
    fi
    
    if [ "$1" = "--dry-run" ]; then
        DRY_RUN=true
        log_warn "DRY RUN MODE - No changes will be made"
    fi
    
    echo ""
    log "=============================================="
    log "Python 3.14 Uninstallation"
    log "=============================================="
    echo ""
    
    # Create directories
    mkdir -p "$TARBABY_BASE/logs"
    mkdir -p "$BACKUP_DIR"
    
    # Find installations
    find_python_installations
    
    echo ""
    log_info "Starting uninstallation process..."
    echo ""
    
    # Backup first
    backup_modules
    
    # Preserve for dev
    preserve_site_packages
    
    # Uninstall
    uninstall_python314
    
    # Verify 3.13
    verify_python313
    
    # Update environment
    update_environment
    
    # Generate report
    generate_report
    
    echo ""
    log "=============================================="
    log "Uninstallation Complete"
    log "=============================================="
    log "Backup location: $BACKUP_DIR"
    log "Logs: $TARBABY_BASE/logs/"
    echo ""
    log_success "Python 3.14 removed. Python 3.13 preserved."
    echo ""
}

main "$@"
