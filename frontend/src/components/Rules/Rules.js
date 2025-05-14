import React, { useState, useEffect, useCallback } from 'react';
import { rulesService } from '../../services/rulesService';
import {
    Box,
    Button,
    Card,
    CardContent,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    Typography,
    List,
    ListItem,
    ListItemText,
    ListItemSecondaryAction,
    IconButton,
    Snackbar,
    Alert
} from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon, Add as AddIcon } from '@mui/icons-material';

const Rules = () => {
    const [rules, setRules] = useState([]);
    const [openDialog, setOpenDialog] = useState(false);
    const [currentRule, setCurrentRule] = useState({ name: '', description: '', pattern: '' });
    const [isEditing, setIsEditing] = useState(false);
    const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

    const loadRules = useCallback(async () => {
        try {
            const data = await rulesService.getAllRules();
            setRules(data);
        } catch (error) {
            showSnackbar('Error loading rules: ' + error.message, 'error');
        }
    }, []);

    useEffect(() => {
        loadRules();
    }, [loadRules]);

    const handleOpenDialog = (rule = null) => {
        if (rule) {
            setCurrentRule(rule);
            setIsEditing(true);
        } else {
            setCurrentRule({ name: '', description: '', pattern: '' });
            setIsEditing(false);
        }
        setOpenDialog(true);
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
        setCurrentRule({ name: '', description: '', pattern: '' });
        setIsEditing(false);
    };

    const handleSubmit = async () => {
        try {
            if (isEditing) {
                await rulesService.updateRule(currentRule.id, currentRule);
                showSnackbar('Rule updated successfully');
            } else {
                await rulesService.createRule(currentRule);
                showSnackbar('Rule created successfully');
            }
            handleCloseDialog();
            loadRules();
        } catch (error) {
            showSnackbar('Error saving rule: ' + error.message, 'error');
        }
    };

    const handleDelete = async (ruleId) => {
        try {
            await rulesService.deleteRule(ruleId);
            showSnackbar('Rule deleted successfully');
            loadRules();
        } catch (error) {
            showSnackbar('Error deleting rule: ' + error.message, 'error');
        }
    };

    const showSnackbar = (message, severity = 'success') => {
        setSnackbar({ open: true, message, severity });
    };

    const handleCloseSnackbar = () => {
        setSnackbar({ ...snackbar, open: false });
    };

    return (
        <Box sx={{ maxWidth: 800, margin: '0 auto', padding: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" component="h1">
                    Rules Management
                </Typography>
                <Button
                    variant="contained"
                    color="primary"
                    startIcon={<AddIcon />}
                    onClick={() => handleOpenDialog()}
                >
                    Add Rule
                </Button>
            </Box>

            <Card>
                <CardContent>
                    <List>
                        {rules.map((rule) => (
                            <ListItem key={rule.id} divider>
                                <ListItemText
                                    primary={rule.name}
                                    secondary={
                                        <>
                                            <Typography component="span" variant="body2" color="textPrimary">
                                                {rule.description}
                                            </Typography>
                                            <br />
                                            <Typography component="span" variant="body2" color="textSecondary">
                                                Pattern: {rule.pattern}
                                            </Typography>
                                        </>
                                    }
                                />
                                <ListItemSecondaryAction>
                                    <IconButton edge="end" onClick={() => handleOpenDialog(rule)}>
                                        <EditIcon />
                                    </IconButton>
                                    <IconButton edge="end" onClick={() => handleDelete(rule.id)}>
                                        <DeleteIcon />
                                    </IconButton>
                                </ListItemSecondaryAction>
                            </ListItem>
                        ))}
                    </List>
                </CardContent>
            </Card>

            <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
                <DialogTitle>{isEditing ? 'Edit Rule' : 'Add New Rule'}</DialogTitle>
                <DialogContent>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Rule Name"
                        fullWidth
                        value={currentRule.name}
                        onChange={(e) => setCurrentRule({ ...currentRule, name: e.target.value })}
                    />
                    <TextField
                        margin="dense"
                        label="Description"
                        fullWidth
                        multiline
                        rows={2}
                        value={currentRule.description}
                        onChange={(e) => setCurrentRule({ ...currentRule, description: e.target.value })}
                    />
                    <TextField
                        margin="dense"
                        label="Pattern"
                        fullWidth
                        value={currentRule.pattern}
                        onChange={(e) => setCurrentRule({ ...currentRule, pattern: e.target.value })}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog}>Cancel</Button>
                    <Button onClick={handleSubmit} variant="contained" color="primary">
                        {isEditing ? 'Update' : 'Create'}
                    </Button>
                </DialogActions>
            </Dialog>

            <Snackbar
                open={snackbar.open}
                autoHideDuration={6000}
                onClose={handleCloseSnackbar}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            >
                <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </Box>
    );
};

export default Rules; 