document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('courseProgressChart').getContext('2d');
    const courseProgress = JSON.parse(document.getElementById('courseProgressData').textContent);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: courseProgress.map(item => item.course),
            datasets: [{
                label: 'Course Progress',
                data: courseProgress.map(item => item.progress),
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
});
