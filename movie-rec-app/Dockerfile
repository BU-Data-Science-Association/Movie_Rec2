# Node/React Dockerfile (lives in movie-rec-app/)
FROM node:20-slim

# Set workdir
WORKDIR /app


# Clean up node_modules and lock file, then install dependencies
COPY package*.json ./
RUN rm -rf node_modules package-lock.json && npm install

# Copy rest of the app
COPY . .

# Expose React port
EXPOSE 3000

# Start React app
CMD ["npm", "start"]
