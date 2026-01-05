document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-input');
    const analyzeBtn = document.getElementById('analyze-btn');
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const resultsContainer = document.getElementById('results-container');
    const uploadSection = document.getElementById('upload-section');

    let currentSlide = 0;
    let slides = [];

    analyzeBtn.addEventListener('click', async () => {
        const file = fileInput.files[0];
        if (!file) {
            error.textContent = "Please select a file first.";
            error.classList.remove('hidden');
            return;
        }

        error.classList.add('hidden');
        loading.classList.remove('hidden');
        analyzeBtn.disabled = true;

        const reader = new FileReader();
        reader.onload = async (e) => {
            const jsonContent = e.target.result;
            try {
                // Validate JSON first
                const data = JSON.parse(jsonContent);
                
                // Send to backend
                const response = await fetch('/.netlify/functions/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    throw new Error(`Server error: ${response.statusText}`);
                }

                const results = await response.json();
                renderResults(results);
            } catch (err) {
                error.textContent = "Error processing file: " + err.message;
                error.classList.remove('hidden');
            } finally {
                loading.classList.add('hidden');
                analyzeBtn.disabled = false;
            }
        };
        reader.readAsText(file);
    });

    function renderResults(data) {
        // Clear previous results
        resultsContainer.innerHTML = '';
        
        // Helper to create slide
        const createSlide = (htmlContent, bgClass) => {
            const slide = document.createElement('section');
            slide.className = 'slide';
            slide.innerHTML = `<div class="content">${htmlContent}</div><div class="nav-hint">Scroll / Arrow Keys</div>`;
            return slide;
        };

        const slideData = [];

        // Slide 1: Welcome / Total Messages
        slideData.push(`
            <h2>You've been chatty!</h2>
            <p>Total messages analyzed</p>
            <div class="stat-big">${data.total_messages.toLocaleString()}</div>
        `);

        // Slide 2: Top Senders (Pie Chart)
        if (data.charts && data.charts.sender_pie) {
            slideData.push(`
                <h2>Who talks the most?</h2>
                <div class="chart-container">
                    <img src="data:image/png;base64,${data.charts.sender_pie}" class="chart-img" alt="Sender Distribution">
                </div>
            `);
        }

        // Slide 3: Hourly Activity (Bar Chart)
        if (data.charts && data.charts.hourly_bar) {
            slideData.push(`
                <h2>Your Peak Hours</h2>
                <p>When you are most active</p>
                <div class="chart-container">
                    <img src="data:image/png;base64,${data.charts.hourly_bar}" class="chart-img" alt="Hourly Activity">
                </div>
            `);
        }

        // Slide 3.5: Daily Activity (Line Chart)
        if (data.charts && data.charts.daily_line) {
            slideData.push(`
                <h2>Chat History</h2>
                <p>Messages over time</p>
                <div class="chart-container">
                    <img src="data:image/png;base64,${data.charts.daily_line}" class="chart-img" alt="Daily Activity">
                </div>
            `);
        }

        // Slide 3.6: Heatmap
        if (data.charts && data.charts.heatmap) {
            slideData.push(`
                <h2>Weekly Routine</h2>
                <p>Day vs Hour Intensity</p>
                <div class="chart-container">
                    <img src="data:image/png;base64,${data.charts.heatmap}" class="chart-img" alt="Weekly Heatmap">
                </div>
            `);
        }

        // Slide 3.8: Avg Length
        if (data.charts && data.charts.avg_len_bar) {
            slideData.push(`
                <h2>Long Winded?</h2>
                <p>Average characters per message</p>
                <div class="chart-container">
                    <img src="data:image/png;base64,${data.charts.avg_len_bar}" class="chart-img" alt="Avg Message Length">
                </div>
            `);
        }

        // Slide 4: Fun Facts
        let factsHtml = '<h2>Did you know?</h2>';
        if (data.top_sender) {
            factsHtml += `<p><strong>${data.top_sender}</strong> sent the most messages.</p>`;
        }
        if (data.busiest_day) {
            factsHtml += `<p>Your busiest day was <strong>${data.busiest_day}</strong>.</p>`;
        }
        slideData.push(factsHtml);

        // Add slides to DOM
        slideData.forEach((content, index) => {
            const slide = createSlide(content);
            // Assign random gradient class or just let CSS nth-child handle it
            resultsContainer.appendChild(slide);
        });

        // Initialize slides logic
        slides = document.querySelectorAll('.slide');
        currentSlide = 0;
        
        // Hide upload section
        uploadSection.classList.remove('active');
        // Show first result slide
        slides[0].classList.add('active'); // Actually index 0 is upload section in DOM? 
        // No, upload-section is separate. 
        // We need to manage all slides including results.
        // Let's combine them for navigation or just switch context.
        
        // Better: Upload section fades out, results fade in.
        // Re-query slides to include results only
        slides = document.querySelectorAll('#results-container .slide');
        
        setupNavigation();
    }

    function setupNavigation() {
        document.addEventListener('keydown', (e) => {
            if (slides.length === 0) return;
            
            if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') {
                nextSlide();
            } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
                prevSlide();
            }
        });

        document.addEventListener('wheel', (e) => {
            if (slides.length === 0) return;
            if (e.deltaY > 0) nextSlide();
            else prevSlide();
        });
        
        // Touch support for mobile
        let touchStartY = 0;
        document.addEventListener('touchstart', e => touchStartY = e.touches[0].clientY);
        document.addEventListener('touchend', e => {
            const touchEndY = e.changedTouches[0].clientY;
            if (touchStartY - touchEndY > 50) nextSlide();
            if (touchEndY - touchStartY > 50) prevSlide();
        });
    }

    function nextSlide() {
        if (currentSlide < slides.length - 1) {
            slides[currentSlide].classList.remove('active');
            currentSlide++;
            slides[currentSlide].classList.add('active');
        }
    }

    function prevSlide() {
        if (currentSlide > 0) {
            slides[currentSlide].classList.remove('active');
            currentSlide--;
            slides[currentSlide].classList.add('active');
        }
    }
});
