import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const StudentDashboard = () => {
    const [profile, setProfile] = useState(null);
    const [enrolledClasses, setEnrolledClasses] = useState([]);
    const [upcomingQuizzes, setUpcomingQuizzes] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch student data
        fetchStudentData();
    }, []);

    const fetchStudentData = async () => {
        try {
            const [profileRes, classesRes, quizzesRes] = await Promise.all([
                fetch('/api/student/profile'),
                fetch('/api/student/classes'),
                fetch('/api/student/upcoming-quizzes')
            ]);

            const profileData = await profileRes.json();
            const classesData = await classesRes.json();
            const quizzesData = await quizzesRes.json();

            if (profileData.success) setProfile(profileData.profile);
            if (classesData.success) setEnrolledClasses(classesData.classes);
            if (quizzesData.success) setUpcomingQuizzes(quizzesData.quizzes);

        } catch (error) {
            console.error('Error fetching student data:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="d-flex justify-content-center align-items-center" style={{ height: '400px' }}>
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Loading...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="container-fluid">
            {/* Welcome Header */}
            <div className="text-center mb-5">
                <h1 className="display-4 mb-3">
                    <i className="fas fa-seedling text-success me-3"></i>
                    Hi, {profile?.full_name || profile?.username || 'Student'} 👋
                </h1>
                <p className="lead text-muted">
                    Welcome to your learning dashboard! Track your progress and discover new quizzes.
                </p>
            </div>

            {/* My Classes Section */}
            <div className="row mb-5">
                <div className="col-12">
                    <h3 className="mb-4">
                        <i className="fas fa-graduation-cap me-2"></i>My Classes
                    </h3>
                    <div className="row g-4">
                        <div className="col-md-6 col-lg-4">
                            <div className="card h-100 border-0 shadow-sm text-center">
                                <div className="card-body d-flex flex-column">
                                    <div className="mb-3">
                                        <i className="fas fa-graduation-cap fa-3x text-primary"></i>
                                    </div>
                                    <h5 className="card-title">Enroll in Classes</h5>
                                    <p className="card-text text-muted">
                                        Enroll in classes to access quizzes and start learning
                                    </p>
                                    <div className="mt-auto">
                                        <Link to="/my-classes" className="btn btn-primary w-100">
                                            <i className="fas fa-plus me-2"></i>Enroll Now
                                        </Link>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Upcoming Quizzes */}
            {upcomingQuizzes.length > 0 && (
                <div className="row mb-5">
                    <div className="col-12">
                        <h3 className="mb-4">
                            <i className="fas fa-clock me-2"></i>Upcoming Quizzes
                        </h3>
                        <div className="row g-3">
                            {upcomingQuizzes.slice(0, 5).map((quiz) => (
                                <div key={quiz.id} className="col-md-6 col-lg-4">
                                    <div className="card border-warning">
                                        <div className="card-body">
                                            <div className="d-flex justify-content-between align-items-start mb-2">
                                                <h6 className="card-title mb-0">{quiz.title}</h6>
                                                <span className={`badge ${
                                                    quiz.difficulty_level === 'beginner' ? 'bg-success' :
                                                    quiz.difficulty_level === 'intermediate' ? 'bg-warning' : 'bg-danger'
                                                }`}>
                                                    {quiz.difficulty_level?.charAt(0).toUpperCase() + quiz.difficulty_level?.slice(1)}
                                                </span>
                                            </div>
                                            <p className="card-text small text-muted mb-2">{quiz.subject_name}</p>
                                            <p className="card-text small mb-3">
                                                {quiz.description?.substring(0, 100)}
                                                {quiz.description?.length > 100 ? '...' : ''}
                                            </p>
                                            
                                            <div className="d-flex justify-content-between align-items-center">
                                                <small className="text-muted">
                                                    <i className="fas fa-calendar-times me-1"></i>
                                                    Due: {new Date(quiz.deadline).toLocaleDateString()} {new Date(quiz.deadline).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                                                </small>
                                                <Link 
                                                    to={`/take-quiz/${quiz.id}`} 
                                                    className="btn btn-warning btn-sm"
                                                >
                                                    <i className="fas fa-play me-1"></i>Take Quiz
                                                </Link>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Quick Actions */}
            <div className="row">
                <div className="col-12">
                    <div className="card border-0 shadow-sm">
                        <div className="card-body">
                            <h4 className="card-title mb-4">
                                <i className="fas fa-bolt me-2"></i>Quick Actions
                            </h4>
                            <div className="row g-3">
                                <div className="col-md-6">
                                    <Link to="/my-history" className="btn btn-outline-primary w-100">
                                        <i className="fas fa-history me-2"></i>View My History
                                    </Link>
                                </div>
                                <div className="col-md-6">
                                    <Link to="/profile" className="btn btn-outline-secondary w-100">
                                        <i className="fas fa-user me-2"></i>My Profile
                                    </Link>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default StudentDashboard;
