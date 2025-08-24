FROM node:20-alpine

WORKDIR /app

# Copiem doar package*.json ca sa folosim layer cache
COPY package.json package-lock.json* ./
# In lipsa unui package-lock.json, npm va instala si va genera unul
RUN npm install --no-fund --no-audit

# Apoi copiem sursa
COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
