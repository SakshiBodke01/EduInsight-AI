/**
 * General UI Enhancements
 * Auto-dismiss alerts, active states, custom file uploads dropzone styling.
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Auto-dismiss alerts after 4 seconds
    const alerts = document.querySelectorAll('.alert-custom');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(100%)';
            setTimeout(function () {
                alert.remove();
            }, 500);
        }, 4000);

        // Manual close trigger
        const closeBtn = alert.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function () {
                alert.style.opacity = '0';
                alert.style.transform = 'translateX(100%)';
                setTimeout(function () {
                    alert.remove();
                }, 300);
            });
        }
    });

    // 2. Drag & Drop CSV Uploader Visual Updates
    const dropzone = document.getElementById('csvDropzone');
    const fileInput = document.getElementById('csvFileInput');
    
    if (dropzone && fileInput) {
        // Trigger file open when clicking dropzone
        dropzone.addEventListener('click', () => fileInput.click());

        // Visual states on drag
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.style.borderColor = 'var(--accent-secondary)';
                dropzone.style.backgroundColor = 'rgba(6, 182, 212, 0.08)';
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.style.borderColor = 'var(--glass-border)';
                dropzone.style.backgroundColor = 'rgba(30, 41, 59, 0.3)';
            }, false);
        });

        // Drop handling
        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                fileInput.files = files;
                updateDropzoneText(files[0].name);
            }
        });

        // Manual select file change
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                updateDropzoneText(fileInput.files[0].name);
            }
        });
        
        function updateDropzoneText(fileName) {
            const textHeader = dropzone.querySelector('.dropzone-text h3');
            const textDesc = dropzone.querySelector('.dropzone-text p');
            const icon = dropzone.querySelector('.dropzone-icon');
            
            if (textHeader && textDesc && icon) {
                textHeader.textContent = "File Selected";
                textDesc.textContent = `${fileName} ready for submission.`;
                textDesc.style.color = 'var(--accent-secondary)';
                icon.style.color = 'var(--accent-secondary)';
                icon.textContent = '✓';
            }
        }
    }
});
