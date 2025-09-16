import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import StudentDashboard from './StudentDashboard';
import StudentClasses from './StudentClasses';
import StudentSidebar from './StudentSidebar';

const App = () => {
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [userRole, setUserRole] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check authentication status
        checkAuthStatus();
    }, []);

    const checkAuthStatus = async () => {
        try {
            const response = await fetch('/api/auth/status');
            const data = await response.json();
            
            if (data.success && data.authenticated) {
                setIsAuthenticated(true);
                setUserRole(data.user.role);
            }
        } catch (error) {
            console.error('Error checking auth status:', error);
        } finally {
            setLoading(false);
        }
    };

    const toggleSidebar = () => {
        setIsSidebarOpen(!isSidebarOpen);
    };

    const closeSidebar = () => {
        setIsSidebarOpen(false);
    };

    if (loading) {
        return (
            <div className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Loading...</span>
                </div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    return (
        <Router>
            <div className="App">
                {/* Navigation Bar */}
                <nav className="navbar navbar-expand-lg navbar-dark bg-success">
                    <div className="container-fluid">
                        {/* Hamburger Menu Button */}
                        <button 
                            className="btn btn-outline-light me-3" 
                            id="hamburgerToggle"
                            onClick={toggleSidebar}
                            title="Menu"
                        >
                            <i className="fas fa-bars"></i>
                        </button>
                        
                        {/* Brand */}
                        <a className="navbar-brand" href="/home">
                            <i className="fas fa-seedling me-2"></i>AgriQuest
                        </a>
                        
                        {/* Right side navigation */}
                        <div className="ms-auto d-flex align-items-center">
                            {/* Dark Mode Toggle */}
                            <button className="btn btn-outline-light me-2" title="Toggle Dark Mode">
                                <i className="fas fa-moon"></i>
                            </button>
                            
                            {/* Notification Bell */}
                            <button className="btn btn-outline-light me-2" title="Notifications">
                                <i className="fas fa-bell"></i>
                            </button>
                            
                            {/* User Dropdown */}
                            <div className="dropdown">
                                <button className="btn btn-outline-light dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                    <i className="fas fa-user me-1"></i>Student
                                </button>
                                <ul className="dropdown-menu dropdown-menu-end">
                                    <li><span className="dropdown-item-text">
                                        <small className="text-muted">Student</small>
                                    </span></li>
                                    <li><hr className="dropdown-divider" /></li>
                                    <li><a className="dropdown-item" href="/profile">
                                        <i className="fas fa-user me-2"></i>My Profile
                                    </a></li>
                                    <li><hr className="dropdown-divider" /></li>
                                    <li><a className="dropdown-item" href="/logout">
                                        <i className="fas fa-sign-out-alt me-2"></i>Logout
                                    </a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </nav>

                {/* Sidebar */}
                <StudentSidebar isOpen={isSidebarOpen} onClose={closeSidebar} />

                {/* Main Content */}
                <main className="container mt-4">
                    <Routes>
                        <Route path="/home" element={<StudentDashboard />} />
                        <Route path="/my-classes" element={<StudentClasses />} />
                        <Route path="/subjects" element={<div>Subjects Page</div>} />
                        <Route path="/my-history" element={<div>History Page</div>} />
                        <Route path="/analytics" element={<div>Analytics Page</div>} />
                        <Route path="/profile" element={<div>Profile Page</div>} />
                        <Route path="/" element={<Navigate to="/home" replace />} />
                    </Routes>
                </main>

                {/* Footer */}
                <footer className="bg-light text-center text-muted py-3 mt-5">
                    <div className="container">
                        <p>&copy; 2024 AgriQuest - Agricultural Knowledge Platform</p>
                    </div>
                </footer>
            </div>
        </Router>
    );
};

export default App;
