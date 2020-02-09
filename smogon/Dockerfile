FROM node:13.8-slim
USER node
WORKDIR /home/node/app

# Install node stuff
RUN npm install zombie
RUN npm install express

CMD ["node", "app.js"]