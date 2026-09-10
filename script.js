document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    /* ==========================================================================
       NAVIGATION & SCROLL EFFECTS
       ========================================================================== */
    const navbar = document.querySelector('.navbar');
    const scrollProgress = document.getElementById('scroll-progress');
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('section');

    // Scroll progress & navbar scroll state
    window.addEventListener('scroll', () => {
        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrolledPercentage = (scrollTop / docHeight) * 100;

        // Progress bar width
        if (scrollProgress) {
            scrollProgress.style.width = scrolledPercentage + '%';
        }

        // Navbar scrolled class
        if (scrollTop > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        // Active link on scroll highlight
        let currentSectionId = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 120;
            const sectionHeight = section.clientHeight;
            if (scrollTop >= sectionTop && scrollTop < sectionTop + sectionHeight) {
                currentSectionId = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${currentSectionId}`) {
                link.classList.add('active');
            }
        });
    });

    /* ==========================================================================
       MOBILE OVERLAY MENU
       ========================================================================== */
    const hamburgerBtn = document.getElementById('hamburger-btn');
    const mobileMenuOverlay = document.getElementById('mobile-menu-overlay');
    const mobileNavLinks = document.querySelectorAll('.mobile-nav-link');

    const toggleMobileMenu = () => {
        const isOpen = mobileMenuOverlay.classList.contains('open');
        if (isOpen) {
            mobileMenuOverlay.classList.remove('open');
            hamburgerBtn.classList.remove('active');
            document.body.style.overflow = 'auto'; // enable scroll
        } else {
            mobileMenuOverlay.classList.add('open');
            hamburgerBtn.classList.add('active');
            document.body.style.overflow = 'hidden'; // disable scroll
        }
    };

    if (hamburgerBtn && mobileMenuOverlay) {
        hamburgerBtn.addEventListener('click', toggleMobileMenu);
    }

    mobileNavLinks.forEach(link => {
        link.addEventListener('click', () => {
            // Close menu drawer on click
            mobileMenuOverlay.classList.remove('open');
            hamburgerBtn.classList.remove('active');
            document.body.style.overflow = 'auto';
        });
    });

    /* ==========================================================================
       SCROLL REVEAL (INTERSECTION OBSERVER)
       ========================================================================== */
    const revealElements = document.querySelectorAll('.reveal-on-scroll');

    if ('IntersectionObserver' in window) {
        const revealObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    observer.unobserve(entry.target); // Reveal only once
                }
            });
        }, {
            threshold: 0.02,
            rootMargin: '0px 0px 100px 0px'
        });

        revealElements.forEach(el => {
            revealObserver.observe(el);
        });
    } else {
        // Fallback for browsers that don't support IntersectionObserver
        revealElements.forEach(el => el.classList.add('revealed'));
    }

    /* ==========================================================================
       MENU CATEGORIES & SEARCH FILTER
       ========================================================================== */
    const filterButtons = document.querySelectorAll('.filter-btn');
    const menuItems = document.querySelectorAll('.menu-item-card');
    const searchInput = document.getElementById('menu-search-input');

    let activeCategory = 'all';
    let searchQuery = '';

    const filterMenu = () => {
        let shownCount = 0;

        menuItems.forEach(item => {
            const itemCategory = item.getAttribute('data-category');
            const itemName = item.querySelector('.menu-item-name')?.textContent.toLowerCase() || '';
            const itemDesc = item.querySelector('.menu-item-desc')?.textContent.toLowerCase() || '';

            const matchesCategory = activeCategory === 'all' || itemCategory === activeCategory;
            const matchesSearch = itemName.includes(searchQuery) || itemDesc.includes(searchQuery);

            let shouldShow = matchesCategory && matchesSearch;

            // If "All Menu" is active (default landing state), limit to the top 11 items
            if (shouldShow && activeCategory === 'all') {
                if (shownCount >= 11) {
                    shouldShow = false;
                } else {
                    shownCount++;
                }
            }

            // Clear any active timeouts to prevent race conditions when clicking rapidly
            if (item.dataset.timeoutId) {
                clearTimeout(parseInt(item.dataset.timeoutId));
                item.removeAttribute('data-timeout-id');
            }

            if (shouldShow) {
                item.classList.remove('hidden');
                // Quick timeout for smooth visual transition
                const tId = setTimeout(() => {
                    item.style.opacity = '1';
                    item.style.transform = 'translateY(0)';
                }, 50);
                item.dataset.timeoutId = tId;
            } else {
                item.style.opacity = '0';
                item.style.transform = 'translateY(10px)';
                // Delay setting hidden to allow opacity transition to complete
                const tId = setTimeout(() => {
                    item.classList.add('hidden');
                }, 300);
                item.dataset.timeoutId = tId;
            }
        });
    };

    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const isCurrentlyActive = btn.classList.contains('active');

            // Remove active class from all buttons
            filterButtons.forEach(b => b.classList.remove('active'));

            if (isCurrentlyActive) {
                // If clicked an already active button, deselect it and show all items
                activeCategory = 'all';
            } else {
                // Otherwise, activate the clicked button
                btn.classList.add('active');
                activeCategory = btn.getAttribute('data-category');
            }
            filterMenu();
        });
    });

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchQuery = e.target.value.toLowerCase().trim();
            filterMenu();
        });
    }

    // Initialize and display the full menu completely on page load
    filterMenu();

    /* ==========================================================================
       CUSTOM LIGHTBOX GALLERY
       ========================================================================== */
    const galleryItems = document.querySelectorAll('.gallery-item');
    const lightboxModal = document.getElementById('lightbox-modal');
    const lightboxImg = document.getElementById('lightbox-main-img');
    const lightboxClose = document.getElementById('lightbox-close-btn');
    const lightboxPrev = document.getElementById('lightbox-prev-btn');
    const lightboxNext = document.getElementById('lightbox-next-btn');

    let currentImageIndex = 0;
    const imagesData = [];

    // Collect all gallery images sources and captions
    galleryItems.forEach((item, index) => {
        const img = item.querySelector('img');
        const alt = img.getAttribute('alt');
        const src = img.getAttribute('src');
        imagesData.push({ src, alt });

        item.addEventListener('click', () => {
            currentImageIndex = index;
            openLightbox();
        });
    });

    const openLightbox = () => {
        const { src, alt } = imagesData[currentImageIndex];
        lightboxImg.src = src;
        lightboxImg.alt = alt;
        lightboxModal.classList.add('open');
        lightboxModal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden'; // Lock background scroll
    };

    const closeLightbox = () => {
        lightboxModal.classList.remove('open');
        lightboxModal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = 'auto'; // Restore scroll
    };

    const showPrevImage = () => {
        currentImageIndex = (currentImageIndex - 1 + imagesData.length) % imagesData.length;
        updateLightboxContent();
    };

    const showNextImage = () => {
        currentImageIndex = (currentImageIndex + 1) % imagesData.length;
        updateLightboxContent();
    };

    const updateLightboxContent = () => {
        lightboxImg.style.opacity = '0';
        setTimeout(() => {
            const { src, alt } = imagesData[currentImageIndex];
            lightboxImg.src = src;
            lightboxImg.alt = alt;
            lightboxImg.style.opacity = '1';
        }, 150);
    };

    // Event listeners
    if (lightboxClose) lightboxClose.addEventListener('click', closeLightbox);
    if (lightboxPrev) lightboxPrev.addEventListener('click', showPrevImage);
    if (lightboxNext) lightboxNext.addEventListener('click', showNextImage);

    // Close lightbox on click outside the image wrapper
    if (lightboxModal) {
        lightboxModal.addEventListener('click', (e) => {
            if (e.target === lightboxModal) {
                closeLightbox();
            }
        });
    }

    // Keyboard controls for lightbox
    document.addEventListener('keydown', (e) => {
        if (!lightboxModal.classList.contains('open')) return;

        if (e.key === 'Escape') {
            closeLightbox();
        } else if (e.key === 'ArrowLeft') {
            showPrevImage();
        } else if (e.key === 'ArrowRight') {
            showNextImage();
        }
    });

    // Touch gestures for swipe support on mobile devices
    let touchStartX = 0;
    let touchEndX = 0;

    const handleLightboxSwipe = () => {
        const minSwipeDistance = 50; // pixels
        const diffX = touchEndX - touchStartX;
        if (Math.abs(diffX) > minSwipeDistance) {
            if (diffX > 0) {
                showPrevImage(); // Swipe Right -> Prev
            } else {
                showNextImage(); // Swipe Left -> Next
            }
        }
    };

    if (lightboxModal) {
        lightboxModal.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].clientX;
        }, { passive: true });

        lightboxModal.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].clientX;
            handleLightboxSwipe();
        }, { passive: true });
    }

    /* ==========================================================================
       SANCTUARY MAP WIDGET INTEGRATION
       ========================================================================== */
    const CAFE_LAT = 19.0743;
    const CAFE_LNG = 72.8532;
    const mapElement = document.getElementById('footer-map');

    if (mapElement && typeof L !== 'undefined') {
        const map = L.map('footer-map', {
            center: [CAFE_LAT, CAFE_LNG],
            zoom: 15,
            zoomControl: false,
            scrollWheelZoom: false
        });

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        const cafeIcon = L.divIcon({
            className: 'cafe-marker-icon',
            html: '<div class="cafe-marker-dot"></div>',
            iconSize: [20, 20],
            iconAnchor: [10, 10]
        });

        const cafeMarker = L.marker([CAFE_LAT, CAFE_LNG], { icon: cafeIcon }).addTo(map);
        cafeMarker.bindPopup("<b>Cafe Kokomo</b>").openPopup();

        const btnFetch = document.getElementById('btn-fetch-location');
        const detailsContainer = document.getElementById('location-details');
        const valDistance = document.getElementById('val-distance');
        const valTime = document.getElementById('val-time');
        const mapWidget = document.querySelector('.sanctuary-map-widget');
        const btnNav = document.getElementById('btn-start-navigation');

        let userLat = null;
        let userLng = null;

        const calculateDistance = (lat1, lon1, lat2, lon2) => {
            const R = 6371; // Earth radius in km
            const dLat = (lat2 - lat1) * Math.PI / 180;
            const dLon = (lon2 - lon1) * Math.PI / 180;
            const a =
                Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                Math.sin(dLon / 2) * Math.sin(dLon / 2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
            return R * c;
        };

        if (btnFetch) {
            btnFetch.addEventListener('click', () => {
                if (!navigator.geolocation) {
                    alert("Geolocation is not supported by your browser");
                    return;
                }

                btnFetch.textContent = "Fetching Location...";
                btnFetch.classList.add('loading');

                navigator.geolocation.getCurrentPosition((position) => {
                    userLat = position.coords.latitude;
                    userLng = position.coords.longitude;

                    // Calculate distance
                    const distKm = calculateDistance(userLat, userLng, CAFE_LAT, CAFE_LNG);

                    // Estimate driving time in minutes (approx 25 km/h average speed in Mumbai traffic)
                    const avgSpeed = 25;
                    const drivingTimeMins = Math.round((distKm / avgSpeed) * 60);

                    // Update subcard values
                    if (valDistance) valDistance.textContent = `${distKm.toFixed(1)} km`;
                    if (valTime) valTime.textContent = `${drivingTimeMins} mins`;

                    // Update UI state
                    btnFetch.style.display = 'none';
                    if (detailsContainer) detailsContainer.classList.remove('hidden');
                    if (mapWidget) mapWidget.classList.add('fetched');

                    // Add User Marker on map
                    const userIcon = L.divIcon({
                        className: 'user-marker-icon',
                        html: '<div class="user-marker-dot"></div>',
                        iconSize: [20, 20],
                        iconAnchor: [10, 10]
                    });

                    L.marker([userLat, userLng], { icon: userIcon }).addTo(map)
                        .bindPopup("<b>Your Location</b>").openPopup();

                    // Draw routing route line
                    L.polyline([[userLat, userLng], [CAFE_LAT, CAFE_LNG]], {
                        color: '#2ba45e',
                        weight: 3,
                        dashArray: '5, 10'
                    }).addTo(map);

                    // Refit bounds
                    const bounds = L.latLngBounds([[userLat, userLng], [CAFE_LAT, CAFE_LNG]]);
                    map.fitBounds(bounds, { padding: [50, 50] });

                }, (error) => {
                    console.error("Error getting location: ", error);
                    btnFetch.textContent = "Fetch My Location";
                    btnFetch.classList.remove('loading');
                    alert("Could not retrieve your location. Please ensure location services are enabled.");
                });
            });
        }

        if (btnNav) {
            btnNav.addEventListener('click', () => {
                const address = "4, Pratap, Cafe Kokomo, CHS LTD, Shivaji Road, near Vakola Bridge, Pratiksha Nagar, Vakola, Santacruz East, Mumbai, Maharashtra 400055";
                const destination = encodeURIComponent(address);
                if (userLat && userLng) {
                    window.open(`https://www.google.com/maps/dir/?api=1&origin=${userLat},${userLng}&destination=${destination}&travelmode=driving`, '_blank');
                } else {
                    window.open(`https://www.google.com/maps/dir/?api=1&destination=${destination}&travelmode=driving`, '_blank');
                }
            });
        }
    }

    /* ==========================================================================
       WHATSAPP RESERVATION FORM MODAL
       ========================================================================== */
    const waModal = document.getElementById('wa-reservation-modal');
    const waOpenTriggers = document.querySelectorAll('#whatsapp-floating-btn, [data-open-reservation]');
    const waCloseBtn = document.getElementById('wa-reservation-modal-close-btn');
    const waOverlay = document.getElementById('wa-reservation-modal-overlay');
    const waForm = document.getElementById('wa-reservation-form');

    // Default desired date to tomorrow's date
    const dateInput = document.getElementById('wa-reserve-date');
    if (dateInput) {
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);

        const year = tomorrow.getFullYear();
        const month = String(tomorrow.getMonth() + 1).padStart(2, '0');
        const day = String(tomorrow.getDate()).padStart(2, '0');

        dateInput.value = `${year}-${month}-${day}`;

        // Set min date to today
        const minYear = today.getFullYear();
        const minMonth = String(today.getMonth() + 1).padStart(2, '0');
        const minDay = String(today.getDate()).padStart(2, '0');
        dateInput.min = `${minYear}-${minMonth}-${minDay}`;
    }

    const openWaModal = () => {
        if (waModal) {
            waModal.classList.add('open');
            waModal.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden'; // Lock background scroll
        }
    };

    const closeWaModal = () => {
        if (waModal) {
            waModal.classList.remove('open');
            waModal.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = 'auto'; // Restore scroll
        }
    };

    waOpenTriggers.forEach((btn) => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            openWaModal();
        });
    });

    if (waCloseBtn) waCloseBtn.addEventListener('click', closeWaModal);
    if (waOverlay) waOverlay.addEventListener('click', closeWaModal);

    // Close on escape key
    document.addEventListener('keydown', (e) => {
        if (waModal && waModal.classList.contains('open') && e.key === 'Escape') {
            closeWaModal();
        }
    });

    // Helper: format YYYY-MM-DD date to "1 May 2026"
    const formatDateString = (dateStr) => {
        if (!dateStr) return '';
        const parts = dateStr.split('-');
        if (parts.length !== 3) return dateStr;

        const year = parts[0];
        const monthIdx = parseInt(parts[1], 10) - 1;
        const day = parseInt(parts[2], 10);

        const months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ];
        const monthName = months[monthIdx] || '';
        return `${day} ${monthName} ${year}`;
    };

    // Helper: format Guest option to "2 seating"
    const formatGuests = (optionVal) => {
        // e.g. "2 Guests (Intimate)" -> match digits or fallback
        const match = optionVal.match(/^(\d+|\d+\+)/);
        if (match) {
            return `${match[1]} seating`;
        }
        return optionVal; // fallback
    };

    // Handle Form Submit
    if (waForm) {
        waForm.addEventListener('submit', (e) => {
            e.preventDefault();

            const name = document.getElementById('wa-reserve-name').value.trim();
            const rawGuests = document.getElementById('wa-reserve-guests').value;
            const rawDate = document.getElementById('wa-reserve-date').value;
            const time = document.getElementById('wa-reserve-time').value;
            const rawRequests = document.getElementById('wa-reserve-requests').value.trim();

            const guestsFormatted = formatGuests(rawGuests);
            const dateFormatted = formatDateString(rawDate);
            const requestsFormatted = rawRequests ? `"${rawRequests}"` : '"none"';

            // Format message exactly as required:
            // "Hello Cafe Kokomo. Concierge, I would like to request an exclusive reservation under your tropical canopy: • Name: aryan • Guests: 2 seating • Date: 1 May 2026 • Time: 11:00 AM • Special Curation Requests: "none" Thank you, please confirm availability."
            const message = `Hello Cafe Kokomo. I would like to request an exclusive reservation under your tropical canopy: • Name: ${name} • Guests: ${guestsFormatted} • Date: ${dateFormatted} • Time: ${time} • Special Curation Requests: ${requestsFormatted} Thank you, please confirm availability.`;

            const phone = "918591515657";
            const encodedMsg = encodeURIComponent(message);
            const whatsappUrl = `https://wa.me/${phone}?text=${encodedMsg}`;

            // Close the modal
            closeWaModal();

            // Redirect in a new tab
            window.open(whatsappUrl, '_blank');
        });
    }

    /* ==========================================================================
       ORDER ONLINE FORM MODAL
       ========================================================================== */
    const orderModal = document.getElementById('order-online-modal');
    const orderOpenBtn = document.getElementById('order-online-btn');
    const orderCloseBtn = document.getElementById('order-online-modal-close-btn');
    const orderOverlay = document.getElementById('order-online-modal-overlay');

    const openOrderModal = () => {
        if (orderModal) {
            orderModal.classList.add('open');
            orderModal.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden'; // Lock background scroll
        }
    };

    const closeOrderModal = () => {
        if (orderModal) {
            orderModal.classList.remove('open');
            orderModal.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = 'auto'; // Restore scroll
        }
    };

    if (orderOpenBtn) {
        orderOpenBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openOrderModal();
        });
    }

    if (orderCloseBtn) orderCloseBtn.addEventListener('click', closeOrderModal);
    if (orderOverlay) orderOverlay.addEventListener('click', closeOrderModal);

    // Close on escape key
    document.addEventListener('keydown', (e) => {
        if (orderModal && orderModal.classList.contains('open') && e.key === 'Escape') {
            closeOrderModal();
        }
    });

    // Close modal when clicking any option card (so it opens in new tab and closes popup)
    const orderCards = document.querySelectorAll('.order-option-card');
    orderCards.forEach(card => {
        card.addEventListener('click', () => {
            closeOrderModal();
        });
    });
});
