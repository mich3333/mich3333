# Frontend Dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Expose port
EXPOSE 5173

# Set environment variables
ENV VITE_SERVER_URL=http://localhost:5000

# Run development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
