import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [user, setUser] = useState(null);

    useEffect(() => {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            setToken(storedToken);
            // You could also fetch user data here if needed
        }
    }, []);

    const login = async (email, password) => {
        try {
            const response = await fetch(
                `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/auth/login`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password }),
                }
            );
            if (response.ok) {
                const data = await response.json();
                setToken(data.access_token);
                localStorage.setItem('token', data.access_token);
                return true;
            } else {
                return false;
            }
        } catch (error) {
            return false;
        }
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('token');
    };

    const signup = async (email, username, password) => {
        try {
            const response = await fetch(
                `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/auth/signup`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, username, password }),
                }
            );
            return response.ok;
        } catch (error) {
            return false;
        }
    };

    return (
        <AuthContext.Provider value={{ token, user, login, logout, signup }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}; 