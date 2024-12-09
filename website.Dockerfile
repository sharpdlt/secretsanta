FROM node:20-alpine AS builder

WORKDIR /app
COPY ./website/package*.json ./
RUN npm ci

COPY ./website .

RUN npm run build

FROM node:20-alpine3.19 as website

WORKDIR /nuxt
COPY --from=builder /app/.output ./.output

EXPOSE 3000

ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

CMD ["node", ".output/server/index.mjs"]