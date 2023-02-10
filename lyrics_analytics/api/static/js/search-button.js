function submitForm() {
    var btn = document.getElementById('search-button');
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Searching ...';
    btn.setAttribute('disabled', 'disabled');
}