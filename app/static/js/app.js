$(document).ready(function() {
    // Highlight active sidebar link
    $('.sidebar .nav-link').click(function() {
        $('.sidebar .nav-link').removeClass('active');
        $(this).addClass('active');
    });

    // Load Dashboard content
    window.loadDashboard = function() {
        $.get('/api/dashboard', function(data) {
            $('#main-content').html(`
                <div class="mt-4">
                    <h2>Dashboard</h2>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">Daily Progress</div>
                                <div class="card-body">
                                    <div class="d-flex justify-content-between align-items-center mb-3">
                                        <span><strong>Points:</strong> ${data.progress.total_points}</span>
                                        <span class="badge bg-primary">${data.progress.milestone}</span>
                                    </div>
                                    ${data.progress.last_checkin !== data.today ?
                                        `<form id="checkin-form">
                                            <button type="submit" class="btn btn-success w-100">Check In (+5 points)</button>
                                        </form>` :
                                        `<div class="alert alert-info text-center">Checked in today!</div>`
                                    }
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">Goals by Category</div>
                                <div class="card-body">
                                    <canvas id="goalsChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `);
            // Handle check-in form submission
            $('#checkin-form').submit(function(e) {
                e.preventDefault();
                $.post('/api/checkin', {}, function() {
                    loadDashboard();
                });
            });
            // Render goals chart
            const categories = {};
            data.goals.forEach(goal => {
                categories[goal.category] = (categories[goal.category] || 0) + 1;
            });
            const ctx = document.getElementById('goalsChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(categories),
                    datasets: [{
                        label: 'Goals by Category',
                        data: Object.values(categories),
                        backgroundColor: 'rgba(0, 123, 255, 0.5)',
                        borderColor: 'rgba(0, 123, 255, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: { beginAtZero: true, title: { display: true, text: 'Number of Goals' } },
                        x: { title: { display: true, text: 'Category' } }
                    }
                }
            });
        });
    };

    // Load Resources content
    window.loadResources = function() {
        $.get('/api/resources', function(data) {
            $('#main-content').html(`
                <div class="mt-4">
                    <h2>Resources</h2>
                    <div class="card">
                        <div class="card-header">Add Resource</div>
                        <div class="card-body">
                            <form id="resource-form">
                                <div class="mb-3">
                                    <label for="title" class="form-label">Title</label>
                                    <input type="text" class="form-control" id="title" name="title" required>
                                </div>
                                <div class="mb-3">
                                    <label for="url" class="form-label">URL</label>
                                    <input type="url" class="form-control" id="url" name="url">
                                </div>
                                <div class="mb-3">
                                    <label for="notes" class="form-label">Notes</label>
                                    <textarea class="form-control" id="notes" name="notes" rows="4"></textarea>
                                </div>
                                <div class="mb-3">
                                    <label for="category" class="form-label">Category</label>
                                    <input type="text" class="form-control" id="category" name="category" required>
                                </div>
                                <div class="mb-3">
                                    <label for="tags" class="form-label">Tags</label>
                                    <input type="text" class="form-control" id="tags" name="tags" placeholder="e.g., docker, security">
                                </div>
                                <button type="submit" class="btn btn-primary">Add Resource</button>
                            </form>
                        </div>
                    </div>
                    ${data.resources.length ? `
                        <div class="card">
                            <div class="card-header">Your Resources</div>
                            <div class="card-body">
                                <ul class="list-group list-group-flush">
                                    ${data.resources.map(r => `
                                        <li class="list-group-item">
                                            <div class="d-flex justify-content-between align-items-center">
                                                <div>
                                                    <strong>${r.title}</strong> <span class="badge bg-secondary">${r.category}</span><br>
                                                    ${r.url ? `<a href="${r.url}" target="_blank" class="text-primary">${r.url}</a><br>` : ''}
                                                    ${r.notes ? `<p class="mb-1">${r.notes}</p>` : ''}
                                                    ${r.tags ? `<small class="text-muted">Tags: ${r.tags}</small>` : ''}
                                                </div>
                                            </div>
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                        </div>
                    ` : ''}
                </div>
            `);
            $('#resource-form').submit(function(e) {
                e.preventDefault();
                $.post('/api/resources', $(this).serialize(), function() {
                    loadResources();
                });
            });
        });
    };

    // Load Goals content
    window.loadGoals = function() {
        $.get('/api/goals', function(data) {
            $('#main-content').html(`
                <div class="mt-4">
                    <h2>Goals</h2>
                    <div class="card">
                        <div class="card-header">Add Goal</div>
                        <div class="card-body">
                            <form id="goal-form">
                                <div class="mb-3">
                                    <label for="title" class="form-label">Title</label>
                                    <input type="text" class="form-control" id="title" name="title" required>
                                </div>
                                <div class="mb-3">
                                    <label for="deadline" class="form-label">Deadline</label>
                                    <input type="date" class="form-control" id="deadline" name="deadline">
                                </div>
                                <div class="mb-3">
                                    <label for="points" class="form-label">Points</label>
                                    <input type="number" class="form-control" id="points" name="points" value="10" required>
                                </div>
                                <div class="mb-3">
                                    <label for="category" class="form-label">Category</label>
                                    <input type="text" class="form-control" id="category" name="category" required>
                                </div>
                                <button type="submit" class="btn btn-primary">Add Goal</button>
                            </form>
                        </div>
                    </div>
                    ${data.goals.length ? `
                        <div class="card">
                            <div class="card-header">Your Goals</div>
                            <div class="card-body">
                                <ul class="list-group list-group-flush">
                                    ${data.goals.map(g => `
                                        <li class="list-group-item">
                                            <div class="d-flex justify-content-between align-items-center">
                                                <div>
                                                    <strong>${g.title}</strong> <span class="badge bg-secondary">${g.category}</span><br>
                                                    <small>Deadline: ${g.deadline || 'None'}</small><br>
                                                    <small>Points: ${g.points}</small><br>
                                                    <small>Status: ${g.status}</small>
                                                </div>
                                            </div>
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                        </div>
                    ` : ''}
                </div>
            `);
            $('#goal-form').submit(function(e) {
                e.preventDefault();
                $.post('/api/goals', $(this).serialize(), function() {
                    loadGoals();
                });
            });
        });
    };

    // Load Projects content
    window.loadProjects = function() {
        $.get('/api/projects', function(data) {
            $('#main-content').html(`
                <div class="mt-4">
                    <h2>Projects</h2>
                    <div class="card">
                        <div class="card-header">Add Project</div>
                        <div class="card-body">
                            <form id="project-form">
                                <div class="mb-3">
                                    <label for="title" class="form-label">Title</label>
                                    <input type="text" class="form-control" id="title" name="title" required>
                                </div>
                                <div class="mb-3">
                                    <label for="description" class="form-label">Description</label>
                                    <textarea class="form-control" id="description" name="description" rows="4"></textarea>
                                </div>
                                <div class="mb-3">
                                    <label for="repo_url" class="form-label">Repository URL</label>
                                    <input type="url" class="form-control" id="repo_url" name="repo_url">
                                </div>
                                <div class="mb-3">
                                    <label for="notes" class="form-label">Notes</label>
                                    <textarea class="form-control" id="notes" name="notes" rows="4"></textarea>
                                </div>
                                <div class="mb-3">
                                    <label for="points" class="form-label">Points</label>
                                    <input type="number" class="form-control" id="points" name="points" value="100" required>
                                </div>
                                <button type="submit" class="btn btn-primary">Add Project</button>
                            </form>
                        </div>
                    </div>
                    ${data.projects.length ? `
                        <div class="card">
                            <div class="card-header">Your Projects</div>
                            <div class="card-body">
                                <ul class="list-group list-group-flush">
                                    ${data.projects.map(p => `
                                        <li class="list-group-item">
                                            <div class="d-flex justify-content-between align-items-center">
                                                <div>
                                                    <strong>${p.title}</strong><br>
                                                    ${p.description ? `<p class="mb-1">${p.description}</p>` : ''}
                                                    ${p.repo_url ? `<a href="${p.repo_url}" target="_blank" class="text-primary">${p.repo_url}</a><br>` : ''}
                                                    <small>Points: ${p.points}</small><br>
                                                    <small>Status: ${p.completed ? 'Completed' : 'In Progress'}</small>
                                                </div>
                                            </div>
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                        </div>
                    ` : ''}
                </div>
            `);
            $('#project-form').submit(function(e) {
                e.preventDefault();
                $.post('/api/projects', $(this).serialize(), function() {
                    loadProjects();
                });
            });
        });
    };

    // Load Export content
    window.loadExport = function() {
        $.get('/api/export', function(data) {
            $('#main-content').html(`
                <div class="mt-4">
                    <h2>Export Data</h2>
                    <div class="card">
                        <div class="card-header">Export</div>
                        <div class="card-body">
                            <p>Download your data as JSON:</p>
                            <a href="data:text/json;charset=utf-8,${encodeURIComponent(JSON.stringify(data, null, 2))}" download="learning-tracker-data.json" class="btn btn-primary">Download JSON</a>
                        </div>
                    </div>
                </div>
            `);
        });
    };

    // Handle Import
    window.handleImport = function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const data = JSON.parse(e.target.result);
                $.post('/api/import', JSON.stringify(data), function() {
                    loadDashboard();
                }, 'json');
            };
            reader.readAsText(file);
        }
    };

    // Load Account content
    window.loadAccount = function() {
        $.get('/api/account', function(data) {
            $('#main-content').html(`
                <div class="mt-4">
                    <h2>Account</h2>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">Change Password</div>
                                <div class="card-body">
                                    <form id="password-form">
                                        <div class="mb-3">
                                            <label for="current_password" class="form-label">Current Password</label>
                                            <input type="password" class="form-control" id="current_password" name="current_password" required>
                                        </div>
                                        <div class="mb-3">
                                            <label for="new_password" class="form-label">New Password</label>
                                            <input type="password" class="form-control" id="new_password" name="new_password" required>
                                        </div>
                                        <button type="submit" class="btn btn-primary w-100">Update Password</button>
                                    </form>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">User Info</div>
                                <div class="card-body">
                                    <form id="info-form">
                                        <div class="mb-3">
                                            <label for="name" class="form-label">Name</label>
                                            <input type="text" class="form-control" id="name" name="name" value="${data.user_info?.name || ''}">
                                        </div>
                                        <div class="mb-3">
                                            <label for="address" class="form-label">Address</label>
                                            <textarea class="form-control" id="address" name="address" rows="4">${data.user_info?.address || ''}</textarea>
                                        </div>
                                        <button type="submit" class="btn btn-primary w-100">Update Info</button>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `);
            $('#password-form').submit(function(e) {
                e.preventDefault();
                $.post('/api/account/password', $(this).serialize(), function(response) {
                    if (response.success) {
                        $('#main-content').prepend('<div class="alert alert-success">Password updated</div>');
                    } else {
                        $('#main-content').prepend(`<div class="alert alert-danger">${response.error}</div>`);
                    }
                });
            });
            $('#info-form').submit(function(e) {
                e.preventDefault();
                $.post('/api/account/info', $(this).serialize(), function(response) {
                    if (response.success) {
                        $('#main-content').prepend('<div class="alert alert-success">Info updated</div>');
                    } else {
                        $('#main-content').prepend(`<div class="alert alert-danger">${response.error}</div>`);
                    }
                });
            });
        });
    };
});
