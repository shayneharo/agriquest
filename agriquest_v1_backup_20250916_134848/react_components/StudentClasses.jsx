import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const StudentClasses = () => {
    const [enrolledClasses, setEnrolledClasses] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch student's enrolled classes
        fetchEnrolledClasses();
    }, []);

    const fetchEnrolledClasses = async () => {
        try {
            const response = await fetch('/api/student/classes');
            const data = await response.json();
            setEnrolledClasses(data.classes || []);
        } catch (error) {
            console.error('Error fetching classes:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleEnroll = async (classId) => {
        try {
            const response = await fetch(`/api/classes/${classId}/enroll`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            
            if (response.ok) {
                // Refresh classes list
                fetchEnrolledClasses();
                alert('Successfully enrolled in class!');
            } else {
                const error = await response.json();
                alert(error.message || 'Failed to enroll in class');
            }
        } catch (error) {
            console.error('Error enrolling in class:', error);
            alert('Failed to enroll in class');
        }
    };

    if (loading) {
        return (
            <div className="d-flex justify-content-center align-items-center" style={{ height: '200px' }}>
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Loading...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="container-fluid">
            <div className="row">
                <div className="col-12">
                    <div className="d-flex justify-content-between align-items-center mb-4">
                        <div>
                            <h2 className="mb-1">
                                <i className="fas fa-graduation-cap text-success me-2"></i>
                                My Classes
                            </h2>
                            <p className="text-muted mb-0">
                                Enroll in classes to access quizzes and start learning
                            </p>
                        </div>
                        <div>
                            <Link to="/classes" className="btn btn-outline-primary me-2">
                                <i className="fas fa-plus me-1"></i>Browse All Classes
                            </Link>
                            <Link to="/home" className="btn btn-outline-secondary">
                                <i className="fas fa-arrow-left me-1"></i>Back to Dashboard
                            </Link>
                        </div>
                    </div>

                    {enrolledClasses.length > 0 ? (
                        <div className="row">
                            {enrolledClasses.map((classItem) => (
                                <div key={classItem.id} className="col-lg-6 col-xl-4 mb-4">
                                    <div className="card h-100 shadow-sm border-0">
                                        <div className="card-body d-flex flex-column">
                                            <div className="d-flex justify-content-between align-items-start mb-3">
                                                <h5 className="card-title text-success mb-0">
                                                    <i className="fas fa-book me-2"></i>{classItem.name}
                                                </h5>
                                                <span className="badge bg-success">
                                                    <i className="fas fa-check me-1"></i>Enrolled
                                                </span>
                                            </div>
                                            
                                            {classItem.description && (
                                                <p className="card-text text-muted flex-grow-1">
                                                    {classItem.description}
                                                </p>
                                            )}
                                            
                                            <div className="mt-auto">
                                                <div className="d-flex justify-content-between align-items-center">
                                                    <small className="text-muted">
                                                        <i className="fas fa-calendar me-1"></i>
                                                        Enrolled {classItem.approved_at?.split(' ')[0] || 'Unknown'}
                                                    </small>
                                                    
                                                    <div className="btn-group" role="group">
                                                        <Link to="/subjects" className="btn btn-outline-success btn-sm">
                                                            <i className="fas fa-play me-1"></i>Take Quizzes
                                                        </Link>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="row justify-content-center">
                            <div className="col-md-8 col-lg-6">
                                <div className="card border-0 shadow-sm">
                                    <div className="card-body text-center py-5">
                                        <div className="mb-4">
                                            <i className="fas fa-graduation-cap fa-4x text-primary"></i>
                                        </div>
                                        <h4 className="card-title mb-3">Ready to Start Learning?</h4>
                                        <p className="card-text text-muted mb-4">
                                            Enroll in classes to access quizzes and start your agricultural learning journey!
                                        </p>
                                        <Link to="/classes" className="btn btn-primary btn-lg">
                                            <i className="fas fa-plus me-2"></i>Enroll in Classes
                                        </Link>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default StudentClasses;
