document.addEventListener('DOMContentLoaded', () => {
    // Goals by Category Chart
    const goalsCtx = document.getElementById('goalsChart').getContext('2d');
    new Chart(goalsCtx, {
        type: 'bar',
        data: {
            labels: {{ categories | tojson }},
            datasets: [{
                label: 'Goals Completed',
                data: {{ goal_counts.values() | list | tojson }},
                backgroundColor: ['#36A2EB', '#FF6384', '#FFCE56', '#4BC0C0', '#9966FF']
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    // Points Over Time (Mock Data)
    const pointsCtx = document.getElementById('pointsChart').getContext('2d');
    new Chart(pointsCtx, {
        type: 'line',
        data: {
            labels: ['Apr 2025', 'May 2025', 'Jun 2025', 'Jul 2025'],
            datasets: [{
                label: 'Points Earned',
                data: [{{ progress.total_points / 4 }}, {{ progress.total_points / 2 }}, {{ progress.total_points * 3 / 4 }}, {{ progress.total_points }}],
                borderColor: '#36A2EB',
                fill: false
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
});
