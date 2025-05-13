import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
    Container,
    Paper,
    Box,
    Typography,
    TextField,
    Button,
    List,
    ListItem,
    ListItemText,
    Divider,
    CircularProgress,
    Alert,
    Snackbar,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { useAuth } from '../contexts/AuthContext';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const Chat = () => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isConnecting, setIsConnecting] = useState(false);
    const [error, setError] = useState('');
    const messagesEndRef = useRef(null);
    const wsRef = useRef(null);
    const { token } = useAuth();

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const connectWebSocket = useCallback(() => {
        if (!token) return;
        
        setIsConnecting(true);
        const wsUrl = `${API_URL.replace('http', 'ws')}/chat/ws?token=${token}`;
        const websocket = new WebSocket(wsUrl);

        websocket.onopen = () => {
            console.log('WebSocket connected');
            setIsConnecting(false);
            setError('');
        };

        websocket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                // Ensure data has the expected format
                if (data && typeof data.message === 'string') {
                    setMessages((prev) => [...prev, {
                        content: data.message,
                        is_bot: data.is_bot || false
                    }]);
                } else {
                    console.error('Invalid message format received:', data);
                }
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            if (error.message?.includes('401') || error.message?.includes('403')) {
                setError('Authentication failed. Please login again.');
                // Optionally redirect to login
            } else {
                setError('Failed to connect to chat server. Please try again later.');
            }
            setIsConnecting(false);
        };

        websocket.onclose = (event) => {
            console.log('WebSocket disconnected:', event.code, event.reason);
            if (event.code === 1008) { // Policy violation (authentication failed)
                setError('Authentication failed. Please login again.');
                // Optionally redirect to login
            }
            setIsConnecting(false);
        };

        wsRef.current = websocket;
    }, [token]);

    const fetchMessages = useCallback(async () => {
        if (!token) return;
        
        try {
            const response = await fetch(`${API_URL}/chat/messages`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                const data = await response.json();
                // Transform the data to match our frontend format
                const formattedMessages = data.map(msg => ({
                    content: msg.content,
                    is_bot: msg.is_bot
                }));
                setMessages(formattedMessages);
            } else if (response.status === 401) {
                setError('Session expired. Please login again.');
                // Optionally redirect to login
            } else {
                setError('Failed to fetch messages');
            }
        } catch (error) {
            console.error('Error fetching messages:', error);
            setError('Failed to fetch messages');
        }
    }, [token]);

    useEffect(() => {
        if (token) {
            connectWebSocket();
            fetchMessages();
        }
        return () => {
            if (wsRef.current) {
                wsRef.current.close();
                wsRef.current = null;
            }
        };
    }, [token, connectWebSocket, fetchMessages]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSendMessage = (e) => {
        e.preventDefault();
        if (!inputMessage.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

        const message = {
            message: inputMessage.trim(),
            is_bot: false
        };

        wsRef.current.send(JSON.stringify(message));
        setMessages((prev) => [...prev, {
            content: inputMessage.trim(),
            is_bot: false
        }]);
        setInputMessage('');
    };

    const handleCloseError = () => {
        setError('');
    };

    return (
        <Container maxWidth="sm" sx={{ height: 'calc(100vh - 64px)', py: 4 }}>
            <Paper 
                elevation={3} 
                sx={{ 
                    height: '100%', 
                    display: 'flex', 
                    flexDirection: 'column',
                    bgcolor: 'background.paper'
                }}
            >
                <Box sx={{ p: 2, bgcolor: 'primary.main', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Typography variant="h6">AI Chat Bot</Typography>
                    {isConnecting && (
                        <CircularProgress size={20} color="inherit" />
                    )}
                </Box>
                
                <List sx={{ 
                    flex: 1, 
                    overflow: 'auto', 
                    p: 2,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 1
                }}>
                    {messages.map((msg, index) => (
                        <ListItem 
                            key={index}
                            sx={{
                                alignSelf: msg.is_bot ? 'flex-start' : 'flex-end',
                                maxWidth: '80%'
                            }}
                        >
                            <Paper
                                elevation={1}
                                sx={{
                                    p: 2,
                                    bgcolor: msg.is_bot ? 'background.default' : 'primary.main',
                                    color: msg.is_bot ? 'text.primary' : 'white',
                                    borderRadius: 2
                                }}
                            >
                                <ListItemText primary={msg.content} />
                            </Paper>
                        </ListItem>
                    ))}
                    <div ref={messagesEndRef} />
                </List>

                <Divider />
                
                <Box 
                    component="form" 
                    onSubmit={handleSendMessage}
                    sx={{ 
                        p: 2, 
                        bgcolor: 'background.paper',
                        display: 'flex',
                        gap: 1
                    }}
                >
                    <TextField
                        fullWidth
                        variant="outlined"
                        placeholder="Type a message..."
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        size="small"
                        disabled={isConnecting || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN}
                    />
                    <Button 
                        type="submit" 
                        variant="contained" 
                        endIcon={<SendIcon />}
                        disabled={!inputMessage.trim() || isConnecting || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN}
                    >
                        Send
                    </Button>
                </Box>
            </Paper>

            <Snackbar 
                open={!!error} 
                autoHideDuration={6000} 
                onClose={handleCloseError}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            >
                <Alert onClose={handleCloseError} severity="error" sx={{ width: '100%' }}>
                    {error}
                </Alert>
            </Snackbar>
        </Container>
    );
};

export default Chat; 