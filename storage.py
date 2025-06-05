import json
import os
from typing import List, Dict, Optional

class TaskStorage:
    """Simple JSON-based storage for tasks"""
    
    def __init__(self, filename="tasks.json"):
        self.filename = filename
        self.tasks = self._load_tasks()
    
    def _load_tasks(self) -> List[Dict]:
        """Load tasks from JSON file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def _save_tasks(self):
        """Save tasks to JSON file"""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.tasks, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def add_task(self, task: Dict) -> bool:
        """Add a new task"""
        try:
            self.tasks.append(task)
            self._save_tasks()
            return True
        except Exception as e:
            print(f"Error adding task: {e}")
            return False
    
    def get_all_tasks(self) -> List[Dict]:
        """Get all tasks"""
        return self.tasks.copy()
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict]:
        """Get a specific task by ID"""
        for task in self.tasks:
            if task['id'] == task_id:
                return task.copy()
        return None
    
    def update_task(self, task_id: str, updated_task: Dict) -> bool:
        """Update an existing task"""
        try:
            for i, task in enumerate(self.tasks):
                if task['id'] == task_id:
                    self.tasks[i] = updated_task
                    self._save_tasks()
                    return True
            return False
        except Exception as e:
            print(f"Error updating task: {e}")
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        try:
            self.tasks = [task for task in self.tasks if task['id'] != task_id]
            self._save_tasks()
            return True
        except Exception as e:
            print(f"Error deleting task: {e}")
            return False
    
    def get_tasks_by_status(self, status: str) -> List[Dict]:
        """Get tasks filtered by status"""
        return [task for task in self.tasks if task['status'] == status]
    
    def get_tasks_by_priority(self, priority: str) -> List[Dict]:
        """Get tasks filtered by priority"""
        return [task for task in self.tasks if task['priority'] == priority]
    
    def get_overdue_tasks(self) -> List[Dict]:
        """Get overdue tasks"""
        from datetime import datetime
        current_time = datetime.now()
        overdue = []
        
        for task in self.tasks:
            if task['status'] != 'completed':
                due_date = datetime.fromisoformat(task['due_date'])
                if due_date < current_time:
                    overdue.append(task)
        
        return overdue
    
    def get_stats(self) -> Dict:
        """Get storage statistics"""
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks if t['status'] == 'completed'])
        pending_tasks = total_tasks - completed_tasks
        
        priority_counts = {'High': 0, 'Medium': 0, 'Low': 0}
        for task in self.tasks:
            if task['status'] != 'completed':
                priority_counts[task['priority']] += 1
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'priority_counts': priority_counts,
            'file_size': os.path.getsize(self.filename) if os.path.exists(self.filename) else 0
        }
    
    def backup_tasks(self, backup_filename: str = None) -> bool:
        """Create a backup of tasks"""
        if not backup_filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"tasks_backup_{timestamp}.json"
        
        try:
            with open(backup_filename, 'w') as f:
                json.dump(self.tasks, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def restore_from_backup(self, backup_filename: str) -> bool:
        """Restore tasks from backup"""
        try:
            with open(backup_filename, 'r') as f:
                self.tasks = json.load(f)
            self._save_tasks()
            return True
        except Exception as e:
            print(f"Error restoring from backup: {e}")
            return False