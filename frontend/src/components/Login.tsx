import { useState } from "react";
import "./App.css";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = () => {};

  return (
    <>
      <h1>Login</h1>
      Username:{" "}
      <input type="textbox" onChange={(val) => setUsername(val.target.value)} />
      <br />
      Password:{" "}
      <input
        type="password"
        onChange={(val) => setPassword(val.target.value)}
      />
      <br />
      <button type="submit">Login</button>
    </>
  );
};

export default Login;
