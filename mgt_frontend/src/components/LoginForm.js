import { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import './App.css'; // Importing the CSS

function LoginForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post("http://127.0.0.1:8000/users/api/login/", {
        username,
        password,
      });

      const { access_token, role } = response.data;

      localStorage.setItem("access_token", access_token);


      if (role === "Administrator") {
        navigate("/AdminDashboard");
      } else if (role === "Manager") {
        navigate("/ManagerDashboard");
      } else if (role === "Employee") {
        navigate("/EmployeeDashboard");
      }
    } catch (error) {
      setError(
        error.response?.data?.error || "An error occurred. Please try again."
      );
      console.error("Login failed:", error);
    }
  };

  return (
    <div className="login-container">
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="username">Username:</label>
          <input
            type="text"
            id="username"
            name="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            name="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {error && <p style={{ color: "red" }}>{error}</p>}
        <button type="submit">Login</button>
      </form>
    </div>
  );
}

export default LoginForm;
