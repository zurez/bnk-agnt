FROM node:20-alpine
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

COPY package.json pnpm-lock.yaml ./

RUN pnpm install --frozen-lockfile

COPY . .

EXPOSE 3000

# Due to thread streaming bug running it in dev mode ., 
CMD ["pnpm", "dev"]