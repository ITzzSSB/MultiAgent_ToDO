import streamlit as st
import json
import os
from datetime import datetime, timedelta
from agents import PlannerAgent, SchedulerAgent, ReminderAgent
from storage import TaskStorage

# Initialize storage and agents
storage = TaskStorage()
planner = PlannerAgent()
scheduler = SchedulerAgent()
reminder = ReminderAgent()

st.set_page_config(page_title="Smart To-Do App", layout="wide")
st.title("🤖 Multi-Agent To-Do & Reminder App")

# Sidebar for agent logs
with st.sidebar:
    st.header("🔍 Agent Activity Log")
    if 'agent_logs' not in st.session_state:
        st.session_state.agent_logs = []
    
    for log in st.session_state.agent_logs[-10:]:  # Show last 10 logs
        st.text(f"{log['time']}: {log['agent']} - {log['action']}")

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📝 Add New Task")
    
    with st.form("add_task"):
        task_title = st.text_input("Task Title")
        task_desc = st.text_area("Description", height=100)
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        due_date = st.date_input("Due Date", min_value=datetime.now().date())
        due_time = st.time_input("Due Time")
        
        if st.form_submit_button("Add Task"):
            if task_title:
                # Combine date and time
                due_datetime = datetime.combine(due_date, due_time)
                
                # Create task using planner agent
                task = planner.create_task(task_title, task_desc, priority, due_datetime)
                
                # Schedule task using scheduler agent
                scheduled_task = scheduler.schedule_task(task)
                
                # Store task
                storage.add_task(scheduled_task)
                
                # Log agent activity
                st.session_state.agent_logs.append({
                    'time': datetime.now().strftime("%H:%M"),
                    'agent': 'Planner',
                    'action': f'Created task: {task_title}'
                })
                st.session_state.agent_logs.append({
                    'time': datetime.now().strftime("%H:%M"),
                    'agent': 'Scheduler',
                    'action': f'Scheduled task for {due_datetime.strftime("%m/%d %H:%M")}'
                })
                
                st.success("Task added successfully!")
                st.rerun()

with col2:
    st.header("⚡ Quick Actions")
    
    if st.button("🔔 Check Reminders"):
        tasks = storage.get_all_tasks()
        reminders = reminder.check_reminders(tasks)
        
        if reminders:
            st.warning(f"🚨 {len(reminders)} reminders!")
            for task in reminders:
                st.error(f"Due: {task['title']} - {task['due_date']}")
        else:
            st.success("No urgent reminders")
        
        # Log reminder check
        st.session_state.agent_logs.append({
            'time': datetime.now().strftime("%H:%M"),
            'agent': 'Reminder',
            'action': f'Checked {len(reminders)} reminders'
        })

    if st.button("🧹 Auto-Organize"):
        tasks = storage.get_all_tasks()
        organized_tasks = scheduler.optimize_schedule(tasks)
        
        for task in organized_tasks:
            storage.update_task(task['id'], task)
        
        st.success("Tasks reorganized!")
        st.session_state.agent_logs.append({
            'time': datetime.now().strftime("%H:%M"),
            'agent': 'Scheduler',
            'action': 'Optimized task schedule'
        })

# Display tasks
st.header("📋 Your Tasks")

tasks = storage.get_all_tasks()
if not tasks:
    st.info("No tasks yet. Add your first task above!")
else:
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Completed"])
    with col2:
        priority_filter = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
    with col3:
        sort_by = st.selectbox("Sort by", ["Due Date", "Priority", "Created"])

    # Apply filters
    filtered_tasks = tasks
    if status_filter != "All":
        filtered_tasks = [t for t in filtered_tasks if t['status'] == status_filter.lower()]
    if priority_filter != "All":
        filtered_tasks = [t for t in filtered_tasks if t['priority'] == priority_filter]

    # Sort tasks
    if sort_by == "Due Date":
        filtered_tasks.sort(key=lambda x: x['due_date'])
    elif sort_by == "Priority":
        priority_order = {"High": 3, "Medium": 2, "Low": 1}
        filtered_tasks.sort(key=lambda x: priority_order[x['priority']], reverse=True)

    # Display tasks
    for task in filtered_tasks:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                status_icon = "✅" if task['status'] == 'completed' else "⏳"
                priority_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}[task['priority']]
                
                st.write(f"{status_icon} **{task['title']}** {priority_color}")
                if task['description']:
                    st.caption(task['description'])
                
                # Check if overdue
                due_dt = datetime.fromisoformat(task['due_date'])
                if due_dt < datetime.now() and task['status'] != 'completed':
                    st.error(f"⚠️ Overdue by {datetime.now() - due_dt}")
                else:
                    st.caption(f"Due: {due_dt.strftime('%m/%d/%Y %H:%M')}")
            
            with col2:
                if st.button("✓", key=f"complete_{task['id']}", help="Mark Complete"):
                    task['status'] = 'completed'
                    task['completed_date'] = datetime.now().isoformat()
                    storage.update_task(task['id'], task)
                    st.rerun()
            
            with col3:
                if st.button("✏️", key=f"edit_{task['id']}", help="Edit Task"):
                    st.session_state[f"edit_task_{task['id']}"] = True
            
            with col4:
                if st.button("🗑️", key=f"delete_{task['id']}", help="Delete Task"):
                    storage.delete_task(task['id'])
                    st.success("Task deleted!")
                    st.rerun()
            
            # Edit form (appears when edit button is clicked)
            if st.session_state.get(f"edit_task_{task['id']}", False):
                with st.form(f"edit_form_{task['id']}"):
                    new_title = st.text_input("Title", value=task['title'])
                    new_desc = st.text_area("Description", value=task.get('description', ''))
                    new_priority = st.selectbox("Priority", ["Low", "Medium", "High"], 
                                              index=["Low", "Medium", "High"].index(task['priority']))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Save Changes"):
                            task['title'] = new_title
                            task['description'] = new_desc
                            task['priority'] = new_priority
                            storage.update_task(task['id'], task)
                            st.session_state[f"edit_task_{task['id']}"] = False
                            st.rerun()
                    with col2:
                        if st.form_submit_button("Cancel"):
                            st.session_state[f"edit_task_{task['id']}"] = False
                            st.rerun()
            
            st.divider()

# Statistics
if tasks:
    st.header("📊 Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t['status'] == 'completed'])
    pending_tasks = total_tasks - completed_tasks
    overdue_tasks = len([t for t in tasks if datetime.fromisoformat(t['due_date']) < datetime.now() 
                        and t['status'] != 'completed'])
    
    col1.metric("Total Tasks", total_tasks)
    col2.metric("Completed", completed_tasks)
    col3.metric("Pending", pending_tasks)
    col4.metric("Overdue", overdue_tasks)

# Auto-refresh for reminders (every 60 seconds)
if st.button("🔄 Auto-Refresh Reminders"):
    st.session_state.auto_refresh = True

if st.session_state.get('auto_refresh', False):
    import time
    time.sleep(60)  # Wait 60 seconds
    st.rerun()