FROM node:13.8-slim
WORKDIR /home/node/app

# Install node stuff
RUN npm install zombie
RUN npm install express

USER node
CMD ["node", "app.js"]