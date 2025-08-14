// EchoVerse Pro JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    initMobileNavigation();
    initAnimatedCounters();
    initVoicePreviews();
    initSmoothScrolling();
    initIntersectionObserver();
    initCTAButtons();
});

// Mobile Navigation
function initMobileNavigation() {
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.querySelector('.nav__links');
    
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            navLinks.classList.toggle('nav__links--open');
            navToggle.classList.toggle('nav__toggle--open');
        });
        
        // Close mobile menu when clicking on a link
        const links = navLinks.querySelectorAll('a');
        links.forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('nav__links--open');
                navToggle.classList.remove('nav__toggle--open');
            });
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
                navLinks.classList.remove('nav__links--open');
                navToggle.classList.remove('nav__toggle--open');
            }
        });
    }
}

// Animated Counters
function initAnimatedCounters() {
    const stats = document.querySelectorAll('.stat');
    let hasAnimated = false;
    
    function animateCounters() {
        if (hasAnimated) return;
        
        stats.forEach(stat => {
            const target = parseInt(stat.dataset.target) || parseFloat(stat.dataset.target);
            const numberElement = stat.querySelector('.stat__number');
            const suffix = stat.dataset.target.includes('.') ? '%' : '+';
            
            if (target && numberElement) {
                animateCounter(numberElement, 0, target, 2000, suffix);
            }
        });
        
        hasAnimated = true;
    }
    
    function animateCounter(element, start, end, duration, suffix) {
        const startTime = performance.now();
        const isDecimal = end.toString().includes('.');
        
        function updateCounter(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function for smooth animation
            const easedProgress = 1 - Math.pow(1 - progress, 3);
            const current = start + (end - start) * easedProgress;
            
            if (isDecimal) {
                element.textContent = current.toFixed(1) + suffix;
            } else {
                element.textContent = Math.floor(current).toLocaleString() + suffix;
            }
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            }
        }
        
        requestAnimationFrame(updateCounter);
    }
    
    // Trigger animation when stats section comes into view
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounters();
            }
        });
    }, { threshold: 0.5 });
    
    const heroStats = document.querySelector('.hero__stats');
    if (heroStats) {
        observer.observe(heroStats);
    }
}

// Voice Previews
function initVoicePreviews() {
    const voiceButtons = document.querySelectorAll('.voice-preview');
    
    voiceButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const voiceName = this.dataset.voice;
            playVoicePreview(this, voiceName);
        });
    });
}

function playVoicePreview(button, voiceName) {
    // Remove playing state from all buttons
    document.querySelectorAll('.voice-preview').forEach(btn => {
        btn.classList.remove('playing');
        btn.textContent = 'Preview Voice';
    });
    
    // Add playing state to clicked button
    button.classList.add('playing');
    button.textContent = 'Playing...';
    
    // Simulate voice preview with text feedback
    const sampleTexts = {
        'Lisa': 'Hello, this is Lisa speaking with a clear American accent.',
        'Michael': 'This is Michael, demonstrating a deep authoritative voice.',
        'Allison': 'Hi there! This is Allison with a warm Canadian accent.',
        'David': 'This is David, showcasing a rich resonant male voice.',
        'Emma': 'Hello, I\'m Emma with a versatile and clear voice.',
        'Sarah': 'Good day! This is Sarah with an elegant British accent.'
    };
    
    // Show notification
    showNotification(`Playing ${voiceName}: "${sampleTexts[voiceName] || 'Sample voice preview'}"`, 'info');
    
    // Reset button after 3 seconds
    setTimeout(() => {
        button.classList.remove('playing');
        button.textContent = 'Preview Voice';
    }, 3000);
}

// Smooth Scrolling for Navigation
function initSmoothScrolling() {
    const navLinks = document.querySelectorAll('.nav__links a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const href = this.getAttribute('href');
            const targetId = href.substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const nav = document.querySelector('.nav');
                const navHeight = nav ? nav.offsetHeight : 70;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - navHeight - 20;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
                
                // Close mobile menu if open
                const navLinksContainer = document.querySelector('.nav__links');
                const navToggle = document.getElementById('navToggle');
                if (navLinksContainer && navToggle) {
                    navLinksContainer.classList.remove('nav__links--open');
                    navToggle.classList.remove('nav__toggle--open');
                }
            }
        });
    });
}

