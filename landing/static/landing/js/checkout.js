document.addEventListener('DOMContentLoaded', () => {
    // 1. Parsing URL params to check Selected Plan
    const urlParams = new URLSearchParams(window.location.search);
    const plan = urlParams.get('plan');
    
    // Default values
    let planTitle = "Plan Desconocido";
    let planPrice = "$0 CLP";
    
    // Feature Lists matching index.html
    const features = {
        'scanner': [
            'Diagnóstico Electrónico',
            'Lectura de fallas ECU',
            'Reporte digital'
        ],
        'completa': [
            'Diagnóstico Electrónico Global',
            'Prueba de compresión/motor',
            'Revisión de pintura y chasis',
            'Validación real de Kilometraje',
            '<span class="text-warning fw-bold">Asesoría y Certificación</span>'
        ],
        'promo_2x1': [
            '<span class="text-success fw-bold">✔ Incluye 2 inspecciones completas</span>',
            'Diagnóstico Electrónico Global',
            'Prueba de compresión/motor',
            'Revisión de pintura y chasis',
            'Validación real de Kilometraje',
            '<span class="text-warning fw-bold">Asesoría y Certificación</span>'
        ]
    };
    
    // Mapping 
    if (plan === 'scanner') {
        planTitle = "Scanner Automotriz";
        planPrice = "$30.000";
    } else if (plan === 'completa') {
        planTitle = "Inspección Completa 360°";
        planPrice = "$65.000";
    } else if (plan === 'promo_2x1') {
        planTitle = "Promo 2x1: Inspección Completa";
        planPrice = "$100.000";
    }

    // Set UI Details
    document.querySelectorAll('.summary-title').forEach(el => el.innerText = planTitle);
    document.querySelectorAll('.summary-price').forEach(el => el.innerText = planPrice);
    document.querySelectorAll('.summary-total').forEach(el => el.innerText = planPrice);

    // Inject Features
    const planFeatures = features[plan] || features['scanner'];
    let featureHtml = '<ul class="list-unstyled text-start m-0">';
    planFeatures.forEach((feat, index) => {
        const isLast = index === planFeatures.length - 1;
        const borderClass = isLast ? '' : 'border-bottom border-secondary border-opacity-25 pb-3 mb-3';
        
        if(feat.includes('✔')) {
            let cleanFeat = feat.replace('<span class="text-success fw-bold">', '').replace('</span>', '');
            featureHtml += `<li class="p-3 rounded-3 text-center mb-4 shadow-sm" style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2);"><span class="fs-6" style="color: #10b981; font-weight: 600;">${cleanFeat}</span></li>`;
        } else {
            featureHtml += `<li class="d-flex align-items-center ${borderClass}">
                                <div class="d-flex align-items-center justify-content-center me-3 flex-shrink-0" style="width: 24px; height: 24px; background: rgba(16, 185, 129, 0.15); border-radius: 6px;">
                                    <i class="bi bi-check-lg" style="color: #10b981; font-size: 1.1rem; text-shadow: 0 0 8px rgba(16, 185, 129, 0.4);"></i>
                                </div>
                                <span class="text-light fw-medium" style="line-height: 1.4;">${feat}</span>
                            </li>`;
        }
    });
    featureHtml += '</ul>';
    document.querySelectorAll('.summary-features').forEach(el => el.innerHTML = featureHtml);

    // Populate RM Comunas
    const comunasRM = [
        "Cerrillos", "Cerro Navia", "Conchalí", "El Bosque", "Estación Central", 
        "Huechuraba", "Independencia", "La Cisterna", "La Florida", "La Granja", 
        "La Pintana", "La Reina", "Las Condes", "Lo Barnechea", "Lo Espejo", 
        "Lo Prado", "Macul", "Maipú", "Ñuñoa", "Pedro Aguirre Cerda", "Peñalolén", 
        "Providencia", "Pudahuel", "Quilicura", "Quinta Normal", "Recoleta", 
        "Renca", "San Joaquín", "San Miguel", "San Ramón", "Santiago", "Vitacura", 
        "Puente Alto", "Pirque", "San José de Maipo", "Colina", "Lampa", "Tiltil", 
        "San Bernardo", "Buin", "Calera de Tango", "Paine", "Melipilla", "Alhué", 
        "Curacaví", "María Pinto", "San Pedro", "Talagante", "El Monte", "Isla de Maipo", 
        "Padre Hurtado", "Peñaflor"
    ].sort();
    
    const comunaDropdownMenu = document.getElementById('comunaDropdownMenu');
    const comunaInput = document.getElementById('comuna');
    const comunaSelectedText = document.getElementById('comunaSelectedText');
    
    comunasRM.forEach(c => {
        let li = document.createElement('li');
        let a = document.createElement('a');
        a.className = 'dropdown-item rounded mb-1 text-white custom-dropdown-item py-2';
        a.href = '#';
        a.innerText = c;
        a.addEventListener('click', (e) => {
            e.preventDefault();
            comunaInput.value = c;
            comunaSelectedText.innerText = c;
            comunaSelectedText.style.color = "white";
        });
        li.appendChild(a);
        comunaDropdownMenu.appendChild(li);
    });

    // Set minimum date to today
    const dateInput = document.getElementById('fecha');
    const today = new Date().toISOString().split('T')[0];
    dateInput.min = today;

    // Time Slot Logic
    const timeSlotsContainer = document.getElementById('timeSlotsContainer');
    const timeSlotsGrid = document.getElementById('timeSlotsGrid');
    const horaInput = document.getElementById('hora');
    
    // Intervalos de 1.5h desde 09:00 a 21:00
    const timeSlots = [
        "09:00", "10:30", "12:00", "13:30", "15:00", 
        "16:30", "18:00", "19:30", "21:00"
    ];

    dateInput.addEventListener('change', function() {
        if (!this.value) {
            timeSlotsContainer.classList.add('d-none');
            return;
        }
        
        timeSlotsContainer.classList.remove('d-none');
        horaInput.value = ''; // Reset selection
        
        timeSlotsGrid.innerHTML = '';
        
        timeSlots.forEach((time) => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'btn btn-outline-brand time-slot-btn fw-bold px-3 py-2';
            btn.innerText = time;
            
            btn.addEventListener('click', () => {
                // Deselect others
                document.querySelectorAll('.time-slot-btn').forEach(b => {
                    b.classList.remove('active', 'bg-brand', 'text-white');
                    b.classList.add('btn-outline-brand');
                    b.style.borderColor = 'var(--brand-color)';
                });
                
                // Select current
                btn.classList.remove('btn-outline-brand');
                btn.classList.add('active', 'bg-brand', 'text-white');
                btn.style.borderColor = 'var(--brand-color)';
                
                horaInput.value = time;
            });
            
            timeSlotsGrid.appendChild(btn);
        });
    });

    // --- STEP LOGIC ---
    const step1 = document.getElementById('step1');
    const step2 = document.getElementById('step2');
    const form1 = document.getElementById('formStep1');
    const form2 = document.getElementById('formStep2');
    
    document.getElementById('btnNext1').addEventListener('click', () => {
        if(form1.checkValidity()) {
            step1.style.display = 'none';
            step2.style.display = 'block';
            window.scrollTo({top: 0, behavior: 'smooth'});
        } else {
            form1.reportValidity();
        }
    });
    
    document.getElementById('btnBack').addEventListener('click', () => {
        step2.style.display = 'none';
        step1.style.display = 'block';
        window.scrollTo({top: 0, behavior: 'smooth'});
    });
    
    // --- VALIDATORS --- 

    // RUT Formatter
    const rutInput = document.getElementById('rut');
    rutInput.addEventListener('input', function(e) {
        let value = this.value.replace(/[^0-9kK]/g, '').toUpperCase();
        if (value.length > 1) {
            value = value.slice(0, -1) + '-' + value.slice(-1);
        }
        if (value.length > 5) {
            value = value.slice(0, -5) + '.' + value.slice(-5);
        }
        if (value.length > 9) {
            value = value.slice(0, -9) + '.' + value.slice(-9);
        }
        this.value = value;
    });

    // Patente Validator
    const patenteInput = document.getElementById('patente');
    patenteInput.addEventListener('input', function() {
        this.value = this.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
        const oldFormat = /^[A-Z]{2}[0-9]{4}$/;
        const newFormat = /^[B-DF-HJ-LP-TV-Z]{4}[0-9]{2}$/;
        
        if (this.value.length === 6) {
            if (oldFormat.test(this.value) || newFormat.test(this.value)) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
                this.setCustomValidity('');
            } else {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
                this.setCustomValidity('Patente inválida');
            }
        } else {
            this.classList.remove('is-valid', 'is-invalid');
            this.setCustomValidity('Patente incompleta');
        }
    });

    // Final Submission
    form2.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!form2.checkValidity()) {
            form2.reportValidity();
            return;
        }

        const submitter = e.submitter;
        const isCash = submitter && submitter.id === 'btnCash';
        const activeBtn = submitter || document.getElementById('submitBtn');
        const originalText = activeBtn.innerHTML;
        
        activeBtn.disabled = true;
        activeBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Procesando...';

        if(isCash) {
            setTimeout(() => {
                Swal.fire({
                    title: '¡Reserva Confirmada!',
                    text: 'Te hemos enviado un correo. El pago se realizará presencialmente el día de la inspección.',
                    icon: 'success',
                    confirmButtonColor: '#10b981',
                    background: '#18181b',
                    color: '#fff'
                }).then(() => {
                    activeBtn.disabled = false;
                    activeBtn.innerHTML = originalText;
                });
            }, 1000);
        } else {
            setTimeout(() => {
                Swal.fire({
                    title: '¡Redirigiendo a Flow!',
                    text: 'Serás llevado al portal de pago seguro.',
                    icon: 'success',
                    confirmButtonColor: '#ff3c00',
                    background: '#18181b',
                    color: '#fff'
                }).then(() => {
                    activeBtn.disabled = false;
                    activeBtn.innerHTML = originalText;
                });
            }, 1500);
        }
    });
});
