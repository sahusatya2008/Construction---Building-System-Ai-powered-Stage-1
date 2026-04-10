/**
 * Dashboard Page
 * ==============
 * Main dashboard showing projects and recent designs.
 */

import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import type { Project } from '../types';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [projects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      setIsLoading(false);
    }, 500);
  }, []);
  
  const handleNewProject = () => {
    navigate('/design');
  };
  
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-indigo-600">ArchAI</h1>
            <span className="text-gray-400">|</span>
            <span className="text-gray-600">Dashboard</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-gray-600">
              Welcome, User
            </span>
            <Link
              to="/login"
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Logout
            </Link>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Actions */}
        <div className="mb-8">
          <button
            onClick={handleNewProject}
            className="px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors"
          >
            + New Design Project
          </button>
        </div>
        
        {/* Projects Grid */}
        <div>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Your Projects</h2>
          
          {isLoading ? (
            <div className="text-center py-12 text-gray-500">Loading...</div>
          ) : projects.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-xl shadow-sm">
              <div className="text-gray-400 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-600 mb-2">No projects yet</h3>
              <p className="text-gray-500 mb-4">Create your first architectural design project</p>
              <button
                onClick={handleNewProject}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                Create Project
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projects.map((project) => (
                <Link
                  key={project.id}
                  to={`/design/${project.id}`}
                  className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-6"
                >
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="font-semibold text-gray-800">{project.name}</h3>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      project.status === 'draft' ? 'bg-gray-100 text-gray-600' :
                      project.status === 'active' ? 'bg-green-100 text-green-600' :
                      project.status === 'completed' ? 'bg-blue-100 text-blue-600' :
                      'bg-gray-100 text-gray-600'
                    }`}>
                      {project.status}
                    </span>
                  </div>
                  <p className="text-gray-500 text-sm mb-4">
                    {project.description || 'No description'}
                  </p>
                  <div className="text-xs text-gray-400">
                    Created {new Date(project.created_at).toLocaleDateString()}
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;