// CTA Button Functionality - REPLACE WITH YOUR STREAMLIT APP URL
function initCTAButtons() {
    document.addEventListener('click', function(e) {
        const button = e.target.closest('button, .btn');
        if (!button) return;
        
        const buttonText = button.textContent.trim();
        
        // Handle primary CTA buttons - REPLACE THE URL BELOW
        if (buttonText.includes('Try EchoVerse') || 
            buttonText.includes('Try Now') ||
            buttonText.includes('Get Started') ||
            buttonText.includes('Start Pro Trial')) {
            
            e.preventDefault();
            
            // 🔥 REPLACE THIS URL WITH YOUR ACTUAL STREAMLIT APP URL 🔥
            window.open('http://localhost:8501', '_blank');
            
            // Alternative if deployed online:
            // window.open('https://your-streamlit-app-url.streamlit.app', '_blank');
        }
        
        // Handle Learn More button - scroll to features
        else if (buttonText === 'Learn More') {
            e.preventDefault();
            const featuresSection = document.getElementById('features');
            if (featuresSection) {
                const nav = document.querySelector('.nav');
                const navHeight = nav ? nav.offsetHeight : 70;
                const elementPosition = featuresSection.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - navHeight - 20;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        }
        
        // Handle Contact Sales button
        else if (buttonText === 'Contact Sales') {
            e.preventDefault();
            showNotification('Contact feature coming soon!', 'info');
        }
    });
}

// Intersection Observer for Animations
function initIntersectionObserver() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe elements that should animate in
    const elementsToAnimate = document.querySelectorAll(`
        .feature-card,
        .step,
        .voice-card,
        .pricing-card,
        .testimonial-card
    `);
    
    elementsToAnimate.forEach(el => observer.observe(el));
}

// Notification System
function showNotification(message, type = 'info') {
    // Remove existing notification
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Create new notification
    const notification = document.createElement('div');
    notification.className = `notification notification--${type}`;
    notification.innerHTML = `
        <div class="notification__content">
            <span class="notification__message">${message}</span>
            <button class="notification__close">&times;</button>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        max-width: 400px;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    const content = notification.querySelector('.notification__content');
    content.style.cssText = `
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
    `;
    
    const messageEl = notification.querySelector('.notification__message');
    messageEl.style.cssText = `
        color: #374151;
        font-size: 14px;
        line-height: 1.5;
    `;
    
    const closeBtn = notification.querySelector('.notification__close');
    closeBtn.style.cssText = `
        background: none;
        border: none;
        font-size: 18px;
        cursor: pointer;
        color: #6b7280;
        padding: 0;
        line-height: 1;
    `;
    
    // Type-specific styling
    if (type === 'success') {
        notification.style.borderColor = '#10b981';
        messageEl.style.color = '#10b981';
    } else if (type === 'info') {
        notification.style.borderColor = '#2563eb';
        messageEl.style.color = '#2563eb';
    }
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Close functionality
    closeBtn.addEventListener('click', () => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => notification.remove(), 300);
    });
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }
    }, 4000);
}

// Handle window resize
window.addEventListener('resize', function() {
    const navLinks = document.querySelector('.nav__links');
    const navToggle = document.getElementById('navToggle');
    
    if (window.innerWidth > 768) {
        if (navLinks) navLinks.classList.remove('nav__links--open');
        if (navToggle) navToggle.classList.remove('nav__toggle--open');
    }
});

// Add scroll effect to navigation
window.addEventListener('scroll', function() {
    const nav = document.querySelector('.nav');
    if (nav && window.scrollY > 100) {
        nav.style.background = 'rgba(255, 255, 255, 0.98)';
    } else if (nav) {
        nav.style.background = 'rgba(255, 255, 255, 0.95)';
    }
});
