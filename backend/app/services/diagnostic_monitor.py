"""
Diagnostic Monitor Service
Digital Utopia Platform

Service để monitor health status real-time và trigger alerts
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import asyncio
from collections import defaultdict

from ..models.diagnostics import TradingDiagnosticReport
from ..models.alert_rules import AlertRule, AlertHistory
from ..db.redis_client import RedisCache

logger = logging.getLogger(__name__)


class DiagnosticMonitor:
    """
    Service để monitor diagnostic health và trigger alerts
    
    Features:
    - Continuous health monitoring với configurable intervals
    - Health status change detection
    - Automatic alert triggering khi detect issues
    - Track health trends over time
    """
    
    def __init__(self, db: Session, cache: Optional[RedisCache] = None):
        """
        Khởi tạo DiagnosticMonitor
        
        Args:
            db: SQLAlchemy session
            cache: Redis cache client (optional)
        """
        self.db = db
        self.cache = cache
        self.monitoring_intervals = {}  # {user_id: interval_seconds}
        self.last_health_status = {}  # {user_id: health_status}
        self.error_counts = defaultdict(int)  # Track error counts for thresholds
        
    def check_health_status(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Kiểm tra health status hiện tại
        
        Args:
            user_id: ID của user (None cho system-wide check)
            
        Returns:
            Dict với health status và issues detected
        """
        try:
            # Lấy diagnostic report mới nhất
            query = self.db.query(TradingDiagnosticReport)
            if user_id:
                query = query.filter(TradingDiagnosticReport.user_id == user_id)
            else:
                # System-wide: lấy report mới nhất của bất kỳ user nào
                query = query.order_by(TradingDiagnosticReport.created_at.desc())
            
            latest_report = query.first()
            
            if not latest_report:
                return {
                    'status': 'unknown',
                    'has_issues': False,
                    'issues': [],
                    'timestamp': datetime.utcnow().isoformat(),
                }
            
            # Phân tích health status
            health_status = latest_report.overall_health or 'unknown'
            has_issues = health_status in ['degraded', 'unhealthy']
            
            issues = []
            
            # Check auth issues
            if latest_report.auth_status:
                auth = latest_report.auth_status
                if not auth.get('hasToken'):
                    issues.append({
                        'type': 'auth',
                        'severity': 'high',
                        'message': 'No authentication token found',
                    })
                elif auth.get('isExpired'):
                    issues.append({
                        'type': 'auth',
                        'severity': 'high',
                        'message': 'Authentication token expired',
                    })
            
            # Check API issues
            if latest_report.api_status:
                api = latest_report.api_status
                if api.get('overallHealth') == 'unhealthy':
                    issues.append({
                        'type': 'api',
                        'severity': 'critical',
                        'message': 'All API endpoints are unhealthy',
                    })
                elif api.get('overallHealth') == 'degraded':
                    issues.append({
                        'type': 'api',
                        'severity': 'medium',
                        'message': 'Some API endpoints are failing',
                    })
                
                # Check specific API errors
                api_errors = api.get('errors', [])
                if api_errors:
                    error_count = len(api_errors)
                    issues.append({
                        'type': 'api_errors',
                        'severity': 'medium',
                        'message': f'{error_count} API endpoint(s) failed',
                        'error_count': error_count,
                    })
            
            # Check WebSocket issues
            if latest_report.ws_status:
                ws = latest_report.ws_status
                if not ws.get('connected'):
                    issues.append({
                        'type': 'websocket',
                        'severity': 'medium',
                        'message': 'WebSocket connection lost',
                    })
            
            # Check component empty states
            if latest_report.component_status:
                empty_components = []
                for comp_name, comp_status in latest_report.component_status.items():
                    if isinstance(comp_status, dict) and comp_status.get('isEmpty'):
                        empty_components.append(comp_name)
                
                if empty_components:
                    issues.append({
                        'type': 'components',
                        'severity': 'medium',
                        'message': f'Empty components: {", ".join(empty_components)}',
                        'components': empty_components,
                    })
            
            # Check recommendations
            recommendations = latest_report.recommendations or []
            critical_recommendations = [
                r for r in recommendations 
                if isinstance(r, dict) and r.get('severity') == 'high'
            ]
            
            if critical_recommendations:
                issues.append({
                    'type': 'recommendations',
                    'severity': 'high',
                    'message': f'{len(critical_recommendations)} critical recommendations',
                    'count': len(critical_recommendations),
                })
            
            return {
                'status': health_status,
                'has_issues': has_issues,
                'issues': issues,
                'report_id': latest_report.id,
                'timestamp': latest_report.created_at.isoformat() if latest_report.created_at else datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error checking health status: {e}", exc_info=True)
            return {
                'status': 'error',
                'has_issues': True,
                'issues': [{
                    'type': 'monitor_error',
                    'severity': 'high',
                    'message': f'Error checking health: {str(e)}',
                }],
                'timestamp': datetime.utcnow().isoformat(),
            }
    
    def detect_health_change(
        self, 
        user_id: Optional[int], 
        current_status: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Phát hiện thay đổi health status
        
        Args:
            user_id: ID của user
            current_status: Current health status từ check_health_status
            
        Returns:
            Dict với change information nếu có thay đổi, None nếu không
        """
        cache_key = f"diagnostic:last_health:{user_id or 'system'}"
        last_status = None
        
        # Get last status from cache or memory
        if self.cache:
            try:
                cached = self.cache.get(cache_key)
                if cached:
                    last_status = cached
            except:
                pass
        
        if not last_status:
            last_status = self.last_health_status.get(user_id)
        
        # Check for changes
        if last_status:
            last_health = last_status.get('status')
            current_health = current_status.get('status')
            
            if last_health != current_health:
                # Health status changed
                change = {
                    'type': 'health_change',
                    'from': last_health,
                    'to': current_health,
                    'timestamp': current_status.get('timestamp'),
                    'issues': current_status.get('issues', []),
                }
                
                # Save current status
                if self.cache:
                    try:
                        self.cache.set(cache_key, current_status, ttl=3600)  # 1 hour
                    except:
                        pass
                self.last_health_status[user_id] = current_status
                
                return change
        
        # Save current status even if no change
        if self.cache:
            try:
                self.cache.set(cache_key, current_status, ttl=3600)
            except:
                pass
        self.last_health_status[user_id] = current_status
        
        return None
    
    def evaluate_alert_rules(
        self,
        health_status: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Đánh giá alert rules và trả về rules nào đã được trigger
        
        Args:
            health_status: Health status từ check_health_status
            user_id: ID của user (None cho system-wide)
            
        Returns:
            List of alert rules that should be triggered
        """
        try:
            # Get enabled alert rules
            query = self.db.query(AlertRule).filter(AlertRule.enabled == True)
            
            # Filter by user_id if provided, or get system-wide rules (user_id is None)
            if user_id:
                query = query.filter(
                    (AlertRule.user_id == user_id) | (AlertRule.user_id.is_(None))
                )
            else:
                query = query.filter(AlertRule.user_id.is_(None))
            
            rules = query.order_by(AlertRule.priority.desc()).all()
            
            triggered_rules = []
            
            for rule in rules:
                if self._evaluate_rule(rule, health_status):
                    triggered_rules.append({
                        'rule': rule,
                        'health_status': health_status,
                        'conditions_met': self._get_conditions_met(rule, health_status),
                    })
            
            return triggered_rules
            
        except Exception as e:
            logger.error(f"Error evaluating alert rules: {e}", exc_info=True)
            return []
    
    def _evaluate_rule(self, rule: AlertRule, health_status: Dict[str, Any]) -> bool:
        """
        Đánh giá một alert rule có được trigger không
        
        Args:
            rule: AlertRule instance
            health_status: Current health status
            
        Returns:
            True nếu rule should be triggered
        """
        conditions = rule.conditions or {}
        thresholds = rule.thresholds or {}
        
        # Check health status condition
        if 'health_status' in conditions:
            required_status = conditions['health_status']
            current_status = health_status.get('status')
            if current_status != required_status:
                return False
        
        # Check API errors condition
        if 'api_errors' in conditions:
            required_error_count = conditions.get('api_errors', {}).get('min_count', 0)
            issues = health_status.get('issues', [])
            api_error_issues = [i for i in issues if i.get('type') == 'api_errors']
            if api_error_issues:
                error_count = api_error_issues[0].get('error_count', 0)
                if error_count < required_error_count:
                    return False
        
        # Check WebSocket disconnect condition
        if 'ws_disconnect' in conditions and conditions['ws_disconnect']:
            issues = health_status.get('issues', [])
            ws_issues = [i for i in issues if i.get('type') == 'websocket']
            if not ws_issues:
                return False
        
        # Check component empty condition
        if 'component_empty' in conditions:
            required_components = conditions.get('component_empty', [])
            if required_components:
                issues = health_status.get('issues', [])
                component_issues = [i for i in issues if i.get('type') == 'components']
                if component_issues:
                    empty_components = component_issues[0].get('components', [])
                    # Check if any required component is empty
                    if not any(comp in empty_components for comp in required_components):
                        return False
                else:
                    return False
        
        # Check thresholds
        if 'error_count' in thresholds:
            min_errors = thresholds.get('error_count', 0)
            if len(health_status.get('issues', [])) < min_errors:
                return False
        
        if 'duration_seconds' in thresholds:
            # This would require tracking when issue started
            # For now, we'll skip this check
            pass
        
        return True
    
    def _get_conditions_met(self, rule: AlertRule, health_status: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lấy thông tin về conditions đã được thỏa mãn
        
        Args:
            rule: AlertRule instance
            health_status: Current health status
            
        Returns:
            Dict với conditions met
        """
        conditions_met = {}
        
        conditions = rule.conditions or {}
        
        if 'health_status' in conditions:
            conditions_met['health_status'] = health_status.get('status')
        
        issues = health_status.get('issues', [])
        
        if 'api_errors' in conditions:
            api_error_issues = [i for i in issues if i.get('type') == 'api_errors']
            if api_error_issues:
                conditions_met['api_errors'] = api_error_issues[0].get('error_count', 0)
        
        if 'ws_disconnect' in conditions:
            ws_issues = [i for i in issues if i.get('type') == 'websocket']
            conditions_met['ws_disconnect'] = len(ws_issues) > 0
        
        if 'component_empty' in conditions:
            component_issues = [i for i in issues if i.get('type') == 'components']
            if component_issues:
                conditions_met['component_empty'] = component_issues[0].get('components', [])
        
        return conditions_met
    
    def record_alert_triggered(
        self,
        rule: AlertRule,
        health_status: Dict[str, Any],
        conditions_met: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> AlertHistory:
        """
        Ghi lại alert đã được trigger
        
        Args:
            rule: AlertRule instance
            health_status: Health status khi trigger
            conditions_met: Conditions đã được thỏa mãn
            user_id: ID của user liên quan
            
        Returns:
            AlertHistory instance
        """
        # Determine severity from rule thresholds or health status
        severity = 'medium'
        thresholds = rule.thresholds or {}
        if 'severity_level' in thresholds:
            severity = thresholds['severity_level']
        elif health_status.get('status') == 'unhealthy':
            severity = 'high'
        elif health_status.get('status') == 'degraded':
            severity = 'medium'
        
        alert_history = AlertHistory(
            alert_rule_id=rule.id,
            user_id=user_id,
            triggered_at=datetime.utcnow(),
            conditions_met=conditions_met,
            severity=severity,
        )
        
        self.db.add(alert_history)
        self.db.commit()
        self.db.refresh(alert_history)
        
        logger.info(f"Alert triggered: rule_id={rule.id}, user_id={user_id}, severity={severity}")
        
        # Send WebSocket notification if available
        if WS_AVAILABLE and user_id:
            try:
                import asyncio
                message = {
                    'type': 'alert',
                    'id': alert_history.id,
                    'alert_rule_id': rule.id,
                    'severity': severity,
                    'title': f"Alert: {rule.name}",
                    'message': f"Alert rule '{rule.name}' triggered",
                    'timestamp': alert_history.triggered_at.isoformat() if alert_history.triggered_at else datetime.utcnow().isoformat(),
                    'conditions_met': conditions_met,
                }
                # Use asyncio to send message
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(ws_manager.send_personal_message(message, user_id, 'diagnostics'))
                else:
                    asyncio.run(ws_manager.send_personal_message(message, user_id, 'diagnostics'))
            except Exception as e:
                logger.error(f"Error sending WebSocket alert: {e}", exc_info=True)
        
        return alert_history

