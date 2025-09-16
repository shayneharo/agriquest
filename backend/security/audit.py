"""
Audit Logging System
Comprehensive security and activity logging
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from enum import Enum
from flask import request, current_app
import hashlib

logger = logging.getLogger(__name__)

class AuditEventType(Enum):
    """Types of audit events"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_EVENT = "system_event"
    SECURITY_EVENT = "security_event"
    USER_ACTION = "user_action"
    ADMIN_ACTION = "admin_action"

class AuditSeverity(Enum):
    """Audit event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditLogger:
    """Comprehensive audit logging system"""
    
    def __init__(self):
        self.audit_logger = logging.getLogger('audit')
        self.audit_logger.setLevel(logging.INFO)
        
        # Create audit log handler
        handler = logging.FileHandler('logs/audit.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.audit_logger.addHandler(handler)
        
        # Prevent duplicate logs
        self.audit_logger.propagate = False
    
    def log_event(self, 
                  event_type: AuditEventType,
                  severity: AuditSeverity,
                  user_id: Optional[int],
                  action: str,
                  details: Dict[str, Any],
                  ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None,
                  success: bool = True,
                  error_message: Optional[str] = None):
        """Log audit event with comprehensive details"""
        
        # Get request context if available
        if not ip_address and request:
            ip_address = request.remote_addr
        if not user_agent and request:
            user_agent = request.headers.get('User-Agent', '')
        
        # Create audit record
        audit_record = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type.value,
            'severity': severity.value,
            'user_id': user_id,
            'action': action,
            'details': details,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'success': success,
            'error_message': error_message,
            'session_id': self._get_session_id(),
            'request_id': self._get_request_id()
        }
        
        # Log to file
        log_message = json.dumps(audit_record, default=str)
        
        if severity == AuditSeverity.CRITICAL:
            self.audit_logger.critical(log_message)
        elif severity == AuditSeverity.HIGH:
            self.audit_logger.error(log_message)
        elif severity == AuditSeverity.MEDIUM:
            self.audit_logger.warning(log_message)
        else:
            self.audit_logger.info(log_message)
        
        # Store in database for analysis
        self._store_audit_record(audit_record)
        
        # Send alerts for critical events
        if severity == AuditSeverity.CRITICAL:
            self._send_security_alert(audit_record)
    
    def log_authentication(self, user_id: Optional[int], action: str, success: bool, 
                          details: Dict[str, Any], error_message: Optional[str] = None):
        """Log authentication events"""
        severity = AuditSeverity.HIGH if not success else AuditSeverity.MEDIUM
        self.log_event(
            AuditEventType.AUTHENTICATION,
            severity,
            user_id,
            action,
            details,
            success=success,
            error_message=error_message
        )
    
    def log_authorization(self, user_id: int, action: str, resource: str, 
                         success: bool, details: Dict[str, Any]):
        """Log authorization events"""
        severity = AuditSeverity.HIGH if not success else AuditSeverity.LOW
        details['resource'] = resource
        self.log_event(
            AuditEventType.AUTHORIZATION,
            severity,
            user_id,
            action,
            details,
            success=success
        )
    
    def log_data_access(self, user_id: int, action: str, resource_type: str, 
                       resource_id: Optional[int], details: Dict[str, Any]):
        """Log data access events"""
        details['resource_type'] = resource_type
        details['resource_id'] = resource_id
        self.log_event(
            AuditEventType.DATA_ACCESS,
            AuditSeverity.LOW,
            user_id,
            action,
            details
        )
    
    def log_data_modification(self, user_id: int, action: str, resource_type: str, 
                             resource_id: Optional[int], old_data: Dict[str, Any], 
                             new_data: Dict[str, Any]):
        """Log data modification events"""
        details = {
            'resource_type': resource_type,
            'resource_id': resource_id,
            'old_data': old_data,
            'new_data': new_data,
            'changes': self._calculate_changes(old_data, new_data)
        }
        self.log_event(
            AuditEventType.DATA_MODIFICATION,
            AuditSeverity.MEDIUM,
            user_id,
            action,
            details
        )
    
    def log_security_event(self, event_type: str, severity: AuditSeverity, 
                          details: Dict[str, Any], user_id: Optional[int] = None):
        """Log security-related events"""
        self.log_event(
            AuditEventType.SECURITY_EVENT,
            severity,
            user_id,
            event_type,
            details
        )
    
    def log_admin_action(self, admin_id: int, action: str, target_user_id: Optional[int], 
                        details: Dict[str, Any]):
        """Log administrative actions"""
        details['target_user_id'] = target_user_id
        self.log_event(
            AuditEventType.ADMIN_ACTION,
            AuditSeverity.HIGH,
            admin_id,
            action,
            details
        )
    
    def log_system_event(self, event_type: str, severity: AuditSeverity, 
                        details: Dict[str, Any]):
        """Log system events"""
        self.log_event(
            AuditEventType.SYSTEM_EVENT,
            severity,
            None,
            event_type,
            details
        )
    
    def _get_session_id(self) -> Optional[str]:
        """Get current session ID"""
        try:
            from flask import session
            return session.get('session_id')
        except:
            return None
    
    def _get_request_id(self) -> str:
        """Generate unique request ID"""
        request_data = f"{request.remote_addr}:{request.method}:{request.path}:{time.time()}"
        return hashlib.md5(request_data.encode()).hexdigest()[:16]
    
    def _calculate_changes(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate changes between old and new data"""
        changes = {}
        
        # Find modified fields
        for key in set(old_data.keys()) | set(new_data.keys()):
            old_value = old_data.get(key)
            new_value = new_data.get(key)
            
            if old_value != new_value:
                changes[key] = {
                    'old': old_value,
                    'new': new_value
                }
        
        return changes
    
    def _store_audit_record(self, audit_record: Dict[str, Any]):
        """Store audit record in database"""
        try:
            from config.database_optimized import db_manager
            
            db_manager.execute_query(
                """INSERT INTO audit_logs (timestamp, event_type, severity, user_id, action, 
                   details, ip_address, user_agent, success, error_message, session_id, request_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    audit_record['timestamp'],
                    audit_record['event_type'],
                    audit_record['severity'],
                    audit_record['user_id'],
                    audit_record['action'],
                    json.dumps(audit_record['details']),
                    audit_record['ip_address'],
                    audit_record['user_agent'],
                    audit_record['success'],
                    audit_record['error_message'],
                    audit_record['session_id'],
                    audit_record['request_id']
                )
            )
        except Exception as e:
            logger.error(f"Failed to store audit record: {e}")
    
    def _send_security_alert(self, audit_record: Dict[str, Any]):
        """Send security alert for critical events"""
        try:
            # In production, integrate with alerting system (email, Slack, etc.)
            logger.critical(f"SECURITY ALERT: {audit_record['action']} - {audit_record['details']}")
            
            # Example: Send email alert
            # send_security_alert_email(audit_record)
            
        except Exception as e:
            logger.error(f"Failed to send security alert: {e}")
    
    def get_audit_logs(self, user_id: Optional[int] = None, 
                      event_type: Optional[AuditEventType] = None,
                      severity: Optional[AuditSeverity] = None,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve audit logs with filtering"""
        try:
            from config.database_optimized import db_manager
            
            query = "SELECT * FROM audit_logs WHERE 1=1"
            params = []
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type.value)
            
            if severity:
                query += " AND severity = ?"
                params.append(severity.value)
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date.isoformat())
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            results = db_manager.execute_query(query, tuple(params), fetch='all')
            
            # Parse JSON details
            for result in results:
                if result.get('details'):
                    try:
                        result['details'] = json.loads(result['details'])
                    except:
                        pass
            
            return [dict(result) for result in results]
            
        except Exception as e:
            logger.error(f"Failed to retrieve audit logs: {e}")
            return []
    
    def generate_security_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate security report for specified period"""
        try:
            from config.database_optimized import db_manager
            
            # Get security events
            security_events = db_manager.execute_query(
                """SELECT event_type, severity, COUNT(*) as count
                   FROM audit_logs 
                   WHERE timestamp BETWEEN ? AND ? 
                   AND event_type IN ('authentication', 'authorization', 'security_event')
                   GROUP BY event_type, severity""",
                (start_date.isoformat(), end_date.isoformat()),
                fetch='all'
            )
            
            # Get failed login attempts
            failed_logins = db_manager.execute_query(
                """SELECT COUNT(*) as count
                   FROM audit_logs 
                   WHERE timestamp BETWEEN ? AND ? 
                   AND event_type = 'authentication' 
                   AND success = FALSE""",
                (start_date.isoformat(), end_date.isoformat()),
                fetch='one'
            )
            
            # Get suspicious IPs
            suspicious_ips = db_manager.execute_query(
                """SELECT ip_address, COUNT(*) as count
                   FROM audit_logs 
                   WHERE timestamp BETWEEN ? AND ? 
                   AND success = FALSE
                   GROUP BY ip_address
                   HAVING COUNT(*) > 5
                   ORDER BY COUNT(*) DESC""",
                (start_date.isoformat(), end_date.isoformat()),
                fetch='all'
            )
            
            return {
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'security_events': [dict(event) for event in security_events],
                'failed_logins': failed_logins['count'] if failed_logins else 0,
                'suspicious_ips': [dict(ip) for ip in suspicious_ips],
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate security report: {e}")
            return {}

# Global audit logger instance
audit_logger = AuditLogger()

# Audit logging decorators
def audit_log(event_type: AuditEventType, severity: AuditSeverity = AuditSeverity.LOW):
    """Decorator to automatically log function execution"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = getattr(request, 'current_user', {}).get('user_id') if request else None
            
            # Log function start
            audit_logger.log_event(
                event_type,
                severity,
                user_id,
                f"{f.__name__}_started",
                {'function': f.__name__, 'args': str(args), 'kwargs': str(kwargs)}
            )
            
            try:
                result = f(*args, **kwargs)
                
                # Log successful completion
                audit_logger.log_event(
                    event_type,
                    severity,
                    user_id,
                    f"{f.__name__}_completed",
                    {'function': f.__name__, 'result_type': type(result).__name__}
                )
                
                return result
                
            except Exception as e:
                # Log error
                audit_logger.log_event(
                    event_type,
                    AuditSeverity.HIGH,
                    user_id,
                    f"{f.__name__}_failed",
                    {'function': f.__name__, 'error': str(e)},
                    success=False,
                    error_message=str(e)
                )
                raise
        
        return decorated_function
    return decorator

def log_authentication(f):
    """Decorator for authentication logging"""
    return audit_log(AuditEventType.AUTHENTICATION, AuditSeverity.MEDIUM)(f)

def log_authorization(f):
    """Decorator for authorization logging"""
    return audit_log(AuditEventType.AUTHORIZATION, AuditSeverity.LOW)(f)

def log_data_access(f):
    """Decorator for data access logging"""
    return audit_log(AuditEventType.DATA_ACCESS, AuditSeverity.LOW)(f)

def log_data_modification(f):
    """Decorator for data modification logging"""
    return audit_log(AuditEventType.DATA_MODIFICATION, AuditSeverity.MEDIUM)(f)

def log_admin_action(f):
    """Decorator for admin action logging"""
    return audit_log(AuditEventType.ADMIN_ACTION, AuditSeverity.HIGH)(f)

def log_security_event(f):
    """Decorator for security event logging"""
    return audit_log(AuditEventType.SECURITY_EVENT, AuditSeverity.HIGH)(f)

