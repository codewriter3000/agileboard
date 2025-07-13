import React from 'react';
import { useNavigate } from 'react-router-dom';
import type { Project } from '../lib/project';

interface ProjectCardProps {
    project: Project;
    onEdit: (project: Project) => void;
}

// CSS styles
const styles = `
.project-card {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 16px;
    background: rgb(40, 44, 42);
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 16px;
    max-width: 400px;
    cursor: pointer;
}

.project-card:hover {
    background: rgb(50, 54, 52);
}

.project-card-title {
    font-size: 1.25rem;
    margin: 0 0 8px 0;
    color: #fff;
}
.project-card-desc {
    font-size: 1rem;
    margin: 0 0 12px 0;
    color: #aaa;
}
.project-meta {
    display: flex;
    justify-content: space-between;
    font-size: 0.9rem;
    color: #aaa;
}
.project-meta-owner {
    font-weight: 500;
}
.project-meta-date {
    font-style: italic;
}
.project-card-actions {
    display: flex;
    gap: 8px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #555;
}
.project-card-edit-btn {
    padding: 4px 8px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.8rem;
}
.project-card-edit-btn:hover {
    background: #0056b3;
}
`;

// Inject styles into the document
const injectStyles = () => {
    if (typeof document !== 'undefined' && !document.getElementById('project-card-styles')) {
        const style = document.createElement('style');
        style.id = 'project-card-styles';
        style.innerHTML = styles;
        document.head.appendChild(style);
    }
};

const ProjectCard: React.FC<ProjectCardProps> = ({ project, onEdit }) => {
    React.useEffect(() => {
        injectStyles();
    }, []);

    const navigate = useNavigate();

    const handleClick = () => {
        navigate(`/projects/${project.id}`);
    };

    const handleEditClick = (e: React.MouseEvent) => {
        e.stopPropagation(); // Prevent navigation when clicking edit
        onEdit(project);
    };

    return (
        <div className="project-card">
            <div className="project-card-content" onClick={handleClick} tabIndex={0} role="button">
                <h3 className="project-card-title">{project.name}</h3>
                {project.description && <p className="project-card-desc">{project.description}</p>}
                <div className="project-meta">
                    <span className="project-meta-owner">Owner: {project.owner_id}</span>
                    <span className="project-meta-date">
                        Created: {new Date(project.created_at).toLocaleDateString()}
                    </span>
                </div>
            </div>
            <div className="project-card-actions">
                <button
                    className="project-card-edit-btn"
                    onClick={handleEditClick}
                >
                    Edit
                </button>
            </div>
        </div>
    );
};

export default ProjectCard;