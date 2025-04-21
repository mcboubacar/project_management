// Fonction pour initialiser les tooltips Bootstrap
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Fonction pour confirmer les actions critiques (suppressions)
function initConfirmations() {
    document.querySelectorAll('a[data-confirm]').forEach(link => {
        link.addEventListener('click', (e) => {
            const message = link.getAttribute('data-confirm');
            if (!confirm(message || 'Êtes-vous sûr de vouloir effectuer cette action ?')) {
                e.preventDefault();
            }
        });
    });
}

// Fonction pour gérer les dates et délais
function initDateHandlers() {
    // Formatage des dates dans les tableaux
    document.querySelectorAll('.date-column').forEach(el => {
        if (el.textContent) {
            const date = new Date(el.textContent);
            el.textContent = date.toLocaleDateString('fr-FR');
        }
    });

    // Calcul des retards
    document.querySelectorAll('.task-row').forEach(row => {
        const deadlineStr = row.getAttribute('data-deadline');
        if (!deadlineStr) return;

        const deadline = new Date(deadlineStr);
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        if (deadline < today && !row.classList.contains('completed')) {
            row.classList.add('table-danger');
        }
    });
}

// Fonction pour gérer les barres de progression
function initProgressBars() {
    document.querySelectorAll('.progress-bar').forEach(bar => {
        const progress = parseInt(bar.style.width);
        if (progress < 30) {
            bar.classList.add('bg-danger');
        } else if (progress < 70) {
            bar.classList.add('bg-warning');
        } else {
            bar.classList.add('bg-success');
        }
    });
}

// Fonction pour les filtres de tableau
function initTableFilters() {
    document.querySelectorAll('.table-filter').forEach(filter => {
        filter.addEventListener('keyup', function() {
            const tableId = this.getAttribute('data-table');
            const table = document.getElementById(tableId);
            const filterText = this.value.toLowerCase();
            
            table.querySelectorAll('tbody tr').forEach(row => {
                const rowText = row.textContent.toLowerCase();
                row.style.display = rowText.includes(filterText) ? '' : 'none';
            });
        });
    });
}

// Initialisation des composants lorsque le DOM est chargé
document.addEventListener('DOMContentLoaded', function() {
    initTooltips();
    initConfirmations();
    initDateHandlers();
    initProgressBars();
    initTableFilters();

    // Gestion des messages flash (disparition après 5s)
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            const fade = new bootstrap.Collapse(alert, {
                toggle: false,
                hide: true
            });
            alert.addEventListener('closed.bs.collapse', () => alert.remove());
            fade.hide();
        });
    }, 5000);
});

// Fonctions utilitaires pour les requêtes AJAX
const ApiUtils = {
    async get(url) {
        const response = await fetch(url);
        return await response.json();
    },

    async post(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrf_token]')?.value
            },
            body: JSON.stringify(data)
        });
        return await response.json();
    },

    handleError(error) {
        console.error('API Error:', error);
        // Vous pourriez afficher une notification à l'utilisateur ici
    }
};

// Export pour les modules (si utilisation de modules ES6)
// export { ApiUtils };