// Configuración del Frontend - Portal Inmobiliario
const CONFIG = {
    // URLs de la API
    API_URL: window.location.hostname === 'localhost' 
        ? 'http://localhost:3001/api' 
        : '/api',
    
    // Configuración de la aplicación
    APP_NAME: 'STELLART HOMES',
    APP_VERSION: '1.0.0',
    
    // Configuración del chat
    CHAT: {
        MAX_MESSAGES: 50,
        TYPING_DELAY: 1000,
        AUTO_SCROLL: true
    },
    
    // Configuración de propiedades
    PROPERTIES: {
        ITEMS_PER_PAGE: 12,
        IMAGE_PLACEHOLDER: 'https://via.placeholder.com/400x250/2563eb/ffffff?text=',
        DEFAULT_IMAGE: '/images/property-placeholder.jpg'
    },
    
    // Configuración de animaciones
    ANIMATIONS: {
        FADE_DURATION: 300,
        SLIDE_DURATION: 500,
        BOUNCE_DURATION: 600
    },
    
    // Configuración de breakpoints responsive
    BREAKPOINTS: {
        MOBILE: 768,
        TABLET: 1024,
        DESKTOP: 1200
    },
    
    // Configuración de colores (para uso en JavaScript)
    COLORS: {
        PRIMARY: '#2563eb',
        SECONDARY: '#64748b',
        SUCCESS: '#10b981',
        WARNING: '#f59e0b',
        ERROR: '#ef4444',
        INFO: '#3b82f6'
    },
    
    // Configuración de notificaciones
    NOTIFICATIONS: {
        DURATION: 5000,
        POSITION: 'top-right'
    }
};

// Exportar configuración para uso en otros archivos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
} else {
    window.CONFIG = CONFIG;
}
