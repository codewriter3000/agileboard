import React from 'react';
import { useNavigate } from 'react-router-dom';

export interface Project {
    id: string;
    name: string;
    description?: string;
    owner_id: string;
    created_at: string;
}

interface ProjectCardProps {
    project: Project;
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

const ProjectCard: React.FC<ProjectCardProps> = ({ project }) => {
    React.useEffect(() => {
        injectStyles();
    }, []);

    const navigate = useNavigate();

    const handleClick = () => {
        navigate(`/projects/${project.id}`);
    };

    return (
        <div className="project-card" onClick={handleClick} tabIndex={0} role="button">
            <h3 className="project-card-title">{project.name}</h3>
            {project.description && <p className="project-card-desc">{project.description}</p>}
            <div className="project-meta">
                <span className="project-meta-owner">Owner: {project.owner_id}</span>
                <span className="project-meta-date">
                    Created: {new Date(project.created_at).toLocaleDateString()}
                </span>
            </div>
        </div>
    );
};

export default ProjectCard;