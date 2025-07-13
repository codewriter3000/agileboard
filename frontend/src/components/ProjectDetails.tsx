import React from "react";
import { useNavigate } from "react-router-dom";

type Task = {
  id: number;
  title: string;
  description: string;
  status: "Backlog" | "In Progress" | "Review" | "Done";
  assignee_id?: number;
  assignee_name?: string;
};

type Project = {
  id: number;
  name: string;
  description: string;
  owner: string;
  startDate: string;
  endDate?: string;
  tasks: Task[];
};

type ProjectDetailsProps = {
  project: Project;
  onCreateTask?: () => void;
  onEditProject?: () => void;
};

const statusColor = {
  "Backlog": "#f0ad4e",
  "In Progress": "#5bc0de",
  "Review": "#d9534f",
  "Done": "#5cb85c",
};

const style = `
.task-row {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.task-row:hover {
  background-color: #3f3f3f;
}
`;

// Inject styles into the document
const injectStyles = () => {
  if (
    typeof document !== "undefined" &&
    !document.getElementById("project-details-styles")
  ) {
    const styleElement = document.createElement("style");
    styleElement.id = "project-details-styles";
    styleElement.innerHTML = style;
    document.head.appendChild(styleElement);
  }
};

export const ProjectDetails: React.FC<ProjectDetailsProps> = ({ project, onCreateTask, onEditProject }) => {
  const navigate = useNavigate();

  const handleTaskClick = (taskId: number) => {
    navigate(`/projects/${project.id}/tasks/${taskId}`);
  };

  injectStyles();
  if (!project) {
    return <div className="error">Project not found</div>;
  }

  return (
    <div style={{ padding: 24, maxWidth: 800, margin: "0 auto" }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2>{project.name}</h2>
        {onEditProject && (
          <button
            onClick={onEditProject}
            style={{
              background: '#007bff',
              color: 'white',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            Edit Project
          </button>
        )}
      </div>
      <p>
        <strong>Description:</strong> {project.description}
      </p>
      <p>
        <strong>Owner:</strong> {project.owner}
      </p>
      <p>
        <strong>Start Date:</strong> {project.startDate}
        {project.endDate && (
          <>
            {" "}
            <strong>End Date:</strong> {project.endDate}
          </>
        )}
      </p>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h3>Tasks</h3>
        {onCreateTask && (
          <button
            onClick={onCreateTask}
            style={{
              background: '#28a745',
              color: 'white',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            + Add Task
          </button>
        )}
      </div>

      {project.tasks.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
          <p>No tasks available for this project.</p>
          {onCreateTask && (
            <button
              onClick={onCreateTask}
              style={{
                background: '#007bff',
                color: 'white',
                border: 'none',
                padding: '12px 24px',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '14px',
                marginTop: '16px'
              }}
            >
              Create Your First Task
            </button>
          )}
        </div>
      ) : (
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th
              style={{
                borderBottom: "1px solid #ccc",
                textAlign: "left",
                padding: "8px",
              }}
            >
              Title
            </th>
            <th
              style={{
                borderBottom: "1px solid #ccc",
                textAlign: "left",
                padding: "8px",
              }}
            >
              Description
            </th>
            <th
              style={{
                borderBottom: "1px solid #ccc",
                textAlign: "left",
                padding: "8px",
              }}
            >
              Status
            </th>
            <th
              style={{
                borderBottom: "1px solid #ccc",
                textAlign: "left",
                padding: "8px",
              }}
            >
              Assignee
            </th>
          </tr>
        </thead>
        <tbody>
          {project.tasks.map((task) => (
            <tr
              className="task-row"
              key={task.id}
              onClick={() => handleTaskClick(task.id)}
              style={{ cursor: 'pointer' }}
            >
              <td style={{ borderBottom: "1px solid #eee", padding: "8px" }}>
                {task.title}
              </td>
              <td style={{ borderBottom: "1px solid #eee", padding: "8px" }}>
                {task.description}
              </td>
              <td style={{ borderBottom: "1px solid #eee", padding: "8px" }}>
                <span
                  style={{
                    background: statusColor[task.status],
                    color: "#fff",
                    borderRadius: 4,
                    padding: "2px 8px",
                    fontSize: 12,
                  }}
                >
                  {task.status}
                </span>
              </td>
              <td style={{ borderBottom: "1px solid #eee", padding: "8px" }}>
                {task.assignee_name ? (
                  <span
                    style={{
                      background: "#e9ecef",
                      color: "#495057",
                      borderRadius: 4,
                      padding: "2px 8px",
                      fontSize: 12,
                    }}
                  >
                    {task.assignee_name}
                  </span>
                ) : (
                  <span style={{ color: "#6c757d", fontStyle: "italic" }}>
                    Unassigned
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      )}
    </div>
  );
};

export default ProjectDetails;
