const config = {
    API_URL: process.env.NODE_ENV === 'production'
        ? "http://34.70.213.118:8000"
        : "http://localhost:8000",
    
    IMAGE_URL: process.env.NODE_ENV === 'production'
        ? "http://34.70.213.118:80"
        : "http://localhost:8000",
};

export default config;
