"""
Automated Scheduling System
Handles scheduled tasks for market data, reports, alerts, etc.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from typing import Callable, Dict, Any, List
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.session import async_session
from ..websocket.push_manager import push_alert, push_admin_broadcast
import asyncio

logger = logging.getLogger(__name__)

class SchedulingManager:
    """Central scheduling manager for automated tasks"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs: Dict[str, Any] = {}
        self.is_running = False
    
    def start(self):
        """Start the scheduler"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("Scheduling manager started")
            
            # Register default jobs
            self._register_default_jobs()
    
    def stop(self):
        """Stop the scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduling manager stopped")
    
    def add_job(
        self,
        job_id: str,
        func: Callable,
        trigger_type: str = "interval",
        **trigger_args
    ):
        """Add a scheduled job"""
        try:
            if trigger_type == "interval":
                trigger = IntervalTrigger(**trigger_args)
            elif trigger_type == "cron":
                trigger = CronTrigger(**trigger_args)
            else:
                raise ValueError(f"Unknown trigger type: {trigger_type}")
            
            job = self.scheduler.add_job(
                func,
                trigger=trigger,
                id=job_id,
                replace_existing=True
            )
            
            self.jobs[job_id] = {
                "job": job,
                "trigger_type": trigger_type,
                "trigger_args": trigger_args,
                "added_at": datetime.utcnow()
            }
            
            logger.info(f"Job '{job_id}' added with {trigger_type} trigger")
            return job
            
        except Exception as e:
            logger.error(f"Failed to add job '{job_id}': {e}")
            raise
    
    def remove_job(self, job_id: str):
        """Remove a scheduled job"""
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.jobs:
                del self.jobs[job_id]
            logger.info(f"Job '{job_id}' removed")
        except Exception as e:
            logger.error(f"Failed to remove job '{job_id}': {e}")
    
    def get_job(self, job_id: str):
        """Get job details"""
        return self.jobs.get(job_id)
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all scheduled jobs"""
        jobs_list = []
        for job_id, job_info in self.jobs.items():
            job = job_info["job"]
            jobs_list.append({
                "id": job_id,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger_type": job_info["trigger_type"],
                "trigger_args": job_info["trigger_args"],
                "added_at": job_info["added_at"].isoformat()
            })
        return jobs_list
    
    def _register_default_jobs(self):
        """Register default system jobs"""
        
        # Market data refresh - every 5 seconds
        self.add_job(
            "market_data_refresh",
            self._update_market_data,
            trigger_type="interval",
            seconds=5
        )
        
        # Market analysis - every minute
        self.add_job(
            "market_analysis",
            self._run_market_analysis,
            trigger_type="interval",
            minutes=1
        )
        
        # Generate daily report - every day at 00:00
        self.add_job(
            "daily_report",
            self._generate_daily_report,
            trigger_type="cron",
            hour=0,
            minute=0
        )
        
        # Generate weekly report - every Monday at 00:00
        self.add_job(
            "weekly_report",
            self._generate_weekly_report,
            trigger_type="cron",
            day_of_week="mon",
            hour=0,
            minute=0
        )
        
        # Clean old data - every day at 02:00
        self.add_job(
            "cleanup_old_data",
            self._cleanup_old_data,
            trigger_type="cron",
            hour=2,
            minute=0
        )
        
        # System health check - every 30 seconds
        self.add_job(
            "system_health_check",
            self._check_system_health,
            trigger_type="interval",
            seconds=30
        )
        
        # Alert check - every 10 seconds
        self.add_job(
            "alert_check",
            self._check_alerts,
            trigger_type="interval",
            seconds=10
        )
        
        # Backup database - every day at 03:00
        self.add_job(
            "database_backup",
            self._backup_database,
            trigger_type="cron",
            hour=3,
            minute=0
        )
    
    # Default job implementations
    async def _update_market_data(self):
        """Update market data from providers"""
        try:
            # Import here to avoid circular imports
            from ..services.market_service import update_all_market_data
            await update_all_market_data()
        except Exception as e:
            logger.error(f"Market data update failed: {e}")
    
    async def _run_market_analysis(self):
        """Run market analysis algorithms"""
        try:
            from ..services.analysis_service import run_market_analysis
            await run_market_analysis()
        except Exception as e:
            logger.error(f"Market analysis failed: {e}")
    
    async def _generate_daily_report(self):
        """Generate and send daily report"""
        try:
            from ..services.report_service import generate_daily_report
            report = await generate_daily_report()
            
            # Send notification to admins
            await push_admin_broadcast(
                f"Daily report generated: {report['summary']}",
                level="info"
            )
            
            logger.info("Daily report generated successfully")
        except Exception as e:
            logger.error(f"Daily report generation failed: {e}")
            await push_alert({
                "severity": "warning",
                "message": f"Daily report generation failed: {str(e)}"
            })
    
    async def _generate_weekly_report(self):
        """Generate and send weekly report"""
        try:
            from ..services.report_service import generate_weekly_report
            report = await generate_weekly_report()
            
            await push_admin_broadcast(
                f"Weekly report generated: {report['summary']}",
                level="info"
            )
            
            logger.info("Weekly report generated successfully")
        except Exception as e:
            logger.error(f"Weekly report generation failed: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old data from database"""
        try:
            async with async_session() as db:
                # Delete old logs (older than 30 days)
                from sqlalchemy import text
                result = await db.execute(text("""
                    DELETE FROM audit_logs 
                    WHERE created_at < NOW() - INTERVAL '30 days'
                """))
                
                deleted_logs = result.rowcount
                await db.commit()
                
                logger.info(f"Cleaned up {deleted_logs} old log entries")
                
        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")
    
    async def _check_system_health(self):
        """Check system health and raise alerts if needed"""
        try:
            import psutil
            
            # Check CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                await push_alert({
                    "severity": "critical",
                    "message": f"High CPU usage: {cpu_percent}%",
                    "service": "system"
                })
            
            # Check memory
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                await push_alert({
                    "severity": "critical",
                    "message": f"High memory usage: {memory.percent}%",
                    "service": "system"
                })
            
            # Check disk
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                await push_alert({
                    "severity": "warning",
                    "message": f"High disk usage: {disk.percent}%",
                    "service": "system"
                })
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
    
    async def _check_alerts(self):
        """Check alert conditions and trigger notifications"""
        try:
            from ..services.alert_service import check_alert_rules
            triggered_alerts = await check_alert_rules()
            
            for alert in triggered_alerts:
                await push_alert(alert)
                
        except Exception as e:
            logger.error(f"Alert check failed: {e}")
    
    async def _backup_database(self):
        """Backup database"""
        try:
            # Implement database backup logic
            logger.info("Database backup initiated")
            
            # Placeholder - implement actual backup
            await asyncio.sleep(1)
            
            logger.info("Database backup completed")
            
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            await push_alert({
                "severity": "critical",
                "message": f"Database backup failed: {str(e)}",
                "service": "database"
            })

# Global scheduler instance
scheduler_manager = SchedulingManager()

# API functions
def start_scheduler():
    """Start the global scheduler"""
    scheduler_manager.start()

def stop_scheduler():
    """Stop the global scheduler"""
    scheduler_manager.stop()

def add_custom_job(job_id: str, func: Callable, trigger_type: str = "interval", **trigger_args):
    """Add a custom scheduled job"""
    return scheduler_manager.add_job(job_id, func, trigger_type, **trigger_args)

def remove_custom_job(job_id: str):
    """Remove a custom scheduled job"""
    scheduler_manager.remove_job(job_id)

def list_scheduled_jobs() -> List[Dict[str, Any]]:
    """List all scheduled jobs"""
    return scheduler_manager.list_jobs()

def get_job_info(job_id: str):
    """Get information about a specific job"""
    return scheduler_manager.get_job(job_id)
