FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM node:20-alpine AS runtime

WORKDIR /app
ENV NODE_ENV=production

COPY package*.json ./
RUN npm install

COPY --from=build /app/dist ./dist
COPY --from=build /app/server.ts ./server.ts

EXPOSE 3000

CMD ["npx", "tsx", "server.ts"]

