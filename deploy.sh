#!/bin/bash

# AgriQuest Production Deployment Script
# This script automates the deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="agriquest"
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
LOG_FILE="deployment.log"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a $LOG_FILE
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a $LOG_FILE
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a $LOG_FILE
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a $LOG_FILE
}

# Banner
print_banner() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🚀 AgriQuest Deployment 🚀              ║"
    echo "║              Production Deployment Script                    ║"
    echo "║                                                              ║"
    echo "║  This script will deploy AgriQuest to production            ║"
    echo "║  with all optimizations and monitoring enabled              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    # Check if .env.production exists
    if [ ! -f ".env.production" ]; then
        warn ".env.production not found. Creating from example..."
        if [ -f "env.production.example" ]; then
            cp env.production.example .env.production
            warn "Please edit .env.production with your actual values before continuing."
            warn "Press Enter when ready to continue..."
            read
        else
            error ".env.production not found and no example file available."
        fi
    fi
    
    log "Prerequisites check completed ✅"
}

# Create backup
create_backup() {
    log "Creating backup..."
    
    mkdir -p $BACKUP_DIR
    
    # Backup current database if exists
    if [ -f "agriquest.db" ]; then
        cp agriquest.db $BACKUP_DIR/
        log "Database backed up to $BACKUP_DIR/agriquest.db"
    fi
    
    # Backup current configuration
    if [ -f ".env.production" ]; then
        cp .env.production $BACKUP_DIR/
        log "Environment configuration backed up"
    fi
    
    # Backup uploads if exists
    if [ -d "uploads" ]; then
        cp -r uploads $BACKUP_DIR/
        log "Uploads backed up"
    fi
    
    log "Backup completed ✅"
}

# Generate secure keys
generate_keys() {
    log "Generating secure keys..."
    
    # Generate SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    
    # Generate JWT_SECRET_KEY
    JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    
    # Generate POSTGRES_PASSWORD
    POSTGRES_PASSWORD=$(python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16)))")
    
    # Update .env.production with generated keys
    sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env.production
    sed -i.bak "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET_KEY/" .env.production
    sed -i.bak "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" .env.production
    
    log "Secure keys generated and updated ✅"
}

# Setup SSL certificates
setup_ssl() {
    log "Setting up SSL certificates..."
    
    # Create SSL directory
    mkdir -p ssl
    
    # Check if certificates exist
    if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
        warn "SSL certificates not found. Creating self-signed certificates for development..."
        warn "For production, replace these with real certificates from Let's Encrypt or your CA."
        
        # Generate self-signed certificate
        openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        
        log "Self-signed SSL certificates created ✅"
    else
        log "SSL certificates found ✅"
    fi
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p uploads/profile_pictures
    mkdir -p logs
    mkdir -p backups
    mkdir -p ssl
    
    log "Directories created ✅"
}

# Build and start services
deploy_services() {
    log "Building and starting services..."
    
    # Stop any existing containers
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    
    # Build and start services
    docker-compose -f docker-compose.prod.yml up -d --build
    
    log "Services started ✅"
}

# Wait for services to be ready
wait_for_services() {
    log "Waiting for services to be ready..."
    
    # Wait for database
    info "Waiting for database..."
    timeout 60 bash -c 'until docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U agriquest -d agriquest; do sleep 2; done'
    
    # Wait for Redis
    info "Waiting for Redis..."
    timeout 30 bash -c 'until docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping; do sleep 2; done'
    
    # Wait for web application
    info "Waiting for web application..."
    timeout 60 bash -c 'until curl -f http://localhost:5000/health 2>/dev/null; do sleep 2; done'
    
    log "All services are ready ✅"
}

# Initialize database
initialize_database() {
    log "Initializing database..."
    
    # Run database initialization
    docker-compose -f docker-compose.prod.yml exec -T web python -c "
from backend.config.database_optimized import db_manager
try:
    db_manager._init_database()
    print('Database initialized successfully')
except Exception as e:
    print(f'Database initialization error: {e}')
    exit(1)
"
    
    log "Database initialized ✅"
}

# Run health checks
health_check() {
    log "Running health checks..."
    
    # Check web application
    if curl -f http://localhost:5000/health >/dev/null 2>&1; then
        log "Web application health check passed ✅"
    else
        error "Web application health check failed ❌"
    fi
    
    # Check database
    if docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U agriquest -d agriquest >/dev/null 2>&1; then
        log "Database health check passed ✅"
    else
        error "Database health check failed ❌"
    fi
    
    # Check Redis
    if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping >/dev/null 2>&1; then
        log "Redis health check passed ✅"
    else
        error "Redis health check failed ❌"
    fi
    
    log "All health checks passed ✅"
}

# Show deployment information
show_deployment_info() {
    log "Deployment completed successfully! 🎉"
    
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🎉 Deployment Complete! 🎉              ║"
    echo "║                                                              ║"
    echo "║  AgriQuest is now running in production mode!               ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${BLUE}🌐 Application Access:${NC}"
    echo "   📱 Local:    http://localhost:5000"
    echo "   🌍 Network:  http://$(hostname -I | awk '{print $1}'):5000"
    echo "   🔒 HTTPS:    https://localhost (if SSL configured)"
    echo ""
    
    echo -e "${BLUE}📊 Monitoring Dashboards:${NC}"
    echo "   📈 Grafana:  http://localhost:3000 (admin/admin)"
    echo "   📊 Prometheus: http://localhost:9090"
    echo ""
    
    echo -e "${BLUE}🔧 Management Commands:${NC}"
    echo "   📋 View logs:    docker-compose -f docker-compose.prod.yml logs -f"
    echo "   🛑 Stop:         docker-compose -f docker-compose.prod.yml down"
    echo "   🔄 Restart:      docker-compose -f docker-compose.prod.yml restart"
    echo "   📊 Status:       docker-compose -f docker-compose.prod.yml ps"
    echo ""
    
    echo -e "${BLUE}🔑 Test Accounts:${NC}"
    echo "   👨‍🏫 Teacher: username='teacher', password='Teacher123!'"
    echo "   🎓 Student:  username='student', password='Student123!'"
    echo ""
    
    echo -e "${YELLOW}⚠️  Important Notes:${NC}"
    echo "   🔒 Change default passwords in production"
    echo "   📧 Configure email settings in .env.production"
    echo "   📱 Configure SMS settings in .env.production"
    echo "   🌐 Update domain settings for production use"
    echo "   🔐 Replace self-signed SSL certificates with real ones"
    echo ""
    
    echo -e "${GREEN}✨ AgriQuest is ready for production use! ✨${NC}"
}

# Main deployment function
main() {
    print_banner
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        warn "Running as root. This is not recommended for production."
        warn "Consider running as a non-root user."
    fi
    
    # Start deployment process
    check_prerequisites
    create_backup
    generate_keys
    setup_ssl
    create_directories
    deploy_services
    wait_for_services
    initialize_database
    health_check
    show_deployment_info
    
    log "Deployment script completed successfully! 🎉"
}

# Run main function
main "$@"
