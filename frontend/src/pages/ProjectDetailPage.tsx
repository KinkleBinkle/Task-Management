import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import apiClient from "../api/client";

interface Task {
  id: number;
  title: string;
  description?: string;
  status: "To Do" | "In Progress" | "Done";
  assignee_id?: number;
  created_at: string;
  updated_at: string;
}

interface Project {
  id: number;
  name: string;
  description?: string;
  owner_id: number;
  members?: any[];
  tasks?: Task[];
}

interface Member {
  id: number;
  username: string;
  name: string;
  role: string;
}

export const ProjectDetailPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [project, setProject] = useState<Project | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showCreateTaskModal, setShowCreateTaskModal] = useState(false);
  const [taskTitle, setTaskTitle] = useState("");
  const [taskDescription, setTaskDescription] = useState("");
  const [taskAssignee, setTaskAssignee] = useState("");

  useEffect(() => {
    if (projectId) {
      fetchProjectDetails();
    }
  }, [projectId]);

  const fetchProjectDetails = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getProject(parseInt(projectId!));
      setProject(data);
      if (data.members) {
        setMembers(data.members);
      }
      if (data.tasks) {
        setTasks(data.tasks);
      }
    } catch (err: any) {
      setError(err.message || "Failed to load project");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      const newTask = await apiClient.createTask(
        parseInt(projectId!),
        taskTitle,
        taskDescription,
        taskAssignee ? parseInt(taskAssignee) : undefined
      );
      setTasks([...tasks, newTask]);
      setTaskTitle("");
      setTaskDescription("");
      setTaskAssignee("");
      setShowCreateTaskModal(false);
    } catch (err: any) {
      setError(err.message || "Failed to create task");
    }
  };

  const handleUpdateTaskStatus = async (taskId: number, newStatus: string) => {
    try {
      await apiClient.updateTask(parseInt(projectId!), taskId, {
        status: newStatus,
      });
      setTasks(
        tasks.map((t) =>
          t.id === taskId ? { ...t, status: newStatus as any } : t
        )
      );
    } catch (err: any) {
      setError(err.message || "Failed to update task");
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    if (!window.confirm("Are you sure you want to delete this task?")) return;

    try {
      await apiClient.deleteTask(parseInt(projectId!), taskId);
      setTasks(tasks.filter((t) => t.id !== taskId));
    } catch (err: any) {
      setError(err.message || "Failed to delete task");
    }
  };

  const isOwner = project?.owner_id === user?.id;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <button
            onClick={() => navigate("/dashboard")}
            className="text-blue-500 hover:underline mb-2"
          >
            ← Back to Dashboard
          </button>
          {project && (
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {project.name}
              </h1>
              {project.description && (
                <p className="text-gray-600 mt-2">{project.description}</p>
              )}
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-600">Loading project...</p>
          </div>
        ) : error ? (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Tasks Section */}
            <div className="lg:col-span-2">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Tasks</h2>
                {isOwner && (
                  <button
                    onClick={() => setShowCreateTaskModal(true)}
                    className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg"
                  >
                    + Add Task
                  </button>
                )}
              </div>

              {/* Task Columns */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {["To Do", "In Progress", "Done"].map((status) => (
                  <div key={status} className="bg-gray-100 rounded-lg p-4">
                    <h3 className="font-semibold text-gray-800 mb-4">
                      {status}
                    </h3>
                    <div className="space-y-3">
                      {tasks
                        .filter((t) => t.status === status)
                        .map((task) => (
                          <div
                            key={task.id}
                            className="bg-white p-4 rounded-lg shadow hover:shadow-md transition"
                          >
                            <h4 className="font-semibold text-gray-800">
                              {task.title}
                            </h4>
                            {task.description && (
                              <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                                {task.description}
                              </p>
                            )}
                            {isOwner && (
                              <div className="flex space-x-2 mt-3">
                                {status !== "Done" && (
                                  <button
                                    onClick={() => {
                                      const nextStatus =
                                        status === "To Do"
                                          ? "In Progress"
                                          : "Done";
                                      handleUpdateTaskStatus(
                                        task.id,
                                        nextStatus
                                      );
                                    }}
                                    className="text-xs bg-blue-100 hover:bg-blue-200 text-blue-800 px-2 py-1 rounded"
                                  >
                                    Move →
                                  </button>
                                )}
                                <button
                                  onClick={() => handleDeleteTask(task.id)}
                                  className="text-xs bg-red-100 hover:bg-red-200 text-red-800 px-2 py-1 rounded"
                                >
                                  Delete
                                </button>
                              </div>
                            )}
                          </div>
                        ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Members Section */}
            <div className="lg:col-span-1">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Members</h2>
              <div className="bg-white rounded-lg shadow p-6">
                {members.length === 0 ? (
                  <p className="text-gray-600">No members yet</p>
                ) : (
                  <ul className="space-y-4">
                    {members.map((member) => (
                      <li
                        key={member.id}
                        className="flex justify-between items-center"
                      >
                        <div>
                          <p className="font-semibold text-gray-800">
                            {member.name}
                          </p>
                          <p className="text-sm text-gray-600">
                            @{member.username}
                          </p>
                        </div>
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          {member.role}
                        </span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Create Task Modal */}
      {showCreateTaskModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-8 w-full max-w-lg">
            <h2 className="text-2xl font-bold mb-6">Create New Task</h2>

            <form onSubmit={handleCreateTask}>
              <div className="mb-4">
                <label className="block text-gray-700 font-semibold mb-2">
                  Task Title
                </label>
                <input
                  type="text"
                  value={taskTitle}
                  onChange={(e) => setTaskTitle(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter task title"
                  required
                />
              </div>

              <div className="mb-4">
                <label className="block text-gray-700 font-semibold mb-2">
                  Description (optional)
                </label>
                <textarea
                  value={taskDescription}
                  onChange={(e) => setTaskDescription(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter task description"
                  rows={4}
                />
              </div>

              <div className="mb-6">
                <label className="block text-gray-700 font-semibold mb-2">
                  Assign To (optional)
                </label>
                <select
                  value={taskAssignee}
                  onChange={(e) => setTaskAssignee(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Unassigned</option>
                  {members.map((member) => (
                    <option key={member.id} value={member.id}>
                      {member.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex space-x-4">
                <button
                  type="submit"
                  className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-lg"
                >
                  Create
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateTaskModal(false)}
                  className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-2 rounded-lg"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
