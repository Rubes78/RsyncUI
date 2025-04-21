function openBrowser(fieldId) {
    const iframe = document.getElementById('browserFrame');
    iframe.src = '/browse?path=/Quarks&field=' + encodeURIComponent(fieldId);
}
