/*
 * Frontend component for task creation and editing
 * This would be implemented in the frontend directory
 */

import React, { useState } from 'react';

const TaskEditor = ({ onSave, onCancel, task }) => {
  const [title, setTitle] = useState(task?.title || '');
  const [description, setDescription] = useState(task?.description || '');
  const [priority, setPriority] = useState(task?.priority || 'medium');
  const [tags, setTags] = useState(task?.tags || []);
  const [dueAt, setDueAt] = useState(task?.due_at || '');
  const [remindAt, setRemindAt] = useState(task?.remind_at || '');
  const [recurrenceRule, setRecurrenceRule] = useState(task?.recurrence_rule || '');

  const handleSave = () => {
    const taskData = {
      title,
      description,
      priority,
      tags,
      due_at: dueAt || null,
      remind_at: remindAt || null,
      recurrence_rule: recurrenceRule || null
    };

    if (task?.task_id) {
      taskData.task_id = task.task_id;
    }

    onSave(taskData);
  };

  const addTag = (tagText) => {
    if (tagText && !tags.includes(tagText)) {
      setTags([...tags, tagText.trim()]);
    }
  };

  const removeTag = (index) => {
    setTags(tags.filter((_, i) => i !== index));
  };

  return (
    <div className="task-editor">
      <h2>{task ? 'Edit Task' : 'Create Task'}</h2>
      <div className="form-group">
        <label htmlFor="title">Title *</label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="description">Description</label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>

      <div className="form-group">
        <label htmlFor="priority">Priority</label>
        <select
          id="priority"
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="tags">Tags</label>
        <div className="tags-input">
          {tags.map((tag, index) => (
            <span key={index} className="tag">
              {tag}
              <button onClick={() => removeTag(index)}>×</button>
            </span>
          ))}
          <input
            type="text"
            placeholder="Add a tag..."
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                addTag(e.target.value);
                e.target.value = '';
              }
            }}
          />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="dueAt">Due Date</label>
        <input
          id="dueAt"
          type="datetime-local"
          value={dueAt}
          onChange={(e) => setDueAt(e.target.value)}
        />
      </div>

      <div className="form-group">
        <label htmlFor="remindAt">Reminder Time</label>
        <input
          id="remindAt"
          type="datetime-local"
          value={remindAt}
          onChange={(e) => setRemindAt(e.target.value)}
        />
      </div>

      <div className="form-group">
        <label htmlFor="recurrenceRule">Recurrence Rule</label>
        <select
          id="recurrenceRule"
          value={recurrenceRule}
          onChange={(e) => setRecurrenceRule(e.target.value)}
        >
          <option value="">None</option>
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </select>
      </div>

      <div className="actions">
        <button onClick={handleSave}>Save</button>
        <button onClick={onCancel}>Cancel</button>
      </div>
    </div>
  );
};

export default TaskEditor;