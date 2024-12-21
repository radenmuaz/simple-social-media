const config = {
    API_URL: process.env.NODE_ENV === 'production'
        ? "http://35.184.43.116:8000"
        : "http://localhost:8000",
    
    IMAGE_URL: process.env.NODE_ENV === 'production'
        ? "http://35.184.43.116:80"
        : "http://localhost:8000",
};

export default config;
