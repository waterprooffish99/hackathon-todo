'use client';

import { useState, useEffect } from 'react';
import { useSession } from '../context/session';

interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
  user_id: string;
}

export default function DashboardPage() {
  const { user, token, isAuthenticated, logout } = useSession();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskDescription, setNewTaskDescription] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      window.location.href = '/login';
      return;
    }

    fetchTasks();
  }, [isAuthenticated]);

  const fetchTasks = async () => {
    if (!token) return;

    try {
      // Use the new endpoint that gets user from JWT token
      const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/api/tasks`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          logout(); // Log out the user if token is invalid/expired
          window.location.href = '/login'; // Redirect to login
          return;
        } else if (response.status === 404) {
          // If no tasks found, return empty array instead of throwing error
          setTasks([]);
          return;
        } else {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `Failed to fetch tasks: ${response.status}`);
        }
      }

      const data = await response.json();
      setTasks(data.tasks || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskTitle.trim() || !token) return;

    try {
      // Use the new endpoint that gets user from JWT token
      const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/api/tasks`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: newTaskTitle,
          description: newTaskDescription || null,
          priority: "medium",
          tags: [],
          ai_interpret: false
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          logout(); // Log out the user if token is invalid/expired
          window.location.href = '/login'; // Redirect to login
          return;
        } else {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `Failed to create task: ${response.status}`);
        }
      }

      const newTask = await response.json();
      setTasks([...tasks, newTask]);
      setNewTaskTitle('');
      setNewTaskDescription('');
    } catch (err: any) {
      setError(err.message || 'Failed to create task');
    }
  };

  const handleToggleComplete = async (taskId: string, currentStatus: boolean) => {
    if (!token) return;

    try {
      // Use the new endpoint that gets user from JWT token
      const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/api/tasks/${taskId}/complete`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          completed: !currentStatus,
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          logout(); // Log out the user if token is invalid/expired
          window.location.href = '/login'; // Redirect to login
          return;
        } else {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `Failed to update task: ${response.status}`);
        }
      }

      const updatedTask = await response.json();
      setTasks(tasks.map(task =>
        task.id === taskId ? { ...task, completed: !currentStatus } : task
      ));
    } catch (err: any) {
      setError(err.message || 'Failed to update task');
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    if (!token) return;

    try {
      // Use the new endpoint that gets user from JWT token
      const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/api/tasks/${taskId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          logout(); // Log out the user if token is invalid/expired
          window.location.href = '/login'; // Redirect to login
          return;
        } else {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `Failed to delete task: ${response.status}`);
        }
      }

      setTasks(tasks.filter(task => task.id !== taskId));
    } catch (err: any) {
      setError(err.message || 'Failed to delete task');
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p>Please log in to access your dashboard</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold">Todo Dashboard</h1>
            </div>
            <div className="flex items-center">
              <a
                href="/chat"
                className="mr-4 px-3 py-2 rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
              >
                AI Assistant
              </a>
              <span className="mr-4">Welcome, {user?.name || 'User'}!</span>
              <button
                onClick={logout}
                className="ml-4 px-3 py-2 rounded-md text-sm font-medium text-white bg-red-600 hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg p-6">
            <h2 className="text-2xl font-bold mb-6">Your Tasks</h2>

            {error && (
              <div className="rounded-md bg-red-50 p-4 mb-4">
                <div className="text-sm text-red-700">{error}</div>
              </div>
            )}

            {/* Add Task Form */}
            <form onSubmit={handleCreateTask} className="mb-8">
              <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                <div className="sm:col-span-3">
                  <label htmlFor="task-title" className="block text-sm font-medium text-gray-700">
                    Task Title
                  </label>
                  <div className="mt-1">
                    <input
                      type="text"
                      id="task-title"
                      value={newTaskTitle}
                      onChange={(e) => setNewTaskTitle(e.target.value)}
                      required
                      className="py-2 px-3 block w-full shadow-sm focus:ring-indigo-500 focus:border-indigo-500 border-gray-300 rounded-md text-gray-900 bg-white"
                      placeholder="What needs to be done?"
                    />
                  </div>
                </div>

                <div className="sm:col-span-3">
                  <label htmlFor="task-description" className="block text-sm font-medium text-gray-700">
                    Description (Optional)
                  </label>
                  <div className="mt-1">
                    <input
                      type="text"
                      id="task-description"
                      value={newTaskDescription}
                      onChange={(e) => setNewTaskDescription(e.target.value)}
                      className="py-2 px-3 block w-full shadow-sm focus:ring-indigo-500 focus:border-indigo-500 border-gray-300 rounded-md text-gray-900 bg-white"
                      placeholder="Additional details..."
                    />
                  </div>
                </div>

                <div className="sm:col-span-6">
                  <button
                    type="submit"
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Add Task
                  </button>
                </div>
              </div>
            </form>

            {/* Tasks List */}
            <div className="space-y-4">
              {loading ? (
                <p>Loading tasks...</p>
              ) : tasks.length === 0 ? (
                <p className="text-gray-500">No tasks yet. Add your first task above!</p>
              ) : (
                tasks.map((task) => (
                  <div
                    key={task.id}
                    className={`border rounded-lg p-4 ${
                      task.completed ? 'bg-green-50 border-green-200' : 'bg-white'
                    }`}
                  >
                    <div className="flex items-start">
                      <input
                        type="checkbox"
                        checked={task.completed}
                        onChange={() => handleToggleComplete(task.id, task.completed)}
                        className="h-5 w-5 text-indigo-600 rounded mt-1"
                      />
                      <div className="ml-3 flex-1">
                        <h3 className={`text-lg font-medium ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                          {task.title}
                        </h3>
                        {task.description && (
                          <p className={`mt-1 ${task.completed ? 'line-through text-gray-400' : 'text-gray-600'}`}>
                            {task.description}
                          </p>
                        )}
                        <div className="mt-2 text-xs text-gray-500">
                          Created: {new Date(task.created_at).toLocaleString()}
                          {task.updated_at !== task.created_at && (
                            <span>, Updated: {new Date(task.updated_at).toLocaleString()}</span>
                          )}
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteTask(task.id)}
                        className="ml-4 inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}