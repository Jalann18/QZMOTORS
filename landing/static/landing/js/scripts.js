document.addEventListener('DOMContentLoaded', function() {
    // Navbar behavior on scroll
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(9, 9, 11, 0.95)';
            navbar.style.boxShadow = '0 10px 30px -10px rgba(0,0,0,0.5)';
        } else {
            navbar.style.background = 'rgba(9, 9, 11, 0.8)';
            navbar.style.boxShadow = 'none';
        }
    });

    // Form validation and Fetch
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('fecha').setAttribute('min', today);

    const form = document.getElementById('citaForm');
    const alertBox = document.getElementById('form-alert');
    const submitBtn = document.getElementById('submitBtn');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        alertBox.className = 'alert d-none rounded-3 border-0';
        
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Procesando Agenda Inmediata...';

        const data = {
            nombre: document.getElementById('nombre').value,
            telefono: document.getElementById('telefono').value,
            patente: document.getElementById('patente').value,
            comuna: document.getElementById('comuna').value,
            fecha: document.getElementById('fecha').value
        };

        try {
            const response = await fetch('/api/agendar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                alertBox.className = 'alert alert-success bg-success bg-opacity-10 text-success border-start border-success border-4';
                alertBox.innerHTML = '<strong><i class="bi bi-check-circle-fill me-2"></i>¡Agenda Confirmada!</strong><br>Nos contactaremos contigo a la brevedad.';
                form.reset();
            } else {
                alertBox.className = 'alert alert-danger bg-danger bg-opacity-10 text-danger border-start border-danger border-4';
                alertBox.innerHTML = '<strong><i class="bi bi-exclamation-triangle-fill me-2"></i>Error</strong><br>' + result.error;
            }
        } catch (error) {
            alertBox.className = 'alert alert-danger bg-danger bg-opacity-10 text-danger border-start border-danger border-4';
            alertBox.innerHTML = '<strong><i class="bi bi-wifi-off me-2"></i>Error de conexión</strong><br>Revisa tu internet e intenta nuevamente.';
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
            alertBox.classList.remove('d-none');
        }
    });

    // Scroll Reveal Observer
    const revealElements = document.querySelectorAll('.reveal-slide-up');
    
    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.15, // trigger when 15% is visible
        rootMargin: "0px 0px -50px 0px"
    });

    revealElements.forEach(el => {
        revealObserver.observe(el);
    });

});