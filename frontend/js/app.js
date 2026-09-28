// STELLART HOMES - JavaScript Principal
class StellartHomes {
    constructor() {
        this.apiUrl = window.CONFIG?.API_URL || 'http://localhost:3001/api';
        this.properties = [];
        this.chatMessages = [];
        this.isChatOpen = false;
        this.config = window.CONFIG || {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadProperties();
        this.setupChat();
        this.setupSmoothScrolling();
    }

    setupEventListeners() {
        // Navegación móvil
        const navToggle = document.querySelector('.nav-toggle');
        const navMenu = document.querySelector('.nav-menu');
        
        if (navToggle && navMenu) {
            navToggle.addEventListener('click', () => {
                navMenu.classList.toggle('active');
            });
        }

        // Búsqueda
        const searchBtn = document.querySelector('.search-btn');
        if (searchBtn) {
            searchBtn.addEventListener('click', () => this.searchProperties());
        }

        // Filtros
        const filterSelects = document.querySelectorAll('.filter-select');
        filterSelects.forEach(select => {
            select.addEventListener('change', () => this.searchProperties());
        });

        // Chat
        const chatToggle = document.getElementById('chatToggle');
        const chatClose = document.getElementById('chatClose');
        const chatSend = document.getElementById('chatSend');
        const chatInput = document.getElementById('chatInput');

        if (chatToggle) {
            chatToggle.addEventListener('click', () => this.toggleChat());
        }

        if (chatClose) {
            chatClose.addEventListener('click', () => this.closeChat());
        }

        if (chatSend) {
            chatSend.addEventListener('click', () => this.sendMessage());
        }

        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            });
        }

        // Scroll para header
        window.addEventListener('scroll', () => this.handleScroll());
    }

    setupSmoothScrolling() {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    handleScroll() {
        const header = document.querySelector('.header');
        if (window.scrollY > 100) {
            header.style.background = 'rgba(255, 255, 255, 0.98)';
            header.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
        } else {
            header.style.background = 'rgba(255, 255, 255, 0.95)';
            header.style.boxShadow = 'none';
        }
    }

    async loadProperties() {
        const propertiesGrid = document.getElementById('propertiesGrid');
        const loadingElement = document.getElementById('propertiesLoading');
        
        if (loadingElement) {
            loadingElement.style.display = 'block';
        }

        try {
            console.log('Cargando propiedades desde:', `${this.apiUrl}/properties`);
            
            // Primero probar conexión con el backend
            const testResponse = await fetch(`${this.apiUrl}/test`);
            if (!testResponse.ok) {
                throw new Error(`Backend no responde: ${testResponse.status}`);
            }
            const testData = await testResponse.json();
            console.log('Backend conectado:', testData);

            // Ahora cargar propiedades
            const response = await fetch(`${this.apiUrl}/properties`);
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Datos recibidos:', data);
            
            this.properties = data.properties || [];
            this.renderProperties(this.properties);
        } catch (error) {
            console.error('Error cargando propiedades:', error);
            this.showError(`Error cargando propiedades: ${error.message}`);
            
        } finally {
            if (loadingElement) {
                loadingElement.style.display = 'none';
            }
        }
    }


    async searchProperties() {
        const searchInput = document.getElementById('searchInput');
        const propertyType = document.getElementById('propertyType');
        const minPrice = document.getElementById('minPrice');
        const maxPrice = document.getElementById('maxPrice');
        const bedrooms = document.getElementById('bedrooms');

        const params = new URLSearchParams();
        
        if (searchInput.value) {
            params.append('search', searchInput.value);
        }
        if (propertyType.value) {
            params.append('type', propertyType.value);
        }
        if (minPrice.value) {
            params.append('minPrice', minPrice.value);
        }
        if (maxPrice.value) {
            params.append('maxPrice', maxPrice.value);
        }
        if (bedrooms.value) {
            params.append('bedrooms', bedrooms.value);
        }

        const propertiesGrid = document.getElementById('propertiesGrid');
        const loadingElement = document.getElementById('propertiesLoading');
        
        if (loadingElement) {
            loadingElement.style.display = 'block';
        }

        try {
            const response = await fetch(`${this.apiUrl}/properties?${params.toString()}`);
            const data = await response.json();
            this.properties = data.properties || [];
            this.renderProperties(this.properties);
        } catch (error) {
            console.error('Error buscando propiedades:', error);
            this.showError('Error en la búsqueda. Inténtalo de nuevo.');
        } finally {
            if (loadingElement) {
                loadingElement.style.display = 'none';
            }
        }
    }

    renderProperties(properties) {
        const propertiesGrid = document.getElementById('propertiesGrid');
        if (!propertiesGrid) return;

        if (properties.length === 0) {
            propertiesGrid.innerHTML = `
                <div class="no-properties">
                    <i class="fas fa-search" style="font-size: 3rem; color: var(--text-light); margin-bottom: 1rem;"></i>
                    <h3>No se encontraron propiedades</h3>
                    <p>Intenta ajustar los filtros de búsqueda</p>
                </div>
            `;
            return;
        }

        propertiesGrid.innerHTML = properties.map(property => this.createPropertyCard(property)).join('');
    }

    createPropertyCard(property) {
        const price = this.formatPrice(property.price);
        const features = this.getPropertyFeatures(property);
        
        return `
            <div class="property-card fade-in-up">
                <div class="property-image">
                    <img src="${property.images[0] || this.getPlaceholderImage()}" alt="${property.title}" loading="lazy">
                    <div class="property-badge">${property.type}</div>
                </div>
                <div class="property-content">
                    <h3 class="property-title">${property.title}</h3>
                    <div class="property-location">
                        <i class="fas fa-map-marker-alt"></i>
                        <span>${property.location}</span>
                    </div>
                    <div class="property-features">
                        ${features}
                    </div>
                    <div class="property-price">${price}</div>
                    <div class="property-actions">
                        <button class="btn-primary" onclick="portal.showPropertyDetails(${property.id})">
                            <i class="fas fa-eye"></i>
                            Ver Detalles
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    getPropertyFeatures(property) {
        const features = [];
        
        if (property.bedrooms > 0) {
            features.push(`
                <div class="property-feature">
                    <i class="fas fa-bed"></i>
                    <span>${property.bedrooms} dorm.</span>
                </div>
            `);
        }
        
        if (property.bathrooms > 0) {
            features.push(`
                <div class="property-feature">
                    <i class="fas fa-bath"></i>
                    <span>${property.bathrooms} baños</span>
                </div>
            `);
        }
        
        if (property.area > 0) {
            features.push(`
                <div class="property-feature">
                    <i class="fas fa-ruler-combined"></i>
                    <span>${property.area}m²</span>
                </div>
            `);
        }
        
        return features.join('');
    }

    formatPrice(price) {
        return new Intl.NumberFormat('es-ES', {
            style: 'currency',
            currency: 'EUR',
            minimumFractionDigits: 0,
        }).format(price);
    }

    getPlaceholderImage() {
        return this.config.PROPERTIES?.IMAGE_PLACEHOLDER + encodeURIComponent('Propiedad') || 
               `https://via.placeholder.com/400x250/2563eb/ffffff?text=${encodeURIComponent('Propiedad')}`;
    }

    showPropertyDetails(propertyId) {
        const property = this.properties.find(p => p.id === propertyId);
        if (!property) return;

        // Crear modal de detalles
        const modal = document.createElement('div');
        modal.className = 'property-modal';
        modal.innerHTML = `
            <div class="modal-overlay" onclick="this.parentElement.remove()">
                <div class="modal-content" onclick="event.stopPropagation()">
                    <div class="modal-header">
                        <h2>${property.title}</h2>
                        <button class="modal-close" onclick="this.closest('.property-modal').remove()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        <div class="modal-image">
                            <img src="${property.images && property.images.length > 0 ? property.images[0] : this.getPlaceholderImage()}" alt="${property.title}">
                        </div>
                        <div class="modal-details">
                            <div class="modal-price">${this.formatPrice(property.price)}</div>
                            <div class="modal-location">
                                <i class="fas fa-map-marker-alt"></i>
                                ${property.location}
                            </div>
                            <div class="modal-features">
                                ${this.getPropertyFeatures(property)}
                            </div>
                            <div class="modal-description">
                                <h4>Descripción</h4>
                                <p>${property.description || 'Descripción no disponible.'}</p>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn-secondary" onclick="this.closest('.property-modal').remove()">
                            Cerrar
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Agregar estilos del modal
        if (!document.querySelector('#modal-styles')) {
            const style = document.createElement('style');
            style.id = 'modal-styles';
            style.textContent = `
                .property-modal {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    z-index: 2000;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .modal-overlay {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.8);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 2rem;
                }
                .modal-content {
                    background: white;
                    border-radius: 12px;
                    max-width: 800px;
                    max-height: 90vh;
                    overflow-y: auto;
                    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
                }
                .modal-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 1.5rem;
                    border-bottom: 1px solid var(--border-color);
                }
                .modal-close {
                    background: none;
                    border: none;
                    font-size: 1.5rem;
                    cursor: pointer;
                    color: var(--text-secondary);
                }
                .modal-body {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 2rem;
                    padding: 1.5rem;
                }
                .modal-image img {
                    width: 100%;
                    height: 300px;
                    object-fit: cover;
                    border-radius: 8px;
                }
                .modal-price {
                    font-size: 2rem;
                    font-weight: 700;
                    color: var(--primary-color);
                    margin-bottom: 1rem;
                }
                .modal-location {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    color: var(--text-secondary);
                    margin-bottom: 1rem;
                }
                .modal-features {
                    display: flex;
                    gap: 1rem;
                    margin-bottom: 1rem;
                }
                .modal-description h4 {
                    margin-bottom: 0.5rem;
                    color: var(--text-primary);
                }
                .modal-footer {
                    display: flex;
                    gap: 1rem;
                    padding: 1.5rem;
                    border-top: 1px solid var(--border-color);
                    justify-content: flex-end;
                }
                @media (max-width: 768px) {
                    .modal-body {
                        grid-template-columns: 1fr;
                    }
                }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(modal);
    }


    setupChat() {
        this.chatMessages = [
            {
                id: 1,
                text: '¡Hola! Soy tu asistente inmobiliario. ¿En qué puedo ayudarte hoy?',
                isUser: false,
                timestamp: new Date()
            }
        ];
        this.renderChatMessages();
    }

    toggleChat() {
        const chatContainer = document.getElementById('chatContainer');
        if (!chatContainer) return;

        this.isChatOpen = !this.isChatOpen;
        
        if (this.isChatOpen) {
            chatContainer.classList.add('active');
            document.getElementById('chatInput').focus();
        } else {
            chatContainer.classList.remove('active');
        }
    }

    closeChat() {
        const chatContainer = document.getElementById('chatContainer');
        if (chatContainer) {
            chatContainer.classList.remove('active');
            this.isChatOpen = false;
        }
    }

    openChat() {
        if (!this.isChatOpen) {
            this.toggleChat();
        }
    }

    async sendMessage() {
        const chatInput = document.getElementById('chatInput');
        const message = chatInput.value.trim();
        
        if (!message) return;

        // Agregar mensaje del usuario
        this.addMessage(message, true);
        chatInput.value = '';

        // Mostrar indicador de escritura
        this.showTypingIndicator();

        try {
            const response = await fetch(`${this.apiUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            
            // Remover indicador de escritura
            this.hideTypingIndicator();
            
            // Agregar respuesta del bot
            this.addMessage(data.response || 'Lo siento, no pude procesar tu mensaje.', false);
        } catch (error) {
            console.error('Error enviando mensaje:', error);
            this.hideTypingIndicator();
            this.addMessage('Lo siento, hubo un error al procesar tu mensaje. Inténtalo de nuevo.', false);
        }
    }

    addMessage(text, isUser) {
        const message = {
            id: Date.now(),
            text,
            isUser,
            timestamp: new Date()
        };

        this.chatMessages.push(message);
        this.renderChatMessages();
        this.scrollChatToBottom();
    }

    renderChatMessages() {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;

        chatMessages.innerHTML = this.chatMessages.map(message => this.createMessageElement(message)).join('');
    }

    createMessageElement(message) {
        const timeString = message.timestamp.toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });

        return `
            <div class="message ${message.isUser ? 'user-message' : 'bot-message'}">
                <div class="message-avatar">
                    <i class="fas ${message.isUser ? 'fa-user' : 'fa-robot'}"></i>
                </div>
                <div class="message-content">
                    <p>${message.text}</p>
                    <span class="message-time">${timeString}</span>
                </div>
            </div>
        `;
    }

    showTypingIndicator() {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;

        const typingElement = document.createElement('div');
        typingElement.className = 'message bot-message typing-indicator';
        typingElement.id = 'typing-indicator';
        typingElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;

        // Agregar estilos para los puntos de escritura
        if (!document.querySelector('#typing-styles')) {
            const style = document.createElement('style');
            style.id = 'typing-styles';
            style.textContent = `
                .typing-dots {
                    display: flex;
                    gap: 4px;
                    align-items: center;
                }
                .typing-dots span {
                    width: 8px;
                    height: 8px;
                    background: var(--text-light);
                    border-radius: 50%;
                    animation: typing 1.4s infinite ease-in-out;
                }
                .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
                .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
                @keyframes typing {
                    0%, 80%, 100% { transform: scale(0); }
                    40% { transform: scale(1); }
                }
            `;
            document.head.appendChild(style);
        }

        chatMessages.appendChild(typingElement);
        this.scrollChatToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollChatToBottom() {
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    showError(message) {
        // Crear notificación de error
        const notification = document.createElement('div');
        notification.className = 'error-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-exclamation-circle"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        // Agregar estilos para la notificación
        if (!document.querySelector('#notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                .error-notification {
                    position: fixed;
                    top: 100px;
                    right: 20px;
                    background: var(--error-color);
                    color: white;
                    padding: 1rem;
                    border-radius: 8px;
                    box-shadow: var(--shadow-lg);
                    z-index: 3000;
                    animation: slideIn 0.3s ease-out;
                }
                .notification-content {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }
                .notification-content button {
                    background: none;
                    border: none;
                    color: white;
                    cursor: pointer;
                    margin-left: 0.5rem;
                }
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(notification);

        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
}

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.portal = new StellartHomes();
});

// Funciones globales para uso en HTML
function searchProperties() {
    if (window.portal) {
        window.portal.searchProperties();
    }
}

function showPropertyDetails(propertyId) {
    if (window.portal) {
        window.portal.showPropertyDetails(propertyId);
    }
}


function toggleChat() {
    if (window.portal) {
        window.portal.toggleChat();
    }
}

function sendMessage() {
    if (window.portal) {
        window.portal.sendMessage();
    }
}
