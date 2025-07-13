import { useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import "./App.css";
import { ProjectList } from "./components/ProjectList";
import { ProjectDetailsPage } from "./components/ProjectDetailsPage";
import { TaskDetailsPage } from "./components/TaskDetailsPage";
import { UserList } from "./components/UserList";
import Navbar from "./components/Navbar";

function App() {
  const [username, setUsername] = useState("Developer"); // Default for now
  const [isLoggedIn, setIsLoggedIn] = useState(true); // Default for now

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
  };

  if (!isLoggedIn) {
    return (
      <div className="app">
        <h1>Agile Board - Login</h1>
        <div className="login-form">
          <div>
            Username:{" "}
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>
          <div>
            Password:{" "}
            <input
              type="password"
              placeholder="Password"
            />
          </div>
          <button onClick={handleLogin}>Login</button>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <Navbar
        appTitle="Agile Board"
        username={username}
        onLogout={handleLogout}
      />
      <main>
        <Routes>
          <Route path="/" element={<Navigate to="/projects" replace />} />
          <Route path="/projects" element={<ProjectList />} />
          <Route path="/projects/:id" element={<ProjectDetailsPage />} />
          <Route path="/projects/:projectId/tasks/:taskId" element={<TaskDetailsPage />} />
          <Route path="/users" element={<UserList />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
