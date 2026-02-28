document.addEventListener('DOMContentLoaded', () => {
    // Mobile Menu Toggle
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    hamburger.addEventListener('click', () => {
        navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
        hamburger.classList.toggle('active');
    });

    // Scroll Reveal Animation
    const sections = document.querySelectorAll('section');
    const options = {
        threshold: 0.1,
        rootMargin: "0px"
    };

    const appearOnScroll = new IntersectionObserver(function(entries, observer) {
        entries.forEach(entry => {
            if (!entry.isIntersecting) {
                return;
            } else {
                entry.target.classList.add('visible');
                // Animate children
                const cards = entry.target.querySelectorAll('.card');
                cards.forEach((card, index) => {
                    card.style.animation = `fadeInUp 0.6s ease forwards ${index * 0.1}s`;
                    card.style.opacity = '0'; // Initial state for animation
                });
                observer.unobserve(entry.target);
            }
        });
    }, options);

    sections.forEach(section => {
        appearOnScroll.observe(section);
    });

    // Smooth Scrolling for Anchors
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetContent = document.querySelector(targetId);
            
            if (targetContent) {
                 window.scrollTo({
                    top: targetContent.offsetTop - 100, // Offset for fixed nav
                    behavior: 'smooth'
                });
                
                // Close mobile menu if open
                if (window.innerWidth <= 768) {
                    navLinks.style.display = 'none';
                }
            }
        });
    });
});
