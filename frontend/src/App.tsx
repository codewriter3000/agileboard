import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
	const [username, setUsername] = useState('');
	const [password, setPassword] = useState('');

	const handleLogin = () => {
	};

  return (
    <>
			<h1>Login</h1>
			Username: <input type="textbox" onChange={val => setUsername(val)} /><br />
			Password: <input type="password" onChange={val => setPassword(val)} /><br />
			<button type="submit">Login</button>
    </>
  )
}

export default App
