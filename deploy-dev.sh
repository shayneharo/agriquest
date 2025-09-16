#!/bin/bash

# AgriQuest Development Deployment Script
# Quick deployment for development and testing

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Banner
print_banner() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🚀 AgriQuest Dev Deploy 🚀              ║"
    echo "║              Development Deployment Script                   ║"
    echo "║                                                              ║"
    echo "║  This script will deploy AgriQuest for development          ║"
    echo "║  with all features enabled for testing                      ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed. Please install Python 3 first."
    fi
    
    # Check if pip is installed
    if ! command -v pip3 &> /dev/null; then
        error "pip3 is not installed. Please install pip3 first."
    fi
    
    log "Prerequisites check completed ✅"
}

# Install dependencies
install_dependencies() {
    log "Installing Python dependencies..."
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
    else
        warn "requirements.txt not found, installing basic dependencies..."
        pip3 install flask werkzeug
    fi
    
    log "Dependencies installed ✅"
}

# Setup environment
setup_environment() {
    log "Setting up development environment..."
    
    # Create necessary directories
    mkdir -p uploads/profile_pictures
    mkdir -p logs
    
    # Set environment variables
    export FLASK_APP=app.py
    export FLASK_ENV=development
    
    log "Environment setup completed ✅"
}

# Initialize database
initialize_database() {
    log "Initializing database..."
    
    # Check if database exists
    if [ ! -f "agriquest.db" ]; then
        info "Creating new database..."
        python3 -c "
from backend.config.database import init_db
init_db()
print('Database initialized successfully')
"
    else
        info "Database already exists, skipping initialization"
    fi
    
    log "Database ready ✅"
}

# Start development server
start_server() {
    log "Starting development server..."
    
    info "Starting AgriQuest in development mode..."
    info "Press Ctrl+C to stop the server"
    
    # Start the Flask development server
    python3 run.py
}

# Main function
main() {
    print_banner
    
    check_prerequisites
    install_dependencies
    setup_environment
    initialize_database
    start_server
}

# Run main function
main "$@"

