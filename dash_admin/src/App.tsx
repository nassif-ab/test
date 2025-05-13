import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./content/AuthProvider";

// Componentes de layout
import AdminLayout from "./components/AdminLayout";

// Páginas
import Dashboard from "./pages/Dashboard";
import Users from "./pages/Users";
import Posts from "./pages/Posts";
import Stats from "./pages/Stats";
import Login from "./pages/Login";

function App() {
  const { isAuthenticated } = useAuth();

  return (
    <Router>
      <Routes>
        {/* Ruta de inicio de sesión */}
        <Route path="/login" element={<Login />} />
        
        {/* Rutas protegidas del panel de administración */}
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="users" element={<Users />} />
          <Route path="posts" element={<Posts />} />
          <Route path="stats" element={<Stats />} />
        </Route>
        
        {/* Redirección a la página principal o al login */}
        <Route path="*" element={<Navigate to={isAuthenticated ? "/admin" : "/login"} />} />
      </Routes>
    </Router>
  );
}

export default App;