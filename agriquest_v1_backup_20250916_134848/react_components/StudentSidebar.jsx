import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

const StudentSidebar = ({ isOpen, onClose }) => {
    const location = useLocation();

    const menuItems = [
        {
            name: 'Home',
            path: '/home',
            icon: 'fas fa-home',
            section: 'main'
        },
        {
            name: 'My Classes',
            path: '/my-classes',
            icon: 'fas fa-graduation-cap',
            section: 'student'
        },
        {
            name: 'My Subjects',
            path: '/subjects',
            icon: 'fas fa-book',
            section: 'student'
        },
        {
            name: 'My History',
            path: '/my-history',
            icon: 'fas fa-history',
            section: 'student'
        },
        {
            name: 'Analytics',
            path: '/analytics',
            icon: 'fas fa-chart-line',
            section: 'account'
        },
        {
            name: 'My Profile',
            path: '/profile',
            icon: 'fas fa-user',
            section: 'account'
        }
    ];

    const isActive = (path) => {
        return location.pathname === path;
    };

    const getSectionTitle = (section) => {
        switch (section) {
            case 'student':
                return 'Student Menu';
            case 'account':
                return 'Account';
            default:
                return '';
        }
    };

    const groupedItems = menuItems.reduce((acc, item) => {
        if (!acc[item.section]) {
            acc[item.section] = [];
        }
        acc[item.section].push(item);
        return acc;
    }, {});

    return (
        <>
            {/* Overlay */}
            {isOpen && (
                <div 
                    className="sidebar-overlay show" 
                    onClick={onClose}
                ></div>
            )}

            {/* Sidebar */}
            <div className={`sidebar ${isOpen ? 'show' : ''}`} id="sidebar">
                <div className="sidebar-header">
                    <h5>
                        <i className="fas fa-seedling me-2"></i>AgriQuest Menu
                    </h5>
                    <button className="btn-close btn-close-white" onClick={onClose}></button>
                </div>
                <nav className="sidebar-nav">
                    {Object.entries(groupedItems).map(([section, items]) => (
                        <div key={section}>
                            {section !== 'main' && (
                                <>
                                    <hr className="sidebar-divider" />
                                    <h6 className="sidebar-section-title">
                                        {getSectionTitle(section)}
                                    </h6>
                                </>
                            )}
                            {items.map((item) => (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    className={`sidebar-link ${isActive(item.path) ? 'active' : ''}`}
                                    onClick={onClose}
                                >
                                    <i className={`${item.icon} me-2`}></i>
                                    {item.name}
                                </Link>
                            ))}
                        </div>
                    ))}
                </nav>
            </div>
        </>
    );
};

export default StudentSidebar;
