import React, { useState, useEffect } from "react";
import { getProjects, createProject } from "../lib";
import type { Project, ProjectCreate } from "../lib";
import { useNavigate } from "react-router-dom";

export const ProjectList: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const navigate = useNavigate();

  const [newProject, setNewProject] = useState<ProjectCreate>({
    name: "",
    description: "",
    owner_id: 10, // David Frisco (Admin user)
  });

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const data = await getProjects();
      setProjects(data);
    } catch (err) {
      setError("Failed to load projects");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const project = await createProject(newProject);
      setProjects([...projects, project]);
      setNewProject({ name: "", description: "", owner_id: 10 });
      setShowCreateForm(false);
    } catch (err) {
      setError("Failed to create project");
      console.error(err);
    }
  };

  const handleProjectClick = (projectId: number) => {
    navigate(`/projects/${projectId}`);
  };

  const filteredProjects = projects.filter(project =>
    project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (project.description && project.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Active': return '#28a745';
      case 'Archived': return '#6c757d';
      default: return '#007bff';
    }
  };

  if (loading) return <div>Loading projects...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1>Project Management</h1>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          style={{
            background: '#007bff',
            color: 'white',
            border: 'none',
            padding: '8px 16px',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          {showCreateForm ? "Cancel" : "New Project"}
        </button>
      </div>

      {showCreateForm && (
        <div style={{
          background: '#161616',
          padding: '24px',
          borderRadius: '8px',
          marginBottom: '24px',
          border: '1px solid #e0e0e0'
        }}>
          <form onSubmit={handleCreateProject}>
            <h3 style={{ margin: '0 0 20px 0', color: '#fff' }}>Create New Project</h3>
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', marginBottom: '4px', color: '#fff' }}>
                Name *
              </label>
              <input
                type="text"
                value={newProject.name}
                onChange={(e) =>
                  setNewProject({ ...newProject, name: e.target.value })
                }
                required
                style={{
                  width: '100%',
                  padding: '8px',
                  borderRadius: '4px',
                  border: '1px solid #ccc',
                  fontSize: '14px'
                }}
              />
            </div>
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '4px', color: '#fff' }}>
                Description
              </label>
              <textarea
                value={newProject.description}
                onChange={(e) =>
                  setNewProject({ ...newProject, description: e.target.value })
                }
                style={{
                  width: '100%',
                  padding: '8px',
                  borderRadius: '4px',
                  border: '1px solid #ccc',
                  fontSize: '14px',
                  minHeight: '80px'
                }}
              />
            </div>
            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                type="submit"
                style={{
                  background: '#007bff',
                  color: 'white',
                  border: 'none',
                  padding: '8px 16px',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Create Project
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                style={{
                  background: '#6c757d',
                  color: 'white',
                  border: 'none',
                  padding: '8px 16px',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          placeholder="Search projects by name or description..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            width: '300px',
            padding: '8px',
            borderRadius: '4px',
            border: '1px solid #ccc'
          }}
        />
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))',
        gap: '20px'
      }}>
        {filteredProjects.map(project => (
          <div
            key={project.id}
            onClick={() => handleProjectClick(project.id)}
            style={{
              border: '1px solid #e0e0e0',
              borderRadius: '8px',
              padding: '20px',
              background: '#2c2c2c',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              cursor: 'pointer',
              transition: 'transform 0.2s ease, box-shadow 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
            }}
          >
            <div>
              <h3 style={{ margin: '0 0 8px 0', color: '#fff' }}>{project.name}</h3>
              <p style={{ margin: '0 0 8px 0', color: '#ccc' }}>{project.description || 'No description'}</p>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <span
                  style={{
                    background: getStatusColor(project.status || 'Active'),
                    color: 'white',
                    padding: '2px 8px',
                    borderRadius: '12px',
                    fontSize: '12px',
                    fontWeight: 'bold'
                  }}
                >
                  {project.status || 'Active'}
                </span>
                <span style={{ color: '#666', fontSize: '12px' }}>
                  Created: {new Date(project.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredProjects.length === 0 && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
          {searchTerm ? 'No projects found matching your search.' : 'No projects found.'}
        </div>
      )}
    </div>
  );
};
