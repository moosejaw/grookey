FROM node:current-slim

WORKDIR /home/node/app
COPY src/ ./
RUN npm install

USER node
CMD ["node", "app.js"]