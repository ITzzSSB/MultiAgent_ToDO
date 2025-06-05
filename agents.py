import uuid
from datetime import datetime, timedelta
import json

class PlannerAgent:
    """Agent responsible for creating and planning tasks"""
    
    def __init__(self):
        self.name = "Planner"
    
    def create_task(self, title, description, priority, due_date):
        """Create a new task with basic planning logic"""
        task = {
            'id': str(uuid.uuid4()),
            'title': title,
            'description': description,
            'priority': priority,
            'due_date': due_date.isoformat(),
            'created_date': datetime.now().isoformat(),
            'status': 'pending',
            'estimated_duration': self._estimate_duration(title, description),
            'tags': self._extract_tags(title, description)
        }
        return task
    
    def _estimate_duration(self, title, description):
        """Simple duration estimation based on content length"""
        content_length = len(title) + len(description)
        if content_length < 50:
            return 30  # 30 minutes
        elif content_length < 100:
            return 60  # 1 hour
        else:
            return 120  # 2 hours
    
    def _extract_tags(self, title, description):
        """Extract simple tags from task content"""
        common_tags = ['meeting', 'call', 'email', 'report', 'review', 'urgent', 'important']
        content = (title + ' ' + description).lower()
        found_tags = [tag for tag in common_tags if tag in content]
        return found_tags

class SchedulerAgent:
    """Agent responsible for scheduling and optimizing tasks"""
    
    def __init__(self):
        self.name = "Scheduler"
    
    def schedule_task(self, task):
        """Add scheduling intelligence to task"""
        task['scheduled_time'] = self._calculate_optimal_time(task)
        task['preparation_time'] = self._calculate_prep_time(task)
        task['buffer_time'] = 15  # 15 minutes buffer
        return task
    
    def optimize_schedule(self, tasks):
        """Optimize the schedule of multiple tasks"""
        # Sort by priority and due date
        pending_tasks = [t for t in tasks if t['status'] == 'pending']
        
        # Priority scoring
        priority_scores = {'High': 3, 'Medium': 2, 'Low': 1}
        
        for task in pending_tasks:
            # Calculate urgency score
            due_date = datetime.fromisoformat(task['due_date'])
            days_until_due = (due_date - datetime.now()).days
            
            urgency_score = max(1, 5 - days_until_due)  # More urgent = higher score
            priority_score = priority_scores[task['priority']]
            
            task['optimization_score'] = urgency_score + priority_score
        
        # Sort by optimization score
        pending_tasks.sort(key=lambda x: x.get('optimization_score', 0), reverse=True)
        
        return tasks
    
    def _calculate_optimal_time(self, task):
        """Calculate optimal time to work on task"""
        due_date = datetime.fromisoformat(task['due_date'])
        
        # If high priority, schedule earlier
        if task['priority'] == 'High':
            optimal_time = due_date - timedelta(hours=2)
        elif task['priority'] == 'Medium':
            optimal_time = due_date - timedelta(hours=1)
        else:
            optimal_time = due_date - timedelta(minutes=30)
        
        return optimal_time.isoformat()
    
    def _calculate_prep_time(self, task):
        """Calculate preparation time needed"""
        if 'meeting' in task.get('tags', []):
            return 15  # 15 minutes prep for meetings
        elif 'report' in task.get('tags', []):
            return 30  # 30 minutes prep for reports
        else:
            return 5   # 5 minutes general prep

class ReminderAgent:
    """Agent responsible for managing reminders and notifications"""
    
    def __init__(self):
        self.name = "Reminder"
        self.reminder_thresholds = {
            'High': [timedelta(hours=2), timedelta(hours=1), timedelta(minutes=30)],
            'Medium': [timedelta(hours=1), timedelta(minutes=30)],
            'Low': [timedelta(minutes=30)]
        }
    
    def check_reminders(self, tasks):
        """Check which tasks need reminders"""
        reminders = []
        current_time = datetime.now()
        
        for task in tasks:
            if task['status'] == 'completed':
                continue
                
            due_date = datetime.fromisoformat(task['due_date'])
            time_until_due = due_date - current_time
            
            # Check if task is overdue
            if time_until_due.total_seconds() < 0:
                task['reminder_type'] = 'overdue'
                reminders.append(task)
                continue
            
            # Check reminder thresholds
            thresholds = self.reminder_thresholds.get(task['priority'], [timedelta(minutes=30)])
            
            for threshold in thresholds:
                if time_until_due <= threshold:
                    task['reminder_type'] = f"due_in_{threshold}"
                    if task not in reminders:
                        reminders.append(task)
                    break
        
        return reminders
    
    def create_reminder_message(self, task):
        """Create a formatted reminder message"""
        due_date = datetime.fromisoformat(task['due_date'])
        current_time = datetime.now()
        time_diff = due_date - current_time
        
        if time_diff.total_seconds() < 0:
            return f"⚠️ OVERDUE: '{task['title']}' was due {abs(time_diff)} ago!"
        else:
            return f"🔔 REMINDER: '{task['title']}' is due in {time_diff}!"
    
    def get_daily_summary(self, tasks):
        """Get daily task summary"""
        today = datetime.now().date()
        today_tasks = []
        
        for task in tasks:
            task_date = datetime.fromisoformat(task['due_date']).date()
            if task_date == today and task['status'] == 'pending':
                today_tasks.append(task)
        
        return {
            'total_today': len(today_tasks),
            'high_priority': len([t for t in today_tasks if t['priority'] == 'High']),
            'tasks': today_tasks
        }