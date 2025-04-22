document.addEventListener('DOMContentLoaded', function() {
    // Sidebar Toggle
    const toggleBtn = document.querySelector('.toggle-sidebar');
    const menuBtn = document.querySelector('.menu-toggle');
    const body = document.body;
    
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            body.classList.toggle('sidebar-collapsed');
        });
    }
    
    if (menuBtn) {
        menuBtn.addEventListener('click', function() {
            body.classList.toggle('sidebar-active');
        });
    }
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (body.classList.contains('sidebar-active') && 
            !e.target.closest('.sidebar') && 
            !e.target.closest('.menu-toggle')) {
            body.classList.remove('sidebar-active');
        }
    });
    
    // Active menu item
    const currentPath = window.location.pathname;
    const menuLinks = document.querySelectorAll('.menu-link');
    
    menuLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || 
            (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        }
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (typeof bootstrap !== 'undefined') {
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Initialize datepickers
    const datepickers = document.querySelectorAll('.datepicker');
    datepickers.forEach(datepicker => {
        if (typeof flatpickr !== 'undefined') {
            flatpickr(datepicker, {
                dateFormat: "Y-m-d"
            });
        }
    });
    
    // Data table initialization
    const dataTable = document.getElementById('studentsTable');
    if (dataTable && typeof DataTable !== 'undefined') {
        new DataTable(dataTable, {
            responsive: true,
            pageLength: 10,
            language: {
                search: "",
                searchPlaceholder: "Search..."
            }
        });
    }
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Confirm Delete
    window.confirmDelete = function(id, name) {
        if (confirm(Are you sure you want to delete ${name || 'this item'}?)) {
            window.location.href = /delete_student/${id};
        }
    };
    
    // Flash message dismiss
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        const dismissBtn = message.querySelector('.dismiss-btn');
        if (dismissBtn) {
            dismissBtn.addEventListener('click', () => {
                message.remove();
            });
            
            // Auto dismiss after 5 seconds
            setTimeout(() => {
                message.classList.add('fade-out');
                setTimeout(() => message.remove(), 500);
            }, 5000);
        }
    });
    
    // Student photo preview (for file uploads)
    const photoInput = document.getElementById('photo');
    const photoPreview = document.getElementById('photoPreview');
    
    if (photoInput && photoPreview) {
        photoInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.addEventListener('load', function() {
                    photoPreview.style.backgroundImage = url(${this.result});
                    photoPreview.classList.add('has-image');
                });
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Simple Chart initializations (if charts exist on page)
    if (typeof Chart !== 'undefined') {
        // Attendance Overview Chart
        const attendanceCtx = document.getElementById('attendanceChart');
        if (attendanceCtx) {
            new Chart(attendanceCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Present', 'Absent', 'Leave'],
                    datasets: [{
                        data: [87, 10, 3],
                        backgroundColor: [
                            '#4CAF50',
                            '#F44336',
                            '#FFC107'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    cutout: '75%'
                }
            });
        }
        
        // Student Performance Chart
        const performanceCtx = document.getElementById('performanceChart');
        if (performanceCtx) {
            new Chart(performanceCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Performance',
                        data: [75, 82, 78, 85, 80, 88],
                        borderColor: '#4361ee',
                        backgroundColor: 'rgba(67, 97, 238, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }
        
        // Student Count by Course Chart
        const courseCtx = document.getElementById('courseChart');
        if (courseCtx) {
            new Chart(courseCtx, {
                type: 'bar',
                data: {
                    labels: ['BCA', 'MCA', 'B.Tech', 'M.Tech', 'BSc', 'MSc'],
                    datasets: [{
                        label: 'Students',
                        data: [45, 30, 60, 25, 35, 20],
                        backgroundColor: '#4895ef'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    }
    
    // Disable form submission if there are invalid fields
    (function() {
        'use strict';
        
        // Fetch all forms we want to apply validation to
        const forms = document.querySelectorAll('.needs-validation');
        
        // Loop over them and prevent submission
        Array.prototype.slice.call(forms).forEach(function(form) {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                
                form.classList.add('was-validated');
            }, false);
        });
    })();
});