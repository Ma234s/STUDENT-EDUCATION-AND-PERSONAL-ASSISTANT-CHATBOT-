// Main JavaScript functionality for Naira

// Global variables
let currentUser = null;
let notifications = [];
let studyTimer = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadUserData();
});

// Application initialization
function initializeApp() {
    // Check authentication status
    checkAuth();
    
    // Initialize components
    initializeNotifications();
    initializeStudyTimer();
    initializeCharts();
    
    // Setup WebSocket connection if available
    setupWebSocket();
}

// Authentication check
function checkAuth() {
    fetch('/auth/check')
        .then(response => response.json())
        .then(data => {
            if (data.authenticated) {
                currentUser = data.user;
                updateUIForAuthenticatedUser();
            } else {
                updateUIForAnonymousUser();
            }
        })
        .catch(error => console.error('Auth check failed:', error));
}

// Event listeners setup
function setupEventListeners() {
    // Task management
    document.querySelectorAll('.task-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', handleTaskStatusChange);
    });
    
    // Study timer controls
    const timerControls = document.querySelectorAll('.timer-control');
    timerControls.forEach(control => {
        control.addEventListener('click', handleTimerControl);
    });
    
    // Form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmission);
    });
    
    // Notification permissions
    if ('Notification' in window) {
        Notification.requestPermission();
    }
}

// Task management
function handleTaskStatusChange(event) {
    const taskId = event.target.dataset.taskId;
    const completed = event.target.checked;
    
    updateTaskStatus(taskId, completed)
        .then(response => {
            if (response.success) {
                updateTaskUI(taskId, completed);
            }
        })
        .catch(error => console.error('Task update failed:', error));
}

function updateTaskStatus(taskId, completed) {
    return fetch('/api/tasks/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            task_id: taskId,
            completed: completed
        })
    }).then(response => response.json());
}

function updateTaskUI(taskId, completed) {
    const taskElement = document.querySelector(`#task-${taskId}`);
    if (taskElement) {
        taskElement.classList.toggle('completed', completed);
        
        // Update progress bars
        updateProgressBars();
    }
}

// Study timer functionality
function initializeStudyTimer() {
    studyTimer = {
        duration: 25 * 60, // 25 minutes in seconds
        timeLeft: 25 * 60,
        active: false,
        interval: null
    };
    
    updateTimerDisplay();
}

function handleTimerControl(event) {
    const action = event.target.dataset.action;
    
    switch (action) {
        case 'start':
            startTimer();
            break;
        case 'pause':
            pauseTimer();
            break;
        case 'reset':
            resetTimer();
            break;
    }
}

function startTimer() {
    if (!studyTimer.active) {
        studyTimer.active = true;
        studyTimer.interval = setInterval(() => {
            studyTimer.timeLeft--;
            updateTimerDisplay();
            
            if (studyTimer.timeLeft <= 0) {
                timerComplete();
            }
        }, 1000);
        
        updateTimerControls('running');
    }
}

function pauseTimer() {
    if (studyTimer.active) {
        studyTimer.active = false;
        clearInterval(studyTimer.interval);
        updateTimerControls('paused');
    }
}

function resetTimer() {
    pauseTimer();
    studyTimer.timeLeft = studyTimer.duration;
    updateTimerDisplay();
    updateTimerControls('reset');
}

function timerComplete() {
    pauseTimer();
    showNotification('Study Session Complete', 'Great job! Take a break.');
    logStudySession();
}

// Notifications
function initializeNotifications() {
    if ('Notification' in window && Notification.permission === 'granted') {
        setupNotificationChecks();
    }
}

function showNotification(title, message) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, {
            body: message,
            icon: '/static/img/logo.png'
        });
    }
}

// WebSocket handling
function setupWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    ws.onclose = function() {
        setTimeout(setupWebSocket, 5000); // Reconnect after 5 seconds
    };
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'task_update':
            updateTaskUI(data.task_id, data.completed);
            break;
        case 'new_message':
            handleNewMessage(data);
            break;
        case 'notification':
            showNotification(data.title, data.message);
            break;
    }
}

// Form handling
function handleFormSubmission(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    fetch(form.action, {
        method: form.method,
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            handleFormSuccess(form.id, data);
        } else {
            handleFormError(form.id, data);
        }
    })
    .catch(error => {
        console.error('Form submission failed:', error);
        handleFormError(form.id, { message: 'An error occurred' });
    });
}

// UI updates
function updateUIForAuthenticatedUser() {
    document.body.classList.add('authenticated');
    loadUserPreferences();
    loadTasks();
    loadStudySessions();
}

function updateUIForAnonymousUser() {
    document.body.classList.remove('authenticated');
}

function updateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const target = bar.dataset.target;
        const current = bar.dataset.current;
        const percentage = (current / target) * 100;
        bar.style.width = `${percentage}%`;
    });
}

