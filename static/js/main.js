// ===== Dark Mode Toggle =====
const darkModeToggle = document.getElementById('darkModeToggle');

if (darkModeToggle) {
    darkModeToggle.addEventListener('click', function() {
        const isDark = document.documentElement.classList.toggle('dark');
        localStorage.setItem('darkMode', isDark);
        updateDarkModeIcon();
    });

    function updateDarkModeIcon() {
        const isDark = document.documentElement.classList.contains('dark');
        darkModeToggle.textContent = isDark ? '☀️' : '🌙';
    }

    updateDarkModeIcon();
}

// ===== Auto-dismiss alerts =====
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('[role="alert"]');
    alerts.forEach((alert, index) => {
        setTimeout(() => {
            alert.style.animation = 'fade-in 0.3s reverse';
            setTimeout(() => alert.remove(), 300);
        }, 4000 + (index * 500));
    });
});

// ===== Price Calculation on Book Page =====
function initPriceCalculation() {
    const cargoTypeSelect = document.querySelector('select[name="cargo_type"]');
    const weightInput = document.querySelector('input[name="weight_kg"]');
    
    if (cargoTypeSelect && weightInput) {
        cargoTypeSelect.addEventListener('change', updatePrice);
        weightInput.addEventListener('input', updatePrice);
    }
}

function updatePrice() {
    const cargoType = document.querySelector('select[name="cargo_type"]')?.value;
    const weight = parseFloat(document.querySelector('input[name="weight_kg"]')?.value) || 0;
    
    if (cargoType && weight > 0) {
        fetch(`/api/calculate-price/?cargo_type=${cargoType}&weight=${weight}`)
            .then(r => r.json())
            .then(data => {
                const pricePerKg = document.getElementById('pricePerKg');
                const totalPrice = document.getElementById('totalPrice');
                if (pricePerKg) pricePerKg.textContent = `$${data.price_per_kg.toFixed(2)}`;
                if (totalPrice) totalPrice.textContent = `$${data.total_price.toFixed(2)}`;
            })
            .catch(err => console.error('Error fetching price:', err));
    } else {
        const pricePerKg = document.getElementById('pricePerKg');
        const totalPrice = document.getElementById('totalPrice');
        if (pricePerKg) pricePerKg.textContent = '$0.00';
        if (totalPrice) totalPrice.textContent = '$0.00';
    }
}

// ===== Form Validation =====
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
            let isValid = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    input.classList.add('border-red-500');
                    isValid = false;
                } else {
                    input.classList.remove('border-red-500');
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });
    });
}

// ===== Search Highlight =====
function initSearchHighlight() {
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const tables = document.querySelectorAll('table tbody tr');
            const query = this.value.toLowerCase();

            tables.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.opacity = text.includes(query) ? '1' : '0.4';
            });
        });
    }
}

// ===== Modal Interactions =====
function initModal() {
    const modals = document.querySelectorAll('[role="dialog"]');
    modals.forEach(modal => {
        const closeBtn = modal.querySelector('[data-close]');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => modal.style.display = 'none');
        }

        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
}

// ===== Smooth Scroll Links =====
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    });
}

// ===== Initialize Everything =====
document.addEventListener('DOMContentLoaded', function() {
    initPriceCalculation();
    initFormValidation();
    initSearchHighlight();
    initModal();
    initSmoothScroll();

    // ✅ FIXED: listen to form 'submit' event, not button 'click'
    // Disabling a button inside 'click' cancels form submission in Chrome
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const btn = form.querySelector('button[type="submit"]');
            if (btn) {
                const originalText = btn.textContent;
                btn.disabled = true;
                btn.style.opacity = '0.7';
                btn.textContent = '⏳ Loading...';

                // Re-enable after 5s in case server returns validation errors
                setTimeout(() => {
                    btn.disabled = false;
                    btn.style.opacity = '1';
                    btn.textContent = originalText;
                }, 5000);
            }
        });
    });
});

// ===== Detect Network Status =====
window.addEventListener('online', () => {
    console.log('Connection restored');
});

window.addEventListener('offline', () => {
    console.warn('Connection lost');
});