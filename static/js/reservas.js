class Calendar {
    constructor() {
        this.currentDate = new Date();
        this.selectedDate = null;
        this.initializeElements();
        this.initializeCalendar();
    }

    initializeElements() {
        this.calendarEl = document.getElementById('calendar');
        this.currentMonthEl = document.getElementById('currentMonth');
        this.prevMonthBtn = document.getElementById('prevMonth');
        this.nextMonthBtn = document.getElementById('nextMonth');
        this.dayReservationsEl = document.getElementById('dayReservations');

        if (this.prevMonthBtn && this.nextMonthBtn) {
            this.prevMonthBtn.addEventListener('click', () => this.changeMonth(-1));
            this.nextMonthBtn.addEventListener('click', () => this.changeMonth(1));
        }
    }

    initializeCalendar() {
        if (!this.calendarEl) return;
        this.renderCalendar();
    }

    renderCalendar() {
        if (!this.calendarEl || !this.currentMonthEl) return;

        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();

        // Update month display
        const monthName = new Date(year, month).toLocaleString('default', { month: 'long', year: 'numeric' });
        this.currentMonthEl.textContent = monthName;

        // Clear previous calendar
        this.calendarEl.innerHTML = '';

        // Add weekday headers
        const weekdays = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
        weekdays.forEach(day => {
            const dayEl = document.createElement('div');
            dayEl.className = 'calendar-weekday';
            dayEl.textContent = day;
            this.calendarEl.appendChild(dayEl);
        });

        // Get first day of month and total days
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        // Add empty cells for days before first of month
        for (let i = 0; i < firstDay; i++) {
            const emptyDay = document.createElement('div');
            emptyDay.className = 'calendar-day empty';
            this.calendarEl.appendChild(emptyDay);
        }

        // Add days of month
        for (let day = 1; day <= daysInMonth; day++) {
            const dayEl = document.createElement('div');
            dayEl.className = 'calendar-day';
            dayEl.textContent = day;

            // Check if day is today
            const currentDay = new Date();
            if (currentDay.getDate() === day && 
                currentDay.getMonth() === month && 
                currentDay.getFullYear() === year) {
                dayEl.classList.add('today');
            }

            // Check if day is selected
            if (this.selectedDate && 
                this.selectedDate.getDate() === day && 
                this.selectedDate.getMonth() === month && 
                this.selectedDate.getFullYear() === year) {
                dayEl.classList.add('selected');
            }

            dayEl.addEventListener('click', () => this.selectDate(new Date(year, month, day)));
            this.calendarEl.appendChild(dayEl);
        }
    }

    changeMonth(delta) {
        this.currentDate.setMonth(this.currentDate.getMonth() + delta);
        this.renderCalendar();
    }

    selectDate(date) {
        this.selectedDate = date;
        this.renderCalendar();
        
        // Update the date input in the form
        const dateInput = document.getElementById('date');
        if (dateInput && dateInput._flatpickr) {
            dateInput._flatpickr.setDate(date);
        }
    }

    updateReservations(reservations) {
        if (!this.dayReservationsEl) return;

        this.dayReservationsEl.innerHTML = '';
        if (!reservations || reservations.length === 0) {
            this.dayReservationsEl.innerHTML = '<p>Nenhuma reserva para este dia.</p>';
            return;
        }

        const list = document.createElement('ul');
        list.className = 'reservations-list';
        
        reservations.forEach(reservation => {
            const item = document.createElement('li');
            item.className = 'reservation-item';
            item.innerHTML = `
                <div class="reservation-time">${reservation.startTime} - ${reservation.endTime}</div>
                <div class="reservation-details">
                    <div class="reservation-location">${reservation.location}</div>
                    <div class="reservation-description">${reservation.description}</div>
                </div>
                <div class="reservation-status status-${reservation.status.toLowerCase()}">${reservation.status}</div>
            `;
            list.appendChild(item);
        });

        this.dayReservationsEl.appendChild(list);
    }
}

class ReservationForm {
    constructor() {
        this.form = document.getElementById('reservationForm');
        this.baseUrl = 'https://sterling-jolly-sailfish.ngrok-free.app';
        console.log('API Base URL:', this.baseUrl); // Debug log
        this.initializeFlatpickr();
        this.attachEventListeners();
        this.loadUpcomingReservations();
    }

    initializeFlatpickr() {
        if (!this.form) return;

        // Initialize date picker
        const dateInput = this.form.querySelector('#date');
        if (dateInput) {
            flatpickr(dateInput, {
                dateFormat: "Y-m-d",
                minDate: "today",
                disableMobile: true,
                allowInput: false,
                clickOpens: true
            });
        }

        // Initialize time pickers
        const timeConfig = {
            enableTime: true,
            noCalendar: true,
            dateFormat: "H:i",
            time_24hr: true,
            minuteIncrement: 30,
            disableMobile: true,
            allowInput: false,
            clickOpens: true
        };

        const startTimeInput = this.form.querySelector('#startTime');
        const endTimeInput = this.form.querySelector('#endTime');

        if (startTimeInput) {
            flatpickr(startTimeInput, {
                ...timeConfig,
                onChange: (selectedDates, dateStr) => {
                    if (endTimeInput && endTimeInput._flatpickr) {
                        endTimeInput._flatpickr.set('minTime', dateStr);
                    }
                }
            });
        }

        if (endTimeInput) {
            flatpickr(endTimeInput, timeConfig);
        }
    }