// Data loading functions
function loadUserData() {
    Promise.all([
        fetch('/api/user/preferences').then(r => r.json()),
        fetch('/api/user/tasks').then(r => r.json()),
        fetch('/api/user/study-sessions').then(r => r.json())
    ])
    .then(([preferences, tasks, sessions]) => {
        applyUserPreferences(preferences);
        renderTasks(tasks);
        renderStudySessions(sessions);
    })
    .catch(error => console.error('Error loading user data:', error));
}

// Chart initialization
function initializeCharts() {
    // Initialize only if charts container exists
    const chartsContainer = document.getElementById('analytics-charts');
    if (!chartsContainer) return;
    
    // Study time distribution chart
    createStudyTimeChart();
    
    // Task completion chart
    createTaskCompletionChart();
    
    // Progress tracking chart
    createProgressChart();
}

// Utility functions
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
}

function updateTimerDisplay() {
    const display = document.getElementById('timer-display');
    if (display) {
        display.textContent = formatTime(studyTimer.timeLeft);
    }
}

function updateTimerControls(state) {
    const startBtn = document.querySelector('[data-action="start"]');
    const pauseBtn = document.querySelector('[data-action="pause"]');
    const resetBtn = document.querySelector('[data-action="reset"]');
    
    if (startBtn && pauseBtn && resetBtn) {
        switch (state) {
            case 'running':
                startBtn.disabled = true;
                pauseBtn.disabled = false;
                resetBtn.disabled = false;
                break;
            case 'paused':
                startBtn.disabled = false;
                pauseBtn.disabled = true;
                resetBtn.disabled = false;
                break;
            case 'reset':
                startBtn.disabled = false;
                pauseBtn.disabled = true;
                resetBtn.disabled = true;
                break;
        }
    }
}

// Error handling
function handleError(error, context = '') {
    console.error(`Error in ${context}:`, error);
    showNotification('Error', `An error occurred in ${context}`);
}

// Flash Message Handling
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
});

// Task Management
function updateTaskStatus(taskId, status) {
    fetch(`/api/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => response.json())
    .then(data => {
        // Update UI based on response
        const taskElement = document.querySelector(`#task-${taskId}`);
        if (taskElement) {
            if (status === 'completed') {
                taskElement.classList.add('completed');
            } else {
                taskElement.classList.remove('completed');
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) return;

    fetch(`/api/tasks/${taskId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (response.ok) {
            const taskElement = document.querySelector(`#task-${taskId}`);
            if (taskElement) {
                taskElement.remove();
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

// Study Session Management
let activeSession = null;
let sessionTimer = null;

function startStudySession(subject) {
    fetch('/api/study-sessions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ subject: subject })
    })
    .then(response => response.json())
    .then(data => {
        activeSession = data;
        updateTimerDisplay();
        sessionTimer = setInterval(updateTimerDisplay, 1000);
    })
    .catch(error => console.error('Error:', error));
}

function endStudySession() {
    if (!activeSession) return;

    fetch(`/api/study-sessions/${activeSession.id}/end`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        clearInterval(sessionTimer);
        activeSession = null;
        updateTimerDisplay();
    })
    .catch(error => console.error('Error:', error));
}

function updateTimerDisplay() {
    const timerDisplay = document.getElementById('session-timer');
    if (!timerDisplay || !activeSession) return;

    const startTime = new Date(activeSession.start_time);
    const now = new Date();
    const duration = Math.floor((now - startTime) / 1000); // Duration in seconds

    const hours = Math.floor(duration / 3600);
    const minutes = Math.floor((duration % 3600) / 60);
    const seconds = duration % 60;

    timerDisplay.textContent = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

// Form Validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');

    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('is-invalid');
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Password Strength Checker
function checkPasswordStrength(password) {
    let strength = 0;
    const feedback = [];

    if (password.length < 8) {
        feedback.push('Password should be at least 8 characters long');
    } else {
        strength += 1;
    }

    if (password.match(/[a-z]/)) strength += 1;
    if (password.match(/[A-Z]/)) strength += 1;
    if (password.match(/[0-9]/)) strength += 1;
    if (password.match(/[^a-zA-Z0-9]/)) strength += 1;

    if (strength < 3) {
        feedback.push('Consider adding uppercase letters, numbers, or special characters');
    }

    return {
        score: strength,
        feedback: feedback
    };
}

// Responsive Navigation
document.addEventListener('DOMContentLoaded', function() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');

    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });

        // Close navbar when clicking outside
        document.addEventListener('click', function(event) {
            const isClickInside = navbarToggler.contains(event.target) || navbarCollapse.contains(event.target);
            if (!isClickInside && navbarCollapse.classList.contains('show')) {
                navbarCollapse.classList.remove('show');
            }
        });
    }
});

// Remove WebSocket connection attempts
document.addEventListener('DOMContentLoaded', function() {
    // Initialize any UI components
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 3000);
    });
});

// Handle form submissions
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = 'Processing...';
        }
    });
}); 