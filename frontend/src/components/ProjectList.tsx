import React, { useState, useEffect } from "react";
import { getProjects, createProject } from "../lib";
import type { Project, ProjectCreate } from "../lib";
import ProjectCard from "./ProjectCard";

export const ProjectList: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState<string>(""); // <-- Added missing hook

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

  if (loading) return <div>Loading projects...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="project-list">
      <div className="header">
        <h2>Projects</h2>
        <button onClick={() => setShowCreateForm(!showCreateForm)}>
          {showCreateForm ? "Cancel" : "New Project"}
        </button>
      </div>

      {showCreateForm && (
        <form onSubmit={handleCreateProject} className="create-form">
          <h3>Create New Project</h3>
          <div>
            <label>
              Name:
              <input
                type="text"
                value={newProject.name}
                onChange={(e) =>
                  setNewProject({ ...newProject, name: e.target.value })
                }
                required
              />
            </label>
          </div>
          <div>
            <label>
              Description:
              <textarea
                value={newProject.description}
                onChange={(e) =>
                  setNewProject({ ...newProject, description: e.target.value })
                }
              />
            </label>
          </div>
          <div>
            <button type="submit">Create Project</button>
            <button type="button" onClick={() => setShowCreateForm(false)}>
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="projects">
        {projects.length === 0 ? (
          <p>No projects found. Create your first project!</p>
        ) : (
          <>
            <div className="search-bar" style={{ marginBottom: "1rem" }}>
              <input
                type="text"
                placeholder="Search projects by name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{ width: "500px", padding: "0.5rem" }}
              />
            </div>
            {projects.filter((project) =>
              project.name.toLowerCase().includes(searchTerm.toLowerCase())
            ).length === 0 ? (
              <p>No results found</p>
            ) : (
              projects
                .filter((project) =>
                  project.name.toLowerCase().includes(searchTerm.toLowerCase())
                )
                .map((project) => (
                  <ProjectCard key={project.id} project={project} />
                ))
            )}
          </>
        )}
      </div>
    </div>
  );
};