    attachEventListeners() {
        if (!this.form) return;

        this.form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (!this.validateForm()) {
                return;
            }

            const formData = new FormData(this.form);
            const reservation = {
                location: formData.get('location'),
                date: formData.get('date'),
                startTime: formData.get('startTime'),
                endTime: formData.get('endTime'),
                description: formData.get('description'),
                email: formData.get('email')
            };

            try {
                const response = await this.submitReservation(reservation);
                this.showSubmissionResult(response);
                if (response.status === 'success') {
                    this.form.reset();
                    this.loadUpcomingReservations(); // Refresh the reservations list
                }
            } catch (error) {
                console.error('Error submitting reservation:', error);
                this.showSubmissionResult({
                    status: 'error',
                    message: error.message || 'Erro ao solicitar reserva. Por favor, tente novamente.'
                });
            }
        });
    }

    validateForm() {
        const requiredFields = ['location', 'date', 'startTime', 'endTime', 'description', 'email'];
        let isValid = true;

        requiredFields.forEach(field => {
            const input = this.form.querySelector(`[name="${field}"]`);
            if (!input.value.trim()) {
                input.classList.add('error');
                isValid = false;
            } else {
                input.classList.remove('error');
            }
        });

        // Validate email format
        const emailInput = this.form.querySelector('[name="email"]');
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (emailInput.value && !emailRegex.test(emailInput.value)) {
            emailInput.classList.add('error');
            alert('Por favor, insira um email válido.');
            isValid = false;
        }

        // Validate time range
        const startTime = this.form.querySelector('[name="startTime"]').value;
        const endTime = this.form.querySelector('[name="endTime"]').value;
        if (startTime && endTime && startTime >= endTime) {
            alert('A hora de início deve ser anterior à hora de término.');
            isValid = false;
        }

        if (!isValid) {
            alert('Por favor, preencha todos os campos obrigatórios corretamente.');
        }

        return isValid;
    }

    async submitReservation(reservation) {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/';
            return;
        }

        const url = `${this.baseUrl}/api/reservations`;
        console.log('Submitting to URL:', url); // Debug log
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'Accept': 'application/json'
                },
                body: JSON.stringify(reservation),
                credentials: 'include',
                redirect: 'follow',
                mode: 'cors'
            });

            console.log('Response status:', response.status); // Debug log
            console.log('Response headers:', [...response.headers]); // Debug log

            const responseData = await response.json();
            console.log('Response data:', responseData); // Debug log

            if (response.status === 401) {
                localStorage.removeItem('token');
                window.location.href = '/';
                throw new Error('Unauthorized');
            }

            return responseData; // Return the response data regardless of status
        } catch (error) {
            console.error('Error submitting reservation:', error);
            throw new Error('Failed to submit reservation. Please check your connection and try again.');
        }
    }

    showSubmissionResult(data) {
        const resultDiv = document.getElementById('submissionResult');
        const titleEl = resultDiv.querySelector('.result-title');
        const messageEl = resultDiv.querySelector('.result-message');
        const conflictingDiv = document.getElementById('conflictingReservations');
        
        console.log('Showing submission result:', data); // Debug log
        
        // Reset previous state
        resultDiv.classList.remove('success', 'error');
        titleEl.classList.remove('success', 'error');
        conflictingDiv.style.display = 'none';
        
        if (data.status === 'success') {
            resultDiv.classList.add('success');
            titleEl.classList.add('success');
            titleEl.textContent = 'Reserva Confirmada';
            messageEl.textContent = 'Sua reserva foi registrada com sucesso!';
        } else {
            resultDiv.classList.add('error');
            titleEl.classList.add('error');
            titleEl.textContent = 'Erro na Reserva';
            
            // Set the error message
            if (data.message) {
                messageEl.textContent = data.message;
            } else {
                messageEl.textContent = 'Erro ao solicitar reserva. Por favor, tente novamente.';
            }
            
            // Handle conflict display
            if (data.conflict) {
                console.log('Displaying conflict:', data.conflict); // Debug log
                this.displayConflictingReservations([data.conflict]);
                conflictingDiv.style.display = 'block';
            }
        }
        
        resultDiv.style.display = 'block';
        resultDiv.scrollIntoView({ behavior: 'smooth' });
    }

    displayConflictingReservations(conflicts) {
        const tbody = document.getElementById('conflictTableBody');
        tbody.innerHTML = '';

        conflicts.forEach(reservation => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${reservation.location || 'N/A'}</td>
                <td>${reservation.date}</td>
                <td>${reservation.startTime} - ${reservation.endTime}</td>
                <td>${reservation.responsible || 'N/A'}</td>
                <td>${reservation.description || 'N/A'}</td>
            `;
            tbody.appendChild(row);
        });
    }

    async loadUpcomingReservations() {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/';
            return;
        }

        const startDate = new Date();
        const endDate = new Date();
        endDate.setDate(endDate.getDate() + 14); // Next 2 weeks

        try {
            const response = await fetch(`${this.baseUrl}/api/reservations/range?start_date=${startDate.toISOString().split('T')[0]}&end_date=${endDate.toISOString().split('T')[0]}`, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'Accept': 'application/json'
                },
                credentials: 'include'
            });

            if (!response.ok) {
                if (response.status === 401) {
                    localStorage.removeItem('token');
                    window.location.href = '/';
                    return;
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (data.status === 'success') {
                this.displayReservations(data.reservations);
            }
        } catch (error) {
            console.error('Error loading reservations:', error);
        }
    }

    displayReservations(reservations) {
        const tbody = document.getElementById('reservationsTableBody');
        tbody.innerHTML = '';

        reservations.forEach(reservation => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${reservation.location || 'N/A'}</td>
                <td>${reservation.date}</td>
                <td>${reservation.startTime} - ${reservation.endTime}</td>
                <td>${reservation.responsible || 'N/A'}</td>
                <td>${reservation.description || 'N/A'}</td>
            `;
            tbody.appendChild(row);
        });

        if (reservations.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="5" class="text-center">Nenhuma reserva encontrada</td>';
            tbody.appendChild(row);
        }
    }
}
