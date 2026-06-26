/**
 * Chart.js configurations for Student Result & Analytics Portal
 * Configured with elegant color schemes, fonts, and dark mode grid settings.
 */

// Helper to configure Chart.js defaults
if (typeof Chart !== 'undefined') {
    Chart.defaults.color = '#94a3b8'; // text-muted
    Chart.defaults.font.family = "'Outfit', sans-serif";
}

document.addEventListener('DOMContentLoaded', function () {
    // 1. TEACHER DASHBOARD: Pass/Fail Pie Chart
    const passFailEl = document.getElementById('passFailChart');
    if (passFailEl) {
        const passVal = parseInt(passFailEl.dataset.pass || 0);
        const failVal = parseInt(passFailEl.dataset.fail || 0);
        
        new Chart(passFailEl, {
            type: 'doughnut',
            data: {
                labels: ['Pass Prediction', 'Fail Prediction'],
                datasets: [{
                    data: [passVal, failVal],
                    backgroundColor: ['#10b981', '#ef4444'], // Emerald and Crimson
                    borderColor: '#1e293b',
                    borderWidth: 2,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            font: { size: 12, weight: '500' }
                        }
                    },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        titleColor: '#f8fafc',
                        bodyColor: '#f8fafc',
                        borderColor: 'rgba(255, 255, 255, 0.08)',
                        borderWidth: 1
                    }
                },
                cutout: '70%'
            }
        });
    }

    // 2. TEACHER DASHBOARD: Subject-wise Performance Comparison
    const subjectEl = document.getElementById('subjectChart');
    if (subjectEl) {
        try {
            const subjects = JSON.parse(subjectEl.dataset.subjects || '[]');
            const avgMids = JSON.parse(subjectEl.dataset.avgMid || '[]');
            const avgAssigns = JSON.parse(subjectEl.dataset.avgAssign || '[]');

            new Chart(subjectEl, {
                type: 'bar',
                data: {
                    labels: subjects,
                    datasets: [
                        {
                            label: 'Avg Mid-Term Marks',
                            data: avgMids,
                            backgroundColor: 'rgba(99, 102, 241, 0.75)', // Indigo
                            borderColor: '#6366f1',
                            borderWidth: 1,
                            borderRadius: 4
                        },
                        {
                            label: 'Avg Assignment Marks',
                            data: avgAssigns,
                            backgroundColor: 'rgba(6, 182, 212, 0.75)', // Cyan
                            borderColor: '#06b6d4',
                            borderWidth: 1,
                            borderRadius: 4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { font: { size: 11 } }
                        },
                        y: {
                            grid: { color: 'rgba(255, 255, 255, 0.05)' },
                            min: 0,
                            max: 100,
                            ticks: { font: { size: 11 } }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                font: { size: 12, weight: '500' },
                                boxWidth: 12
                            }
                        },
                        tooltip: {
                            backgroundColor: '#1e293b',
                            borderColor: 'rgba(255, 255, 255, 0.08)',
                            borderWidth: 1
                        }
                    }
                }
            });
        } catch (e) {
            console.error("Error drawing Teacher Dashboard charts:", e);
        }
    }

    // 3. STUDENT DASHBOARD: Individual Performance
    const studentPerformanceEl = document.getElementById('studentPerformanceChart');
    if (studentPerformanceEl) {
        try {
            const subjects = JSON.parse(studentPerformanceEl.dataset.subjects || '[]');
            const midMarks = JSON.parse(studentPerformanceEl.dataset.mids || '[]');
            const assignMarks = JSON.parse(studentPerformanceEl.dataset.assigns || '[]');

            new Chart(studentPerformanceEl, {
                type: 'line',
                data: {
                    labels: subjects,
                    datasets: [
                        {
                            label: 'Mid-Term Marks',
                            data: midMarks,
                            borderColor: '#6366f1',
                            backgroundColor: 'rgba(99, 102, 241, 0.1)',
                            fill: true,
                            tension: 0.3,
                            borderWidth: 3,
                            pointBackgroundColor: '#6366f1',
                            pointHoverRadius: 7
                        },
                        {
                            label: 'Assignment Marks',
                            data: assignMarks,
                            borderColor: '#06b6d4',
                            backgroundColor: 'rgba(6, 182, 212, 0.1)',
                            fill: true,
                            tension: 0.3,
                            borderWidth: 3,
                            pointBackgroundColor: '#06b6d4',
                            pointHoverRadius: 7
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            grid: { display: false }
                        },
                        y: {
                            grid: { color: 'rgba(255, 255, 255, 0.05)' },
                            min: 0,
                            max: 100
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                font: { size: 12, weight: '500' },
                                boxWidth: 12
                            }
                        },
                        tooltip: {
                            backgroundColor: '#1e293b',
                            borderColor: 'rgba(255, 255, 255, 0.08)',
                            borderWidth: 1
                        }
                    }
                }
            });
        } catch (e) {
            console.error("Error drawing Student Performance chart:", e);
        }
    }
});
