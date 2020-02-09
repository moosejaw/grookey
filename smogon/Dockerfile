FROM node:13.8-slim
WORKDIR /home/node/app

COPY ./ ./

# Install the stuff in package.json
RUN npm install

USER node
CMD ["node", "app.js"]