import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useProject } from "../context/ProjectContext";
import apiClient from "../api/client";

interface Project {
  id: number;
  owner_id: number;
  owner_name: string;
  name?: string;
  description?: string;
  created_at?: string;
  task_count?: number;
  member_count?: number;
}

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { setProjects, addProject } = useProject();
  const [projects, setLocalProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [projectName, setProjectName] = useState("");
  const [projectDescription, setProjectDescription] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user) {
      navigate("/login");
    } else {
      fetchProjects();
    }
  }, [user, navigate]);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const data = await apiClient.listProjects(user?.id);
      setLocalProjects(data);
      setProjects(data);
    } catch (err: any) {
      setError(err.message || "Failed to load projects");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      const newProject = await apiClient.createProject(
        projectName,
        projectDescription
      );
      addProject(newProject);
      setLocalProjects([...projects, newProject]);
      setProjectName("");
      setProjectDescription("");
      setShowCreateModal(false);
    } catch (err: any) {
      setError(err.message || "Failed to create project");
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const handleProjectClick = (projectId: number) => {
    navigate(`/projects/${projectId}`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Task Management</h1>
          <div className="flex items-center space-x-4">
            <span className="text-gray-600">Welcome, {user?.name}</span>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Create Project Button */}
        <div className="mb-8">
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white font-semibold rounded-lg"
          >
            + New Project
          </button>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {/* Projects Grid */}
        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-600">Loading projects...</p>
          </div>
        ) : projects.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">
              No projects yet. Create one to get started!
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <div
                key={project.id}
                onClick={() => handleProjectClick(project.id)}
                className="bg-white rounded-lg shadow hover:shadow-lg cursor-pointer transition p-6"
              >
                <h3 className="text-xl font-semibold text-gray-800 mb-2">
                  {project.name || "Untitled Project"}
                </h3>
                <p className="text-gray-600 mb-4 line-clamp-2">
                  {project.description || "No description"}
                </p>
                <div className="flex justify-between text-sm text-gray-500">
                  <span>👥 {project.member_count || 0} members</span>
                  <span>📋 {project.task_count || 0} tasks</span>
                </div>
                <p className="text-xs text-gray-400 mt-4">
                  Owner: {project.owner_name}
                </p>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Create Project Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-8 w-full max-w-lg">
            <h2 className="text-2xl font-bold mb-6">Create New Project</h2>

            <form onSubmit={handleCreateProject}>
              <div className="mb-4">
                <label className="block text-gray-700 font-semibold mb-2">
                  Project Name
                </label>
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter project name"
                  required
                />
              </div>

              <div className="mb-6">
                <label className="block text-gray-700 font-semibold mb-2">
                  Description (optional)
                </label>
                <textarea
                  value={projectDescription}
                  onChange={(e) => setProjectDescription(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter project description"
                  rows={4}
                />
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
                  onClick={() => setShowCreateModal(false)}
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
