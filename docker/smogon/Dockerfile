FROM node:lts-alpine

WORKDIR /home/node/app
COPY src/ ./
RUN npm install

USER node
CMD ["node", "app.js"]