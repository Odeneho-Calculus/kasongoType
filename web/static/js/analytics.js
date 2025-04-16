document.addEventListener('DOMContentLoaded', function () {
    // Load user stats when dashboard page loads
    loadUserStats();
});

/**
 * Load user statistics from the API
 */
function loadUserStats() {
    console.log("Loading user statistics...");
    fetch('/api/user/stats')
        .then(response => response.json())
        .then(data => {
            console.log("Received user stats data:", data);
            if (data.status === 'success') {
                displayStats(data.stats);
                displayRecentSessions(data.recent_sessions);


            } else {
                console.error('Failed to load user statistics:', data.message);
            }
        })
        .catch(error => {
            console.error('Error loading user statistics:', error);
        });
}

/**
 * Display user statistics in the dashboard
 */
function displayStats(stats) {
    if (!stats) {
        console.warn("No stats data available");
        document.getElementById('best-wpm').textContent = '0.0';
        document.getElementById('avg-wpm').textContent = '0.0';
        document.getElementById('avg-accuracy').textContent = '0.0%';
        document.getElementById('total-sessions').textContent = '0';
        return;
    }

    document.getElementById('best-wpm').textContent = (stats.best_wpm || 0).toFixed(1);
    document.getElementById('avg-wpm').textContent = (stats.average_wpm || 0).toFixed(1);
    document.getElementById('avg-accuracy').textContent = (stats.accuracy || 0).toFixed(1) + '%';
    document.getElementById('total-sessions').textContent = stats.exercises_completed || 0;
}

/**
 * Display recent typing sessions in the table
 */
function displayRecentSessions(sessions) {
    const tableBody = document.getElementById('sessions-table');
    tableBody.innerHTML = '';

    if (!sessions || sessions.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="5">No sessions recorded yet</td>';
        tableBody.appendChild(row);
        return;
    }

    sessions.forEach(session => {
        const row = document.createElement('tr');

        // Format date
        const date = new Date(session.timestamp);
        const formattedDate = `${date.toLocaleDateString()} ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;

        row.innerHTML = `
            <td>${formattedDate}</td>
            <td>${session.exercise_id || 'Unknown'}</td>
            <td>${(session.wpm || 0).toFixed(1)}</td>
            <td>${(session.accuracy || 0).toFixed(1)}%</td>
            <td>${(session.time_elapsed || 0).toFixed(1)}s</td>
        `;

        tableBody.appendChild(row);
    });
}
