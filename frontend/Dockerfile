FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN pnpm install
COPY . .

RUN pnpm build
EXPOSE 3000

CMD ["npm", "start"]
